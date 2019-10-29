
from apps.user.models import Users

from utils.exceptions import PubErrorCustom

from apps.order.models import CashoutList

from libs.utils.string_extension import hexStringTobytes

from utils.log import logger
import hashlib

from apps.utils import upd_bal
from libs.utils.mytime import UtilTime

from apps.lastpass.utils import LastPass_BAWANGKUAIJIE
from libs.utils.string_extension import hexStringTobytes
from apps.cache.utils import RedisCaCheHandler
from apps.account import AccountCashoutConfirmForApi,AccountCashoutConfirmForApiFee



class dfHandler(object):


    def __init__(self,data,ip=None,islock=False,isip=True):

        print("ip:",ip)

        self.dfClass = LastPass_BAWANGKUAIJIE(data={})

        self.data = data

        #代付手续费
        self.fee = 3.0

        #T0提现 90%
        self.t0Tx = 0.9

        if islock:
            try:
                self.user = Users.objects.select_for_update().get(userid=self.data.get("businessid"))
            except Users.DoesNotExist:
                raise PubErrorCustom("无效的商户!")
        else:
            try:
                self.user = Users.objects.get(userid=self.data.get("businessid"))
            except Users.DoesNotExist:
                raise PubErrorCustom("无效的商户!")


        if isip:
            data =RedisCaCheHandler(
                method="filter",
                serialiers="WhiteListModelSerializerToRedis",
                table="whitelist",
                filter_value={
                    "userid" : self.user.userid
                }
            ).run()

            if not len(data):
                raise PubErrorCustom("拒绝访问!")

            isIpValid = False
            print(ip)
            for item in data[0]['dfobj'].split(','):
                print(item)
                if str(item)==str(ip):
                    isIpValid = True
                    break

            if not isIpValid:
                raise PubErrorCustom("拒绝访问!")

    def get_ok_bal(self):
        weeknum = UtilTime().get_week_day()

        if weeknum in [6,7]:
            ok_bal = float(self.user.today_pay_amount) * self.t0Tx - (float(self.user.today_cashout_amount) + float(self.user.today_fee_amount))
        else:
            ok_bal = float(self.user.lastday_bal) + (float(self.user.today_pay_amount) * self.t0Tx - (float(self.user.today_cashout_amount) + float(self.user.today_fee_amount)))

        print("用户ID{} 周几{} 昨日余额{} 当填充值金额{} 当天提现金额{} 当天手续费{}".format(self.user.userid, weeknum, self.user.lastday_bal,
                                                            self.user.today_pay_amount, self.user.today_cashout_amount,self.user.today_fee_amount ))

        return ok_bal

    def BalQuery(self):
        if not self.data.get("businessid"):
            raise PubErrorCustom("商户ID为空!")
        if not self.data.get("nonceStr"):
            raise PubErrorCustom("随机数!")


        md5params = "{}{}{}{}".format(
            self.user.google_token,
            str(self.data.get("businessid")),
            self.data.get("nonceStr"),
            self.user.google_token)
        md5params = md5params.encode("utf-8")

        logger.info("代付查询待签数据:{}".format(md5params))
        sign = hashlib.md5(md5params).hexdigest()
        logger.info("代付查询签名:{}-----{}".format(sign, self.data.get("sign")))
        if sign != self.data.get("sign"):
            raise PubErrorCustom("验签失败!")

        # user = AccountBase(userid=self.user.userid,amount=1).query()

        ok_bal = self.get_ok_bal()

        return {"data":{
            "bal" : round(float(self.user.bal),2),
            "stop_bal" : round(float(self.user.stop_bal),2),
            "ok_bal" : round(ok_bal,2)
        }}

    def BalQueryTest(self):
        if not self.data.get("businessid"):
            raise PubErrorCustom("商户ID为空!")

        # user = AccountBase(userid=self.user.userid,amount=1).query()

        ok_bal = self.get_ok_bal()

        return {"data":{
            "bal" : round(float(self.user.bal),2),
            "stop_bal" : round(float(self.user.stop_bal),2),
            "ok_bal" : round(ok_bal,2)
        }}

    def Query(self):
        if not self.data.get("businessid"):
            raise PubErrorCustom("商户ID为空!")
        if not self.data.get("down_ordercode"):
            raise PubErrorCustom("商户订单号为空!")
        if not self.data.get("nonceStr"):
            raise PubErrorCustom("随机数!")

        md5params = "{}{}{}{}{}".format(
            self.user.google_token,
            str(self.data.get("down_ordercode")),
            str(self.data.get("businessid")),
            self.data.get("nonceStr"),
            self.user.google_token)
        md5params = md5params.encode("utf-8")

        logger.info("代付查询待签数据:{}".format(md5params))
        sign = hashlib.md5(md5params).hexdigest()
        logger.info("代付查询签名:{}-----{}".format(sign, self.data.get("sign")))
        if sign != self.data.get("sign"):
            raise PubErrorCustom("验签失败!")


        self.dfClass.data['orderId'] = "DF%08d%s" % (self.user.userid,self.data.get("down_ordercode"))

        res = self.dfClass.df_query()

        print(res)

        return {"data":{
            "subcode" : res['REP_BODY']['subcode'],
            "submsg" : hexStringTobytes(res['REP_BODY']['submsg']).decode('utf-8') if 'submsg' in res['REP_BODY'] else '',
            "orderId": res['REP_BODY']['orderId'][10:] if 'orderId' in res['REP_BODY'] else '',
            "tranId": res['REP_BODY']['tranId'] if 'tranId' in res['REP_BODY'] else '',
        }}

    def check_params(self):
        if not self.data.get("businessid"):
            raise PubErrorCustom("商户ID为空!")
        if not self.data.get("down_ordercode"):
            raise PubErrorCustom("商户订单号为空!")
        if not self.data.get("nonceStr"):
            raise PubErrorCustom("随机数!")
        if not self.data.get("amount"):
            raise PubErrorCustom("金额不能为空!")

        if float(self.data.get("amount"))<=0 :
            raise PubErrorCustom("请输入正确的提现金额!")

        if not self.data.get("accountNo"):
            raise PubErrorCustom("银行卡号不能为空!")
        if not self.data.get("bankName"):
            raise PubErrorCustom("银行名称不能为空!")
        if not self.data.get("accountName"):
            raise PubErrorCustom("账户名称不能为空!")
        if not self.data.get("sign"):
            raise PubErrorCustom("签名不能为空!")

        md5params = "{}{}{}{}{}{}{}{}{}{}".format(
            self.user.google_token,
            str(self.data.get("down_ordercode")),
            str(self.data.get("businessid")),
            self.user.google_token,
            str(self.data.get("nonceStr")),
            str(self.data.get("amount")),
            str(self.data.get("accountNo")),
            str(self.data.get("bankName")),
            str(self.data.get("accountName")),
            self.user.google_token)
        md5params = md5params.encode("utf-8")

        logger.info("代付待签数据:{}".format(md5params))
        sign = hashlib.md5(md5params).hexdigest()
        logger.info("代付签名:{}-----{}".format(sign, self.data.get("sign")))
        if sign != self.data.get("sign"):
            raise PubErrorCustom("验签失败!")


    def handler(self):

        ok_bal = self.get_ok_bal()
        if float(ok_bal) - abs(float(self.user.cashout_bal)) - self.fee < float(self.data.get("amount")):
            raise PubErrorCustom("可提余额不足!")

        # self.user.cashout_bal = float(self.user.cashout_bal) + float(self.data.get("amount")) + self.fee

        cashlist = CashoutList.objects.create(**{
            "userid": self.user.userid,
            "name": self.user.name,
            "amount": float(self.data.get("amount")),
            "bank_name": hexStringTobytes(self.data.get("bankName")).decode('utf-8'),
            "open_name": hexStringTobytes(self.data.get("accountName")).decode('utf-8'),
            "bank_card_number": self.data.get("accountNo"),
            "status": "0",
            "downordercode" : self.data.get('down_ordercode'),

        })

        AccountCashoutConfirmForApi(user=self.user,amount=cashlist.amount).run()

        AccountCashoutConfirmForApiFee(user=self.user).run()

        self.dfClass.data['orderId'] = "DF%08d%s" % (cashlist.userid,cashlist.downordercode)
        self.dfClass.data['txnAmt'] = str(int(float(cashlist.amount) * 100.0))
        self.dfClass.data['accountNo'] = cashlist.bank_card_number
        self.dfClass.data['bankName'] = cashlist.bank_name
        self.dfClass.data['accountName'] = cashlist.open_name

        res = self.dfClass.df_bal_handler()

        cashlist.status = '1'
        cashlist.paypassid  = '54'
        cashlist.tranid = res['REP_BODY']['tranId']
        cashlist.save()

        # upd_bal(user=self.user,cashout_bal = cashlist.amount*-1,bal=cashlist.amount*-1,memo="Api代付")




        return None



    def run(self):

        self.check_params()
        self.handler()