

from requests import request
import json


class LastPassBase(object):

    def __init__(self,**kwargs):
        self.secret = kwargs.get('secret')
        self.data = kwargs.get('data',{})

    def _sign(self):
        pass

class LastPass_GCPAYS(LastPassBase):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)

        #订单生成地址
        self.create_order_url="http://47.97.62.178"

        self.appId = "G11959365W92A99213979DA592"
        self.appSecret = "12acb033b3065ae85306969c95ae40ecfee40cf7"

        self.username = "1018125792@qq.com"
        self.password = "hxzym@123456"

        self.keyStore = "7312Acs2"
        self.token = None

    def getToken(self):
        url = self.create_order_url + '/oauth/token'
        data=dict(
            client_id = self.appId,
            client_secret = self.appSecret,
            grant_type = "password",
            username = self.username,
            password = self.password
        )
        print(json.dumps(data))
        result = request('POST', url=url,
                         data=data,verify=False)
        # result = request('POST', url=url,
        #                  data=data, verify=False )

        return json.loads(result.content.decode('utf-8'))

    def refreshToken(self):
        if not self.token:
            res = self.getToken()
            self.token = res['access_token']

    def sso(self):
        self.refreshToken()
        print(self.token)
        url = self.create_order_url + '/user/profile/v1/info'
        result = request('GET', url=url,verify=False,headers={
                "ACCESSTOKEN" : self.token
            })

        if json.loads(result.content.decode('utf-8')).get("code") != 0 :
            print("鉴权失败!")

if __name__ == '__main__':
    LastPass_GCPAYS().sso()