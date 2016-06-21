# coding=utf-8

import json
import sys
import os.path

from django.views.generic.base import View
from django.views.generic import ListView
from django.views.generic.detail import SingleObjectMixin
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.core.context_processors import csrf
from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response

from McAdmin.mcadmin.mcadmin_forms import *
from McAdmin.mcadmin.models import *
from McAdmin.mcadmin.backends import CmdbBackend
from McAdmin.mcadmin.fsms import *

from contrib import restful
from contrib import RegEx


class HostQueryView(SingleObjectMixin, ListView):
    
    form_class = HostQueryForm
    paginate_by = 20
    template_name = "mcadmin/host_display.html"
    model = MemcacheHost
    request = None
    
    def post(self, request, *args, **kwargs):
        self.request = request
        print self.request
        self.post_data = request.POST
        self.object = self.get_queryset()
        if self.request.POST.has_key('page'):
            return super(HostQueryView, self).get(request, page=self.request.POST['page'], *args, **kwargs)
        return super(HostQueryView, self).get(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super(HostQueryView, self).get_context_data(**kwargs)
        csrf_token = csrf(self.request)      
        context.update(csrf_token)
        print self.post_data
        form = self.form_class(initial=self.post_data)
        context.update({'form': form })
        return context
        
    def get_queryset(self):
        queryset = self.model.object.all()
        if self.request.method == 'POST':
            if self.request.POST.has_key('server_code'):
                server_code_list = self.request.POST['server_code']
                queryset = queryset.filter(server_code=int(self.request.POST['server_code']))
            if self.request.POST.has_key('interip'):
                queryset = queryset.filter(interip=self.request.POST['interip'])
            if self.request.POST.has_key('idc_fullname'):
                queryset = queryset.filter(idc_fullname=self.request.POST['idc_fullname'])
            return queryset
        if self.request.method == 'GET':
            return queryset
    
    def get(self, request, *args, **kwargs):
        context = {}
        csrf_token = csrf(request)
        context.update(csrf_token)
        form = self.form_class()
        context.update({'form': form })
        return render_to_response(self.template_name, context_instance=RequestContext(request, context))


class HostCreateView(View):
    form_class = HostCreateFrom
    template_name = 'mcadmin/host_create.html'
    
    def get(self, request, *args, **kwargs):
        c = {}
        c.update(csrf(request))
        form = self.form_class()
        c.update({'form': form })
        return render_to_response(self.template_name, context_instance=RequestContext(request, c))
    
    def post(self, request, *args, **kwargs):
        server_code = request.POST["server_code"]
        ipaddress = request.POST["ipaddress"]
        description = request.POST["description"]
        query_dict = {}
        if server_code != 0:
            query_dict['server_code'] = [server_code,]
        if ipaddress != u'':
            query_dict['ips'] = [ipaddress,]
        if len(query_dict) > 0:
            backend = CmdbBackend()
            server_info_list = backend.get_serverinfo(query_dict)
        else:
            return HttpResponse(u"需要serverid或ip地址")
        if len(server_info_list) != 1:
            return HttpResponse(u"查询不到主机数据，请检查CMDB确认该主机是否存在")
        server_info = server_info_list[0]
        host_fsm = MemcacheHostFSM()
        try:
            mc_host = MemcacheHost.object.get(server_code=server_info['server_code'])
            host_fsm.add_by_model(mc_host)
            status = host_fsm.get_status(server_info['server_code'])
            if status != 5:
                return HttpResponse(u"查询到memcache宿主机存在，且状态为" + host_fsm.get_status_name(status) + u',拒绝添加.')
            mc_host.status = 0
        except MemcacheHost.DoesNotExist:
            server_code = server_info['server_code']
            interip = None
            if server_info.has_key('ips'):
                for item in server_info['ips']:
                    if item[0] == 'inter':
                        interip = item[1]
                        break
            if not interip:
                return HttpResponse(u"主机内网ip不存在，无法添加为memcache宿主机.")
            status = 0
            version = '1.4.14'
            idc_code = server_info['idc_code']
            idc_fullname = server_info['idc_fullname']
            mc_host = MemcacheHost(server_code=server_code, interip=interip, status=status, version=version,
                                   idc_code=idc_code, idc_fullname=idc_fullname, description=description)
        except:
            return HttpResponse(u"发生未知错误")
        mc_host.save()
        if host_fsm.cheage_status_to(mc_host.server_code, 1):
            mc_host.status = 1
            mc_host.save()
        try:
            agent_info = MemcacheAgent.object.get(idc_code=mc_host.idc_code)
        except MemcacheAgent.DoesNotExist:
            if host_fsm.cheage_status_to(mc_host.server_code, 0):
                mc_host.status = 0
                mc_host.save()
            return HttpResponse(u"未部署agent或agent工作异常,部署失败")
        request_data = {'host':mc_host.interip}
        request_url = 'httk://' + agent_info.bind_host + ':' + agent_info.bind_port
        request_application = 'mcadmin'
        request_controller = 'memcache_host'
        try:
            do_create_mamcachehost = restful.create(request_url, request_application, request_controller, data=request_data)
        except:
            if host_fsm.cheage_status_to(mc_host.server_code, 0):
                mc_host.status = 0
                mc_host.save()
            return HttpResponse(u"访问agent异常,部署失败")
        rs = json.loads(do_create_mamcachehost)
        failures = rs.get('stdout', {}).get(mc_host.interip, {}).get('failures', None)
        unreachable = rs.get('stdout', {}).get(mc_host.interip, {}).get('unreachable', None)
        if failures != 0 or unreachable != 0:
            if host_fsm.cheage_status_to(mc_host.server_code, 0):
                mc_host.status = 0
                mc_host.save()
            return HttpResponse(u"部署过程发现错误")
        if host_fsm.cheage_status_to(mc_host.server_code, 2):
            mc_host.status = 2
            mc_host.save()
        else:
            return HttpResponse(u"Memcached宿主机" + mc_host.interip + u"切换为Ready状态失败.")
        if host_fsm.cheage_status_to(mc_host.server_code, 3):
            mc_host.status = 3
            mc_host.save()
        else:
            return HttpResponse(u"Memcached宿主机" + mc_host.interip + u"切换为Online状态失败.")
        return HttpResponse(u"Memcached宿主机" + mc_host.interip + u"初始化完成.")


class HostDeleteView(View):
    
    def post(self, request, *args, **kwargs):
        server_code = request.POST["server_code"]
        try:
            mc_host = MemcacheHost.object.get(server_code=server_code)
        except MemcacheHost.DoesNotExist:
            return HttpResponse(u"memcache宿主机不存在.")
        try:
            inc_count = MemcacheInstance.object.filter(host=mc_host).exclude(status=5).conut()
        except:
            return HttpResponse(u"发生未知错误.")
        if inc_count != 0:
            return HttpResponse(u"该宿主机存在活动实例，请先删除实例.")
        



