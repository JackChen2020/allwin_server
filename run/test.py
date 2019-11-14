import os
import sys
import django
pathname = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, pathname)
sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# print()

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "education.settings")

django.setup()

from django.db import transaction
from apps.business_new.df_api import daifuCallBack

from apps.user.models import BalList


if __name__ == '__main__':
    with transaction.atomic():
        BalList.objects.create(**{
            "userid" :10000,
            "amount" : 1,
            "bal" : 1,
            "confirm_bal" : 1,
            "memo" : '1',
            "ordercode": '1'
        })