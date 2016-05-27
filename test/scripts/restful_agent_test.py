#!/usr/bin/env python
#coding:utf-8

import os.path
import sys
from cgi import parse_qs

sys.path.append(os.path.join(os.path.join(os.path.join( os.path.dirname(os.path.dirname(__file__)))), 'Public/public_pkg'))
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

params_dict = parse_qs(query_string)

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



