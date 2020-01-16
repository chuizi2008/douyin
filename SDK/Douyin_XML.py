import xml.dom.minidom as xmldom
import os
import OpenCV_Check
import pytesseract #Tesseract-OCR
from PIL import Image
import math

#海外抖音无法通过这种方式获取，只能图像识别，这种是版本问题可以使用
#利用uiautomator获取当前界面布局XML信息,需要暂停抖音视频播放
class Douyin_XML():
    def __init__(self):
        self.nickname = ''
        self.xmlfilepath = "C:/temp.xml"

    def Run(self):
        self.nickname = ""
        self.about = ""
        self.xin = ""
        self.pinlun = ""
        self.zhuanfa = ""
        self.GuangGao = False

        #暂停
        os.system("adb shell input tap 800 800")
        os.system("adb shell /system/bin/uiautomator dump --compressed /data/local/tmp/uidump.xml > ooxx.txt")
        with open("ooxx.txt", 'r') as file:
            data = file.read()
            n = data.find('UI hierchary dumped to:')
            if n < 0:
                print('获取界面XML信息失败')
                return

        os.system("adb pull /data/local/tmp/uidump.xml " + self.xmlfilepath)

        print ("xml文件路径：", self.xmlfilepath)

        # 得到文档对象
        domobj = xmldom.parse(self.xmlfilepath)
        print("xmldom.parse:", type(domobj))
        # 得到元素对象
        elementobj = domobj.documentElement
        self.Check(elementobj)

        #部分版本问题转发数无法获取，所以直接转成图像识别
        os.system("adb shell /system/bin/screencap -p /sdcard/screenshot.png")
        os.system("adb pull /sdcard/screenshot.png g:/douyin/png/check_savevideo.png")
        
        OpenCV_Check.CaiJianEx('g:/douyin/png/check_savevideo.png','G:/douyin/png/test.png', 940, 1540, 1080, 1660)
        pytesseract.pytesseract.tesseract_cmd = "D:/Tesseract-OCR/tesseract.exe" 
        self.zhuanfa = pytesseract.image_to_string(Image.open('G:/douyin/png/test.png'))
        #恢复播放
        os.system("adb shell input tap 800 800")


        '''
        print('昵称: ', self.nickname)
        print('介绍: ', self.about)
        print('点赞: ', self.xin)
        print('评论: ', self.pinlun)
        print('转发: ', self.zhuanfa)
        '''

    def bounds(self, str):
        val = str.replace('[', '')
        val = val.split(']')
        size1 = val[0].split(',')
        size2 = val[1].split(',')
        ooxx = {"x" : 0, "y" : 0}
        ooxx["x"] = int(size1[0]) + math.ceil((int(size2[0]) - int(size1[0])) / 2)
        ooxx["y"] = int(size1[1]) + math.ceil((int(size2[1]) - int(size1[1])) / 2)
        return ooxx

    def Check(self, node):
        for n in node.childNodes:
            if n.attributes._attrs['resource-id'].nodeValue == 'com.ss.android.ugc.aweme:id/title':
                self.nickname = n.attributes._attrs['text'].nodeValue
            elif n.attributes._attrs['resource-id'].nodeValue == 'com.ss.android.ugc.aweme:id/a8t':
                self.about = n.attributes._attrs['text'].nodeValue
                if self.about.find("[t]") > 0:
                    self.GuangGao = True
            elif n.attributes._attrs['resource-id'].nodeValue == 'com.ss.android.ugc.aweme:id/af1':
                self.xin = n.attributes._attrs['content-desc'].nodeValue.replace('未选中，喜欢', '')
                self.xin = self.xin.replace('，按钮', '')
            elif n.attributes._attrs['resource-id'].nodeValue == 'com.ss.android.ugc.aweme:id/a4b':
                self.pinlun = n.attributes._attrs['content-desc'].nodeValue.replace('评论', '')
                self.pinlun = self.pinlun.replace('，按钮', '')
            elif n.attributes._attrs['resource-id'].nodeValue == 'com.ss.android.ugc.aweme.diamond_sdk:id/btn_disable':
                self.GuangGao = True
            elif n.attributes._attrs['resource-id'].nodeValue == 'com.ss.android.ugc.aweme:id/c_c':
                self.GuangGao = True
            elif n.attributes._attrs['resource-id'].nodeValue == 'com.ss.android.ugc.aweme:id/emq':
                #<node index="1" text="" resource-id="com.ss.android.ugc.aweme:id/emq" class="android.widget.ImageView" package="com.ss.android.ugc.aweme" content-desc="张予曦" checkable="false" checked="false" clickable="true" enabled="true" focusable="false" focused="false" scrollable="false" long-clickable="false" password="false" selected="false" bounds="[941,972][1063,1094]"/>
                self.touxiang = self.bounds(n.attributes._attrs['bounds'].nodeValue)
                print("头像按钮水平位置 : ", self.touxiang)
            elif n.attributes._attrs['resource-id'].nodeValue == 'com.ss.android.ugc.aweme:id/dbn':
                #<node index="0" text="" resource-id="com.ss.android.ugc.aweme:id/dbn" class="android.widget.FrameLayout" package="com.ss.android.ugc.aweme" content-desc="" checkable="false" checked="false" clickable="true" enabled="true" focusable="false" focused="false" scrollable="false" long-clickable="false" password="false" selected="false" bounds="[954,1528][1054,1628]">
                self.fenxiang = self.bounds(n.attributes._attrs['bounds'].nodeValue)
                print("分享按钮水平位置 : ", self.fenxiang)
            self.Check(n)