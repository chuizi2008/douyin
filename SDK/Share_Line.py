# -*- coding: utf-8 -*-
# @Time    : 2019/7/24 12:03
import re
import json
import time
import os
import requests
from lxml import etree
from fontTools.ttLib import TTFont
# 从本地读取字体文件
ttfond = TTFont("./SDK/iconfont_9eb9a50.woff")

def get_cmap_dict():
    """
    :return: 关系映射表
    """
    # 从本地读取关系映射表【从网站下载的woff字体文件】
    best_cmap = ttfond["cmap"].getBestCmap()
    # 循环关系映射表将数字替换成16进制
    best_cmap_dict = {}
    for key,value in best_cmap.items():
        best_cmap_dict[hex(key)] = value
    return best_cmap_dict   # 'num_1', '0xe604': 'num_2', '0xe605': 'num_3'

def get_num_cmap():
    """
    :return: 返回num和真正的数字映射关系
    """
    num_map = {
        "x":"", "num_":1, "num_1":0,
        "num_2":3, "num_3":2, "num_4":4,
        "num_5":5, "num_6":6, "num_7":9,
        "num_8":7, "num_9":8,
    }
    return num_map


def map_cmap_num(get_cmap_dict,get_num_cmap):
    new_cmap = {}
    for key,value in get_cmap_dict().items():
        key = re.sub("0","&#",key,count=1) + ";"    # 源代码中的格式 &#xe606;
        new_cmap[key] = get_num_cmap()[value]
        # 替换后的格式
        # '&#xe602;': 1, '&#xe603;': 0, '&#xe604;': 3, '&#xe605;': 2,
    return new_cmap


# 获取网页源码
def get_html(url):
    headers = {
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
    }
    response = requests.get(url,headers=headers).text
    return response

def replace_num_and_cmap(result,response):
    """
    将网页源代码中的&#xe603;替换成数字
    :param result:
    :param response:
    :return:
    """
    for key,value in result.items():
        if key in response:
            # print(777)
            response = re.sub(key, str(value), response)
    return response

#获取视频地址
def GetVideoLine(xml):
    os.system("adb shell input keyevent 4")
    print('点击分享')
    os.system("adb shell input tap " + str(xml.fenxiang["x"]) + " " + str(xml.fenxiang["y"]))
    time.sleep(1)
    print('滑动屏幕')
    os.system('adb shell input swipe 500 1750 100 1750 300')
    print('点击复制链接')
    os.system('adb shell input tap 585 1730')
    #获取剪贴板的链接
    os.system("adb shell am broadcast -a clipper.get > ooxx.txt")
    #检查保存是否成功
    with open("./ooxx.txt", 'r', encoding='UTF-8') as file:
        data = file.read()
    print(data)
    #清空剪贴板
    os.system('adb shell am broadcast -a clipper.set -e text ""')
    #返回到主页面去
    os.system("adb shell input keyevent 4")
    begin = data.find("https://v.")
    end = data.find("复制此链接")
    if end <= begin:
        print("获取失败，可能出于异常状态，直接PASS.")
        return {"ret" : 0}
    url1 = data[begin:end]
    print("分享链接_1 : ", url1)

    #获取页面内容
    response = get_html(url1)
    begin = response.find("https://aweme")
    end = response.find('",', begin)
    if end <= begin:
        print("获取失败，可能出于异常状态，直接PASS..")
        return {"ret" : 0}
    url2 = response[begin:end]
    print("分享链接_2 : ", url2)
    return {
        "ret" : 200,
        "videourl1" : url1,
        "videourl2" : url2
        }

def manage(url, response):
    res = etree.HTML(response)
    head_img = res.xpath('//*[@id="pagelet-user-info"]/div[2]/div[1]/span[1]/img')[0].attrib
    head_img = head_img["src"]
    douyin_name = res.xpath('//p[@class="nickname"]//text()')[0]
    douyin_id1 = ''.join(res.xpath('//*[@id="pagelet-user-info"]/div[2]/div[1]/p[2]')[0].text).replace(' ','')
    douyin_id1 = douyin_id1.replace("抖音ID：", "")
    douyin_id2 = ''.join(res.xpath('//p[@class="shortid"]/i//text()')).replace(' ','')
    douyin_id = douyin_id1 + douyin_id2
    guanzhu_num = ''.join(res.xpath('//span[@class="focus block"]//text()')).replace(' ','')
    guanzhu_num = guanzhu_num.replace('关注', '')
    fensi_num = ''.join(res.xpath('//span[@class="follower block"]//text()')).replace(' ','')
    fensi_num = fensi_num.replace('粉丝', '')
    dianzan = ''.join(res.xpath('//span[@class="liked-num block"]//text()')).replace(' ','')
    dianzan = dianzan.replace('赞', '')
    zuopin = ''.join(res.xpath('//*[@id="pagelet-user-info"]/div[3]/div/div[1]//text()')).replace(' ','').replace("作品", "")
    xihuan = ''.join(res.xpath('//*[@id="pagelet-user-info"]/div[3]/div/div[2]//text()')).replace(' ','').replace("喜欢", "")
    key = 'uid: "'
    begin = response.find(key)
    end = response.find('",', begin)
    uid = response[begin + len(key):end]
    return {
        "ret" : 200,
        "shareurl" : url,
        "UID" : uid,
        "head_img" : head_img,
        "nickname" : douyin_name,
        "douyin_id" : douyin_id,
        "guanzhu" : guanzhu_num,
        "fensi" : fensi_num,
        "dianzan" : dianzan,
        "zuopin" : zuopin,
        "xihuan" : xihuan
    }

def Run(xml):
    os.system("adb shell input keyevent 4")
    #点击头像
    os.system("adb shell input tap " + str(xml.touxiang["x"]) + " " + str(xml.touxiang["y"]))
    time.sleep(1)
    #拉起菜单
    os.system("adb shell input tap 960 100")
    time.sleep(1)
    #点击分享
    os.system("adb shell input tap 500 1400")
    time.sleep(1)
    #复制链接
    os.system("adb shell input tap 100 1780")
    time.sleep(1)
    #获取剪贴板的链接
    os.system("adb shell am broadcast -a clipper.get > ooxx.txt")
    #检查保存是否成功
    with open("./ooxx.txt", 'r', encoding='UTF-8') as file:
        data = file.read()
    #清空剪贴板
    os.system('adb shell am broadcast -a clipper.set -e text ""')
    #返回到主页面去
    os.system("adb shell input keyevent 4")
    data = data.replace("Broadcasting: Intent { act=clipper.get }\nBroadcast completed: result=-1, data=", "")
    data = data.replace('"在抖音，记录美好生活！ ', "")
    url = data.replace('/"\n', "")
    if len(url) <= 10:
        os.system("adb shell input keyevent 4")
        print("获取用户信息失败~~~")
        return {"ret" : 0}
    print("分享链接 : ", url)

    new_cmap = map_cmap_num(get_cmap_dict, get_num_cmap)

    response = get_html(url)

    response = replace_num_and_cmap(new_cmap,response)

    return manage(url, response)