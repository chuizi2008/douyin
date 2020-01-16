import cv2 as cv
import numpy as np
import aircv as ac
from PIL import Image
import os

#imgsrc=原始图像，imgobj=待查找的图片
def Check_SaveVideo_v1(imgsrc,imgobj):
    confidencevalue = 0.5
    imsrc = ac.imread(imgsrc)
    imobj = ac.imread(imgobj)
 
    match_result = ac.find_template(imsrc,imobj)  # {'confidence': 0.5435812473297119, 'rectangle': ((394, 384), (394, 416), (450, 384), (450, 416)), 'result': (422.0, 400.0)}
    return match_result is not None

def get_outfile(infile, outfile):
    if outfile:
        return outfile
    dir, suffix = os.path.splitext(infile)
    outfile = '{}-out{}'.format(dir, suffix)
    return outfile

def resize_image(infile, outfile='', x_s=600):
    """修改图片尺寸
    :param infile: 图片源文件
    :param outfile: 重设尺寸文件保存地址
    :param x_s: 设置的宽度
    :return:
    """
    im = Image.open(infile)
    x, y = im.size
    y_s = int(y * x_s / x)
    out = im.resize((x_s, y_s), Image.ANTIALIAS)
    outfile = get_outfile(infile, outfile)
    out.save(outfile)

def CaiJian(in_filename, out_filename):
    img = Image.open(in_filename)
    x, y = img.size
    cropped = img.crop((0, x, y / 2, y))  # (left, upper, right, lower)
    cropped.save(out_filename)

def CaiJianEx(in_filename, out_filename, x, y, x1, y1):
    img = Image.open(in_filename)
    cropped = img.crop((x, y, x1, y1))  # (left, upper, right, lower)
    cropped.save(out_filename)

'''
resize_image("G:/douyin/1.png")
CaiJian('G:/douyin/1-out.png','G:/douyin/test.png')
ret = Check_SaveVideo_v1('G:/douyin/test.png', 'G:/douyin/savebutton.png')
if ret != None:
    print('1 正确')
else:
    print('1 错误')

resize_image("G:/douyin/2.png")
CaiJian('G:/douyin/2-out.png','G:/douyin/test.png')
ret = Check_SaveVideo_v1('G:/douyin/test.png', 'G:/douyin/savebutton.png')
if ret != None:
    print('2 正确')
else:
    print('2 错误')

resize_image("G:/douyin/3.png")
CaiJian('G:/douyin/3.png','G:/douyin/test.png')
ret = Check_SaveVideo_v1('G:/douyin/test.png', 'G:/douyin/savebutton.png')
if ret != None:
    print('3 正确')
else:
    print('3 错误')
'''