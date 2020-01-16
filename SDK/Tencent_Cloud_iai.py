# -*- coding: utf-8 -*-
from tencentcloud.common import credential
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException

# 导入对应产品模块的client models。
from tencentcloud.iai.v20180301 import iai_client, models
from tencentcloud.common.abstract_client import AbstractClient
from tencentcloud.common.profile.client_profile import ClientProfile

import base64

class Tencent_Cloud_iai():
    def __init__(self):
        # 实例化一个客户端配置对象，可以指定超时时间等配置
        clientProfile = ClientProfile()
        clientProfile.signMethod = "TC3-HMAC-SHA256"  # 指定签名算法

        # 实例化一个认证对象，入参需要传入腾讯云账户secretId，secretKey
        self.cred = credential.Credential(secretId, secretKey)

        # 实例化要请求产品(以cvm为例)的client对象
        self.client = iai_client.IaiClient(self.cred,'ap-chengdu',clientProfile)

        # 实例化一个请求对象
        self.req = models.DetectFaceRequest()
        self.req.FaceModelVersion = "3.0"
        self.req.NeedFaceAttributes = 1

    def DetectFace(self, filename):
        try:
            with open(filename, 'rb') as bin_data:
                image_data = bin_data.read()

            image_data = base64.b64encode(image_data)
            image_data = image_data.decode("utf-8")

            self.req.Image = image_data

            # 通过client对象调用想要访问的接口，需要传入请求对象
            resp = self.client.DetectFace(self.req)

            # 输出json格式的字符串回包
            print(resp.to_json_string())

            for face in resp.FaceInfos:
                FaceAttributesInfo = face.FaceAttributesInfo
                print("Gender : ", FaceAttributesInfo.Gender, " Age : ", FaceAttributesInfo.Age, " Beauty : ", FaceAttributesInfo.Beauty)
                return {
                    "ret" : 200,
                    "Gender" : FaceAttributesInfo.Gender,
                    "Age" : FaceAttributesInfo.Age,
                    "Beauty" : FaceAttributesInfo.Beauty
                }

            return {
                "ret" : 0
            }

        except TencentCloudSDKException as err:
            print(err)
            return {
                "ret" : 0
            }