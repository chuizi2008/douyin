# -*- coding: utf-8 -*-
from tencentcloud.common import credential
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException

# 导入对应产品模块的client models。
from tencentcloud.ticm.v20181127 import ticm_client, models
from tencentcloud.common.abstract_client import AbstractClient
from tencentcloud.common.profile.client_profile import ClientProfile

import base64

class Tencent_Cloud_tiia():
    def __init__(self):
        # 实例化一个客户端配置对象，可以指定超时时间等配置
        clientProfile = ClientProfile()
        clientProfile.signMethod = "TC3-HMAC-SHA256"  # 指定签名算法

        # 实例化一个认证对象，入参需要传入腾讯云账户secretId，secretKey
        self.cred = credential.Credential(secretId, secretKey)
        
        # 实例化要请求产品(以cvm为例)的client对象
        self.client = ticm_client.TicmClient(self.cred,'ap-guangzhou',clientProfile)

        # 实例化一个请求对象
        self.req = models.ImageModerationRequest()
        self.req.Scenes = ["PORN"]

    def ImageModeration(self, filename):
        try:
            with open(filename, 'rb') as bin_data:
                image_data = bin_data.read()

            image_data = base64.b64encode(image_data)
            image_data = image_data.decode("utf-8")

            self.req.ImageBase64 = image_data

            # 通过client对象调用想要访问的接口，需要传入请求对象
            resp = self.client.ImageModeration(self.req)

            # 输出json格式的字符串回包
            print(resp.to_json_string())

            if resp.PornResult.Code != 0:
                return {"ret" : 0}

            return {"ret" : 200,
                    "Suggestion" : resp.PornResult.Suggestion,
                    "Confidence" :  resp.PornResult.Confidence,
                    "Type" : resp.PornResult.Type}

        except TencentCloudSDKException as err:
            print(err)
            return {"ret" : 0}