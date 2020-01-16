import base64
import time
import requests
import json
import time
import os
import sys
import hashlib
import requests
from PIL import Image
sys.path.append('./SDK')
import OpenCV_Check
import Share_Line
from SDK.Tencent_Cloud_iai import Tencent_Cloud_iai
from SDK.Tencent_Cloud_tiia import Tencent_Cloud_tiia
from SDK.Douyin_XML import Douyin_XML

def ReStart():
    #关闭
    os.system("adb shell am force-stop com.ss.android.ugc.aweme")
    #重新打开
    os.system("adb shell am start com.ss.android.ugc.aweme/com.ss.android.ugc.aweme.splash.SplashActivity")

    '''
    #检查缓存目录，有没有多的，有就清除掉
    os.system('adb shell  find /sdcard/dcim/camera -name "*.mp4" > ooxx.txt')
    #检查保存是否成功
    with open("ooxx.txt", 'r') as file:
        data = file.read()
        
    #清除缓存的视频文件
    file = data.split('\n')
    for i in file:
        print("rm : " + i)
        os.system('adb shell rm -f ' + i)
    '''
    #等待10秒
    time.sleep(10)

def Check_Video():
    ooxx = tc_iai.DetectFace("G:/douyin/png/1-out.png")
    if ooxx["ret"] == 0:
        return ooxx
    if ooxx["Gender"] > 30 or ooxx["Age"] > 40 or ooxx["Beauty"] < 80:
        return {"ret" : 0}

    xxoo = tc_tiia.ImageModeration("g:/douyin/png/2-out.png")
    if xxoo["ret"] == 200:
        if xxoo["Suggestion"] != "PASS":
            print('点个小心心')
            os.system("adb shell input tap 1000 1300")
            time.sleep(1)
        ooxx["Suggestion"] = xxoo["Suggestion"]
        ooxx["Confidence"] = xxoo["Confidence"]
        ooxx["Type"] = xxoo["Type"]
        return ooxx

    return {"ret" : 0}

'''
海外抖音通过保存视频按钮，将视频保存到手机中，然后取出的方法.如果视频拒绝下载，就无法抓取
'''
def SaveVideo(video_type):
    print('点击分享')
    os.system("adb shell input tap 960 1600")
    time.sleep(1)
    print('检查是否可以保存')
    os.system("adb shell /system/bin/screencap -p /sdcard/screenshot.png")
    os.system("adb pull /sdcard/screenshot.png g:/douyin/png/check_savevideo.png")
    OpenCV_Check.resize_image("g:/douyin/png/check_savevideo.png")
    OpenCV_Check.CaiJian('g:/douyin/png/check_savevideo-out.png','G:/douyin/png/test.png')
    ret = OpenCV_Check.Check_SaveVideo_v1('G:/douyin/png/test.png', 'G:/douyin/png/savebutton.png')
    if ret == None:
        print('判断无法保存， 就下一部')
        return True
    #点击保存
    print('可以保存')
    os.system("adb shell input tap 450 1800")

    #循环5次，判断保存是否成功
    cishu = 0
    while True:
        time.sleep(10)
        cishu = cishu + 1
        print('第', cishu, " / 5 判断保存是否成功")
        os.system('adb shell  find /sdcard/dcim/camera -name "*.mp4" > ooxx.txt')
        #检查保存是否成功
        with open("ooxx.txt", 'r') as file:
            data = file.read()

        data = data.replace('\n', '')
        print(data)
        if len(data) > 5:
            os.system("adb shell input keyevent 4")
            os.remove("ooxx.txt")
            if video_type == 1:
                os.system('adb pull ' + data + ' g:/douyin/save_video/DetectFace')
            else:
                os.system('adb pull ' + data + ' g:/douyin/save_video/ImageModeration')
            os.system('adb shell rm -f ' + data)
            print('保存成功')
            return True
        
    print('保存失败')
    return False


xml = Douyin_XML()
tc_tiia = Tencent_Cloud_tiia()
tc_iai = Tencent_Cloud_iai()

# 重启
ReStart()

while True:
    print('=============================================================')
    loop = int(time.time())

    #获取视频相关信息
    xml.Run()

    if len(xml.nickname) == 0:
        ReStart()
        continue

    if xml.touxiang["x"] == 0:
        print("这是直播,PASS")
        os.system("adb shell input swipe 100 800 200 200 300")
        continue

    if xml.GuangGao == True:
        print("这是广告")
        os.system("adb shell input swipe 100 800 200 200 300")
        continue

    #2连截图
    time.sleep(5)
    os.system("adb shell /system/bin/screencap -p /sdcard/screenshot.png")
    os.system("adb pull /sdcard/screenshot.png g:/douyin/png/1.png")
    OpenCV_Check.resize_image("G:/douyin/png/1.png")
    time.sleep(2)
    os.system("adb shell /system/bin/screencap -p /sdcard/screenshot.png")
    os.system("adb pull /sdcard/screenshot.png g:/douyin/png/2.png")
    OpenCV_Check.resize_image("G:/douyin/png/2.png")

    #检测视频是否需要
    videoinfo = Check_Video()
    if videoinfo["ret"] == 0:
        os.system("adb shell input swipe 100 800 200 200 300")
        continue

    #获取用户信息
    ooxx = Share_Line.Run(xml)
    if ooxx["ret"] == 0:
        ReStart()
        continue

    #获取视频下载信息
    xxoo = Share_Line.GetVideoLine(xml)
    if xxoo["ret"] == 0:
        ReStart()
        continue

    begin = xxoo["videourl2"].find("=")
    begin = begin + 1
    end = xxoo["videourl2"].find("&line=0", begin)
    vid = xxoo["videourl2"][begin:end]

    #合并信息
    data = { "userinfo" : {
                "shareurl" : ooxx["shareurl"],
                "head_img" : ooxx["head_img"],
                "nickname" : ooxx["nickname"],
                "UID" : ooxx["UID"],
                "douyin_id" : ooxx["douyin_id"],
                "guanzhu" : ooxx["guanzhu"],
                "fensi" : ooxx["fensi"],
                "dianzan" : ooxx["dianzan"],
                "zuopin" : ooxx["zuopin"],
                "xihuan" : ooxx["xihuan"]
            },
            "videoinfo" : {
                'nickname' : xml.nickname,
                'about' : xml.about,
                'xin' : xml.xin,
                'pinlun' : xml.pinlun,
                'zhuanfa' : xml.zhuanfa,
                "videourl1" : xxoo["videourl1"],
                "videourl2" : xxoo["videourl2"],
                "Age" : videoinfo["Age"],
                "Beauty" : videoinfo["Beauty"],
                "Gender" : videoinfo["Gender"],
                "Suggestion" : videoinfo["Suggestion"],
                "Confidence" : videoinfo["Confidence"],
                "Type" : videoinfo["Type"],
                "vid" : vid
            }
    }

    print('昵称: ', xml.nickname)
    print('介绍: ', xml.about)
    print('点赞: ', xml.xin)
    print('评论: ', xml.pinlun)
    print('转发: ', xml.zhuanfa)
    print('视频转发地址: ', xxoo["videourl1"])
    print('下载地址: ', xxoo["videourl2"])
    print('年龄: ', videoinfo["Age"])
    print('魅力: ', videoinfo["Beauty"])
    print('性别: ', videoinfo["Gender"])
    print('审核: ', videoinfo["Suggestion"])
    print('算法结果: ', videoinfo["Confidence"])
    print('结果: ', videoinfo["Type"])
    print('视频ID: ', vid)

    print("分享链接 : ", ooxx["shareurl"])
    print("头像 : ", ooxx["head_img"])
    print("昵称 : ", ooxx["nickname"])
    print("抖音ID : ", ooxx["UID"])
    print("关注 : ", ooxx["guanzhu"])
    print("粉丝 : ", ooxx["fensi"])
    print("点赞 : ", ooxx["dianzan"])
    print("作品 : ", ooxx["zuopin"])
    print("喜欢 : ", ooxx["xihuan"])
    
    savePath = "G://douyin//save_video//" + ooxx["UID"]
    if not os.path.exists(savePath):
        os.makedirs(savePath)

    #视频主信息
    with open(savePath + "//userinfo.txt", 'w',encoding='utf-8') as file:
        file.write(json.dumps(data["userinfo"], ensure_ascii=False,sort_keys=True, indent=4))

    #视频信息
    with open(savePath + "//" + vid + ".txt", 'w',encoding='utf-8') as file:
        file.write(json.dumps(data["videoinfo"], ensure_ascii=False,sort_keys=True, indent=4))

    #开始下载
    cmd = 'IDMan /d "' +xxoo["videourl2"] + '"  /p "' + savePath + '" /f "' + vid + '.mp4" /n'
    print(cmd)
    os.system(cmd)

    '''
    #保存视频，如果失败，就重启
    if SaveVideo(video_type) == False:
        ReStart()
        print("本次耗时 ", int(time.time()) - loop, " 秒")
        continue
    '''

    #下一个
    time.sleep(1)
    os.system('adb shell input swipe 100 800 200 200 300')
    print("本次耗时 ", int(time.time()) - loop, " 秒")
        