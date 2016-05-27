import json
import sys
import os.path

from django.views.generic.base import View
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from McAdmin.mcadmin.models import *

@csrf_exempt
class ServerInfoView(View):
    
    
    @csrf_exempt
    def post(self, request, *args, **kwargs):
        """
        server information query api
        it just supports POST method and the request body must be json.
        the response body is dump by json like this:
        {'ips':{}, 'bussiness':[], 'server_code':int, 'idc':str, 'status':str, 'tech_admin':str, 'sysop_admin:':str,
        'os':str, 'server_type':str}
        """
        try:
            query_term = json.loads(request.body)
        except Exception, e:
            response = HttpResponse(str(e))
            response.status_code = 400
            return response
        if not isinstance(query_term, dict):
            response = HttpResponse(u"the request body must be json format.")
            response.status_code = 400
            return response
        query_set = server_query_engine(query_term)
        result = []
        if query_set:
            response = HttpResponse(query_set.server_code)

 
def server_query_engine(query_term={}):
    """
    server information query function.
    it just supports a dict type for query parameters.
    if there is some exception occur or QuerySet is empty, it will return None.
    normally, it will return a django QuerySet. 
    the query format like this:
    {'ips':[], 'bussiness':[], 'server_code':int, 'idc':str, 'status':str, 'tech_admin':str, 'sysop_admin:':str}      
    """
    query_set = None
    if query_term.has_key('ips'):
        if not isinstance(query_term['ips'], list):
            return None
        if  len(query_term['ips']) > 0:
            for ip in query_term['ips']:
                if not isinstance(ip, basestring):
                    return None
            query_set = Server.object.filter(ipaddress__ipaddress__in=query_term['ips'])
    if query_term.has_key('bussiness'):
        if not isinstance(query_term['bussiness'], list):
            return None
        if len(query_term['bussiness']) > 0:
            for bussiness in query_term['bussiness']:
                if not isinstance(bussiness, basestring):
                    return None
            if not query_set:
                query_set = Server.object.filter(bussiness__bussiness_fullname__in=query_term['bussiness'])
            else:
                query_set = query_set.filter(bussiness__bussiness_fullname__in=query_term['bussiness'])
    if query_term.has_key('server_code'):
        if not isinstance(query_term['server_code'], int):
            return None
        if not query_set:
            query_set = Server.object.filter(server_code=query_term['server_code'])
        else:
            query_set = query_set.filter(server_code=query_term['server_code'])
    if query_term.has_key('idc'):
        if not isinstance(query_term['idc'], basestring):
            return None
        if not query_set:
            query_set = Server.object.filter(idc__idc_fullname=query_term['idc'])
        else:
            query_set = query_set.filter(idc__idc_fullname=query_term['idc'])
    if query_term.has_key('status'):
        if not isinstance(query_term['status'], basestring):
            return None
        if not query_set:
            query_set = Server.object.filter(status__status_fullname=query_term['idc'])
        else:
            query_set = query_set.filter(status__status_fullname=query_term['idc'])
    if query_term.has_key('tech_admin'):
        if not isinstance(query_term['tech_admin'], basestring):
            return None
        if not query_set:
            query_set = Server.object.filter(tech_admin=query_term['tech_admin'])
        else:
            query_set = query_set.filter(tech_admin=query_term['tech_admin'])
    if query_term.has_key('sysop_admin'):
        if not isinstance(query_term['sysop_admin'], basestring):
            return None
        if not query_set:
            query_set = Server.object.filter(sysop_admin=query_term['sysop_admin'])
        else:
            query_set = query_set.filter(sysop_admin=query_term['sysop_admin'])
    return query_set









           
        