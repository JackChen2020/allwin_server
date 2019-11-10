import os
import sys
import django
pathname = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, pathname)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "education.settings")

django.setup()

from libs.utils.mytime import UtilTime
from apps.lastpass.utils import LastPass_GCPAYS


def neichong_callback():
    """
    内冲回调
    :return:
    """
    LastPass_GCPAYS(data={}).callback_run()


if __name__ == '__main__':
    neichong_callback()