
import os
import sys
import django
pathname = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, pathname)
sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# print()

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "education.settings")
from django.db import transaction
django.setup()

from apps.order.models import CashoutList

def duizhangDf():
    with transaction.atomic():
        for item in CashoutList.objects.filter(paypassid=69):
            res = daifuOrderQuery(request={
                "userid": item.userid,
                "dfordercode": item.downordercode,
                "paypassid": item.paypassid
            })

            item.df_status = res.get("data").get("code")
            item.save()


if __name__ == '__main__':
    duizhangDf()