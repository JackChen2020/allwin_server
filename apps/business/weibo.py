
import requests
import base64
import re
import rsa
import random
import urllib3
import json
import time
from urllib.parse import unquote,quote
from binascii import b2a_hex

urllib3.disable_warnings() # 取消警告

def get_timestamp():
    return int(time.time()*1000)

class WeiboBase(object):

    def __init__(self,**kwargs):
        self.username = kwargs.get("username",None)
        self.password = kwargs.get("password",None)
        self.gsid = kwargs.get("gsid")
        self.amount = kwargs.get("amount")
        self.num = kwargs.get("num")
        self.session = requests.session()
        self.session.verify = False
        self.uid = None
        self.st = None
        self.session.headers = {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 12_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 Weibo (iPhone11,8__weibo__9.11.2__iphone__os12.4.1)',
        }
        self.login()

    def datainitHandler(self):
        html = self.session.get('https://hongbao.weibo.com/h5/pay?groupid=1000303&ouid=6424853549').text
        self.st = html.split("st:")[1].split(",")[0].replace("'","")

    def get_session(self):
        try:
            with open('./cookies','r') as f:
                sessionRes = json.loads(f.read())
            self.uid = sessionRes.pop("uid")
            self.st = sessionRes.pop("st")
            # self.gsid = sessionRes.pop("gsid")
            for key,value in sessionRes.items():
                self.session.cookies.set(key, value)
            print("获取存储的session成功! \n uid :{} \n session:{}".format(self.uid,sessionRes))
            return True
        except Exception as e:
            print("获取存储的session错误! {}".format(str(e)))
            return False

    def save_sessino(self):
        sessionRes={}
        for key,value in self.session.cookies._cookies['.weibo.com']['/'].items():
            sessionRes[key] = value.value

        sessionRes['uid'] = self.uid
        sessionRes['st'] = self.st
        with open('./cookies','w') as f:
            f.write(json.dumps(sessionRes))

    def login(self):
        #如果已经存在session那么就跳过登录
        if self.get_session():
            return

        loginparams={}
        '''预登录，获取一些必须的参数'''
        loginparams['su'] = base64.b64encode(self.username.encode())  #阅读js得知用户名进行base64转码
        url = 'https://login.sina.com.cn/sso/prelogin.php?entry=weibo&callback=sinaSSOController.preloginCallBack&su={}&rsakt=mod&checkpin=1&client=ssologin.js(v1.4.19)&_={}'.format(quote(loginparams['su']),get_timestamp()) #注意su要进行quote转码
        response = self.session.get(url).content.decode()
        loginparams['nonce'] = re.findall(r'"nonce":"(.*?)"',response)[0]
        loginparams['pubkey'] = re.findall(r'"pubkey":"(.*?)"',response)[0]
        loginparams['rsakv'] = re.findall(r'"rsakv":"(.*?)"',response)[0]
        loginparams['servertime'] = re.findall(r'"servertime":(.*?),',response)[0]

        '''用rsa对明文密码进行加密，加密规则通过阅读js代码得知'''
        publickey = rsa.PublicKey(int(loginparams['pubkey'], 16), int('10001', 16))
        message = str(loginparams['servertime']) + '\t' + str(loginparams['nonce']) + '\n' + str(self.password)
        loginparams['sp'] = b2a_hex(rsa.encrypt(message.encode(), publickey))

        url = 'https://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.19)'
        data = {
            'entry': 'weibo',
            'gateway': '1',
            'from': '',
            'savestate': '7',
            'qrcode_flag': 'false',
            'useticket': '1',
            'pagerefer': 'https://login.sina.com.cn/crossdomain2.php?action=logout&r=https%3A%2F%2Fweibo.com%2Flogout.php%3Fbackurl%3D%252F',
            'vsnf': '1',
            'su': loginparams['su'],
            'service': 'miniblog',
            'servertime': str(int(loginparams['servertime']) + random.randint(1, 20)),
            'nonce': loginparams['nonce'],
            'pwencode': 'rsa2',
            'rsakv': loginparams['rsakv'],
            'sp': loginparams['sp'],
            'sr': '1536 * 864',
            'encoding': 'UTF - 8',
            'prelt': '35',
            'url': 'https://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack',
            'returntype': 'META',
        }
        response = self.session.post(url,data=data,allow_redirects=False).text # 提交账号密码等参数
        redirect_url = re.findall(r'location.replace\("(.*?)"\);',response)[0] # 微博在提交数据后会跳转，此处获取跳转的url
        result = self.session.get(redirect_url,allow_redirects=False).text  # 请求跳转页面
        ticket,ssosavestate = re.findall(r'ticket=(.*?)&ssosavestate=(.*?)"',result)[0] #获取ticket和ssosavestate参数
        uid_url = 'https://passport.weibo.com/wbsso/login?ticket={}&ssosavestate={}&callback=sinaSSOController.doCrossDomainCallBack&scriptId=ssoscript0&client=ssologin.js(v1.4.19)&_={}'.format(ticket,ssosavestate,get_timestamp())
        data = self.session.get(uid_url).text #请求获取uid
        self.uid = re.findall(r'"uniqueid":"(.*?)"',data)[0]
        print(self.uid)
        self.datainitHandler()
        self.save_sessino()
        # for key,value in self.session.cookies._cookies['.weibo.com']:
        #     if 'weibo.com' in key:
        #         print(key)
        # d={}
        # for key1,value1 in self.session.cookies._cookies['.weibo.com']['/'].items():
        #     d[key1] = value1.value
        #     # self.session.cookies.set()
        # print(d)
        # self.session.cookies.set("authentication", "这里写cookies")
        # print(self.session.cookies.get_dict())
        # for key,value in self.session.cookies.get_dict().items():
        #     self.session1.cookies.set(key, value)

class WeiboHbPay(WeiboBase):

    def __init__(self,**kwargs):

        self.payScWeiboUrl = None
        self.payScWeiboParams = None
        self.wapPayUrl = None

        super(WeiboHbPay,self).__init__(**kwargs)
        self.session.headers = {
            "Referer": "https://hongbao.weibo.com/h5/pay?groupid=1000303&ouid={}".format(self.uid),
            "Content-Type": "application/x-www-form-urlencoded",
            "Origin": "https://hongbao.weibo.com",
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 12_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 Weibo (iPhone11,8__weibo__9.11.2__iphone__os12.4.1)',
        }

    def getPayUrl(self):
        url = "https://hongbao.weibo.com/aj_h5/createorder?st={}&current_id={}".format(self.st,self.uid)
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
        res = json.loads(self.session.post(url, data).content.decode("utf-8"))
        if res['ok'] != 1:
            print("重新获取session")
        else:
            self.payScWeiboUrl = res['url']

    def getPayParams(self):

        params =  ""
        try:
            self.session.post(self.payScWeiboUrl)
        except Exception as a:
            print(a)
            params = str(a).split("No connection adapters were found for")[1].\
                replace("sinaweibo://wbpay?", "").replace("'",'').split("pay_params=")[1]
            params = unquote(params, 'utf-8')
        self.payScWeiboParams = params

    def orderForWeibo(self):
        data={
            'uid' : self.uid,
            'gsid' : self.gsid,
            'request_str' : self.payScWeiboParams,
            'is4g' : 0,
            'apple_pay_allowed' :  0,
            'from' : "109B293010",
            "v_p" : 78,
            "wm" : "3333_2001",
            "lang" : "zh_CN"
        }
        url = "https://pay.sc.weibo.com/api/client/opensdk/pay/prepare"
        self.session.headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 12_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 Weibo (iPhone11,8__weibo__9.11.2__iphone__os12.4.1)',
        }
        try:
            self.session.post(url,data)
        except Exception as e:
            print("createOrderForWeibo Error ： {}".format(str(e)))

    def orderForAliPay(self):

        data={
            'uid' : self.uid,
            'gsid' : self.gsid,
            "channel" : "ali_wap",
            "coupon_amount" : 0,
            'request_str' : self.payScWeiboParams,
            'from' : "109B293010",
            "v_p" : 78,
            "wm" : "3333_2001",
            "lang" : "zh_CN"
        }
        url = "https://pay.sc.weibo.com/api/client/opensdk/pay/buildparams"
        self.session.headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            'User-Agent': 'iOS__iPhone__iOS__12.4.1__828*1792__iPhone11,8__arm64e__0__9.11.2__2.0.0',
        }
        try:
            res = json.loads(self.session.post(url, data).content.decode('utf-8'))
            # 成功 code=="100000"
            self.wapPayUrl = res['data']['wap_pay_url']
        except Exception as e:
            print("createOrderForAliPay Error ： {}".format(str(e)))

    def createSkipAliPayResponse(self):

        return self.session.get(url=self.wapPayUrl).text

    def run(self):
        self.getPayUrl()
        self.getPayParams()
        self.orderForWeibo()
        self.orderForAliPay()
        return self.createSkipAliPayResponse()


if __name__ == '__main__':
    username="17623069111"
    password="!@#tc123"
    gsid="_2A25w42jBDeRxGeBK6VYZ9S3JzzWIHXVRufsJrDV6PUJbkdANLVn7kWpNR848UD1sYIUKuVtFVB3UFF3F9vWxNkJI"

    WeiboHbPay(username=username,password=password,gsid=gsid,amount=100,num=1).run()