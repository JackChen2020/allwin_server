import os
import sys,json
import django
pathname = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, pathname)
sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# print()

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "education.settings")

django.setup()

import time
from apps.business.weibo import WeiboHbHandler
from apps.pay.models import WeiBoHbList,WeiboPayUsername

"""
同步红包明细
"""

if __name__ == '__main__':

    while True:
        time.sleep(2)
        wPobj = WeiboPayUsername.objects.filter(type='0')

        if not wPobj.exists():
            continue

        for item in wPobj:

            if not item.uid or not len(item.uid):
                continue

            wObj = WeiBoHbList.objects.filter(uid=item.uid).order_by('-ctime')
            if not wObj.exists():
                ctime = "2019-12-01 00:00:01"
            else:
                ctime = wObj[0].ctime

            s = WeiboHbHandler(sessionRes=json.loads(item.session),cookieKey='pccookie',isSession=True)
            page=1
            count,res=s.Hblist(page=page)
            if count == 0:
                time.sleep(2)
                continue

            c=0
            for itemRes in json.dumps(res):
                if itemRes['ctime'] >= ctime:
                    c+=1
                    WeiBoHbList.objects.create(**{
                        "uid" : item.uid,
                        "group_id" : itemRes['group_id'],
                        "ctime" : itemRes['ctime'],
                        "hongbao_total_money" : itemRes['hongbao_total_money'],
                        "event_send_num_cash" : itemRes['event_send_num_cash'],
                        "event_total_num_cash" : itemRes['event_total_num_cash'],
                        "hongbaourl" : itemRes['hongbaourl'],
                        "eid" : itemRes['event_id'],
                        "close_openbag":itemRes['close_openbag']
                    })
            if c<count:
                continue
            else:
                page+=1
                count, res = s.Hblist(page=page)
                if count == 0:
                    time.sleep(2)
                    continue

                for itemRes in json.dumps(res):
                    if itemRes['ctime'] >= ctime:
                        c += 1
                        WeiBoHbList.objects.create(**{
                            "uid": item.uid,
                            "group_id": itemRes['group_id'],
                            "ctime": itemRes['ctime'],
                            "hongbao_total_money": itemRes['hongbao_total_money'],
                            "event_send_num_cash": itemRes['event_send_num_cash'],
                            "event_total_num_cash": itemRes['event_total_num_cash'],
                            "hongbaourl": itemRes['hongbaourl'],
                            "eid": itemRes['event_id'],
                            "close_openbag": itemRes['close_openbag']
                        })
                if c < count:
                    break