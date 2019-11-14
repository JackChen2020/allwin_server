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


if __name__ == '__main__':
    with transaction.atomic():
        daifuCallBack().run()