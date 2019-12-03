

from requests import request
import urllib3
import json

from urllib.parse import unquote

urllib3.disable_warnings() # 取消警告


class woboBase(object):

    def __init__(self,**kwargs):
        self.username = kwargs.get("username")
        self.password = kwargs.get("password")

        self.uid = "6424853549"
        self.amount = kwargs.get("amount")
        self.num = kwargs.get("num")

        self.cookies={
            "HTTP_USER_AGENT_WEIBO":"iPhone11%2C8__weibo__9.11.2__iphone__os12.4.1",
            "SCF":"AjOaGw1K_o2AsNr4Ql_tYHnj67vJMckjmCjIsY1bzl6eCy-sgSxPlrrsrWA9AZK4aA..",
            "SUB":"_2A25w4U1tDeRhGeBK6VYZ9S3JzzWIHXVQfX0lrDV6PUJbitAKLU7CkWtNR848UGL6HjthbLXtJuChinF-YnyLJNKg",
            "SUBP":"0033WrSXqPxfM725Ws9jqgMF55529P9D9WhynzPaK8eg5ghc_zslWHoV5NHD95QcShzX1h-0SKB4Ws4DqcjMi--NiK.Xi-2Ri--ciKnRi-zNSoBEShnfe0-X1Btt",
            "SUHB":"0laFZshoUGdKXu"
        }
        self.gsid="_2A25w4jOdDeRxGeBK6VYZ9S3JzzWIHXVRtsBVrDV6PUJbkdAKLVrFkWpNR848UFt7xYkVzfuFqtRWKnKgMm60SgJA"

    def getRequestForWeibo(self):
        url = "https://hongbao.weibo.cn/aj_h5/createorder?st=0cfa67&current_id={}".format(self.uid)
        data = {
            "uid": self.uid,
            "groupid": "1000303",
            "eid": 0,
            "amount": self.amount,
            "num": self.num,
            "share": 0,
            "_type": 1,
            "isavg": 0,
            "tab": 1,
            "genter": "f,m",
            "clear": 1
        }
        headers = {
            "Referer": "https://hongbao.weibo.cn/h5/pay?groupid=1000303&ouid={}".format(self.uid),
            "Content-Type": "application/x-www-form-urlencoded",
            "Origin": "https://hongbao.weibo.cn",
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 12_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 Weibo (iPhone11,8__weibo__9.11.2__iphone__os12.4.1)',
            "Cookie": "HTTP_USER_AGENT_WEIBO={}; SCF={}; SUB={}; SUBP={}; SUHB={}".format(
                self.cookies['HTTP_USER_AGENT_WEIBO'],
                self.cookies['SCF'],
                self.cookies['SUB'],
                self.cookies['SUBP'],
                self.cookies['SUHB']
            )
        }
        res = request(method='POST', url=url, data=data, headers=headers, verify=False)
        return json.loads(res.content.decode("utf-8"))['url']

    def swichBankPayForWeibo(self,url):
        headers = {
            "Referer": "https://hongbao.weibo.cn/h5/pay?groupid=1000303&ouid=6424853549",
            "Content-Type": "application/x-www-form-urlencoded",
            "Origin": "https://hongbao.weibo.cn",
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 12_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 Weibo (iPhone11,8__weibo__9.11.2__iphone__os12.4.1)'
        }
        params =  ""
        try:
            request(method="GET", url=url, headers=headers, verify=False)
        except Exception as a:
            params = str(a).split("No connection adapters were found for")[1].\
                replace("sinaweibo://wbpay?", "").replace("'",'').split("pay_params=")[1]
            params = unquote(params, 'utf-8')
        return params

    def createOrderForWeibo(self,params):
        data={
            'uid' : self.uid,
            'gsid' : self.gsid,
            'request_str' : params,
            'is4g' : 0,
            'apple_pay_allowed' :  0,
            'from' : "109B293010",
            "v_p" : 78,
            "wm" : "3333_2001",
            "lang" : "zh_CN"
        }
        url = "https://pay.sc.weibo.com/api/client/opensdk/pay/prepare"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            'User-Agent': 'iOS__iPhone__iOS__12.4.1__828*1792__iPhone11,8__arm64e__0__9.11.2__2.0.0',
        }
        try:
            json.loads(request(method="POST", url=url, headers=headers, data=data, verify=False).content.decode('utf-8'))
        except Exception as e:
            print("createOrderForWeibo Error ： {}".format(str(e)))

    def createOrderForAliPay(self,params):

        data={
            'uid' : self.uid,
            'gsid' : self.gsid,
            "channel" : "ali_cashier",
            "coupon_amount" : 0,
            'request_str' : params,
            'from' : "109B293010",
            "v_p" : 78,
            "wm" : "3333_2001",
            "lang" : "zh_CN"
        }
        url = "https://pay.sc.weibo.com/api/client/opensdk/pay/buildparams"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            'User-Agent': 'iOS__iPhone__iOS__12.4.1__828*1792__iPhone11,8__arm64e__0__9.11.2__2.0.0',
        }
        try:
            return json.loads(request(method="POST", url=url, headers=headers, data=data, verify=False).content.decode('utf-8'))
        except Exception as e:
            print("createOrderForAliPay Error ： {}".format(str(e)))

    def run(self):
        url = self.getRequestForWeibo()
        params = self.swichBankPayForWeibo(url)
        self.createOrderForWeibo(params)
        res = self.createOrderForAliPay(params)
        return res

if __name__ == '__main__':
    woboBase().run()