import os.path
import sys
import requests
import json

"""
request data format:
{'ips':[], 'bussiness':[], 'server_code':int, 'idc':str, 'status':str, 'tech_admin':str, 'sysop_admin:':str}
"""


body = {'ips':['192.168.134.129']}
url = 'http://127.0.0.1/cmdb/api/server_info'


headers = {'content-type': 'application/json'}
r = requests.post(url, data=json.dumps(body), headers=headers)


print 'header:\n' + str(r.headers)
if r.headers['content-type'] == 'application/json':
    print 'body:' + str(r.json())
else:
    print 'body:' + str(r.content)