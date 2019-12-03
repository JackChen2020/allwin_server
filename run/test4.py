
from urllib.parse import unquote


params="app_id=2016010401062614&biz_content=%7B%22subject%22%3A%22%E5%BE%AE%E5%8D%9A%E7%BA%A2%E5%8C%85%22%2C%22out_trade_no%22%3A%22104445495032488561%22%2C%22timeout_express%22%3A%221m%22%2C%22total_amount%22%3A%221.00%22%2C%22product_code%22%3A%22QUICK_MSECURITY_PAY%22%7D&charset=UTF-8&format=JSON&method=alipay.trade.app.pay&notify_url=https%3A%2F%2Fpay.sc.weibo.com%2Fapi%2Faliopen%2Fcharge%2Fnotify%3Fcharge_channel%3D2&sign=nCDoVfHLlI4jf2jL8I0tLn4tJ7bSIBnJs3xAk4tv%2BE%2BrX3t9yM4wBVdTCukmFLEQlzsoBhI1AMjkuAL9%2B8%2B3pN6f4DD77CLOeK8n3ResIpGsq%2FNIGof2jviv1n4PEKoLATKe%2BvDA8Wkm8SerOwqBdnf3d4N7a8Pfmd4RE3TL6sQe0WZmPIs4zciRAGOPgHdP5gvF3PASWtFBbCUiunIUJempFLDWDbgCvGaS32F7FmipwJeTV80M1Ye8RbnNkg2tXzCgO%2Fa0rOeEXoDYbwxmJmHuOwIUuJys7PSigCoCq0IENble3M6pM8WaoImwYut2a4vERF2%2BVvXf4cB7cLEKhA%3D%3D&sign_type=RSA2&timestamp=2019-12-03%2019%3A21%3A12&version=1.0"

params = unquote(params, 'utf-8')
data={}
for item in params.split("&") :
    data[item.split("=")[0]] = item.split("=")[1]

print(data)