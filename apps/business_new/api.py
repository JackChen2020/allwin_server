from apps.utils import GenericViewSetCustom
from rest_framework.decorators import list_route

from core.decorator.response_new import Core_connector,Core_connector_DAIFU,Core_connector_NEICHONG

from apps.business.utils import CreateOrder
from apps.business_new.df_api import dfHandler
from apps.business_new.jd_api import jdHandler
from apps.lastpass.utils import LastPass_GCPAYS


class BusinessNewAPIView(GenericViewSetCustom):

    @list_route(methods=['POST'])
    @Core_connector()
    def create_order(self, request, *args, **kwargs):

        data={}
        for item in request.data:
            data[item] = request.data[item]
        return {"data":CreateOrder(user=request.user, request_param=data, lock="1").run()}

    @list_route(methods=['POST'])
    @Core_connector_DAIFU(transaction=True)
    def df(self,request):

        dfHandler(request.data,request.META.get("HTTP_X_REAL_IP"),True).run()
        return None

    @list_route(methods=['POST'])
    @Core_connector_DAIFU()
    def dfQuery(self,request):

        return dfHandler(request.data,request.META.get("HTTP_X_REAL_IP")).Query()

    @list_route(methods=['GET'])
    @Core_connector_DAIFU()
    def dfQueryTest(self,request):

        return dfHandler(request.query_params,request.META.get("HTTP_X_REAL_IP"),isip=False).BalQueryTest()

    @list_route(methods=['POST'])
    @Core_connector_DAIFU()
    def BalQuery(self,request):

        return dfHandler(request.data,request.META.get("HTTP_X_REAL_IP")).BalQuery()


    @list_route(methods=['POST'])
    @Core_connector_DAIFU()
    def JdOrderQuery(self,request):

        return jdHandler(request.data).OrderQuery()


    @list_route(methods=['POST'])
    @Core_connector_NEICHONG()
    def CardPays(self,request):
        data={}
        for item in request.data:
            data[item] = request.data[item]
        return LastPass_GCPAYS(data=data).run(request)