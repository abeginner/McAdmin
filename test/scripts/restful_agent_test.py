#!/usr/bin/env python
#coding:utf-8

import os.path
import sys
from cgi import parse_qs

"""
python restful_agent_test.py create http://192.168.134.129:8090 mcadmin memcache_host host=192.168.134.129
python restful_agent_test.py create http://192.168.134.129:8090 mcadmin memcache_instance "host=192.168.134.129&port=11212&max_memory=256&max_connection=10240&is_bind=1"
 python restful_agent_test.py update http://192.168.134.129:8090 mcadmin memcache_instance_manage_single 12345 "host=192.168.134.129&port=11214&operation=restart"
"""

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(sys.argv[0]))))
sys.path.append(os.path.join(BASE_DIR, 'Public/public_pkg'))
import restful

action = sys.argv[1]
url = sys.argv[2]
application = sys.argv[3]
controller = sys.argv[4]
if action == 'show' or action == 'update' or action == 'delete':
    rid = sys.argv[5]
    query_string = sys.argv[6]
else:
    query_string = sys.argv[5]

params_dict1 = parse_qs(query_string)
params_dict = {k:v[0] for (k, v) in params_dict1.items()}

if action == 'index':
    r = restful.index(url, application, controller, params_dict)
elif action == 'show':
    r = restful.show(url, application, controller, rid, params_dict)
elif action == 'create':
    r = restful.create(url, application, controller, params_dict)
elif action == 'update':
    r = restful.update(url, application, controller, rid, params_dict)
elif action == 'delete':
    r = restful.delete(url, application, controller, rid)


print 'header:' + str(r.headers)
if r.headers['content-type'] == 'application/json':
    print 'body:' + str(r.json())
else:
    print 'body:' + str(r.content)



