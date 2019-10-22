'''
Created on 2012-7-3
'''
import jd.api
import json

jd.setDefaultAppInfo("26EAC2509056EB38FB623D9A49296D2C", "1abdc5a97ecb4594ab7b772296bcfbbd")
a = jd.api.UmpToolsGetRequest()
a.cid = "1"
a.value_id = "1"
a.source = "1"
a.ip = "1"

try:
    f= a.getResponse("1f1d3048-220a-484d-ad93-f3808d9aacc1")
    print(json.dumps(f, ensure_ascii=False))
except Exception as e:
    print(e)
    
