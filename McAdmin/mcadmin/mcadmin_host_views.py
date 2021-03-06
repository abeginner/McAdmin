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
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required

from McAdmin.mcadmin.mcadmin_forms import *
from McAdmin.mcadmin.models import *
from McAdmin.mcadmin.backends import CmdbBackend
from McAdmin.mcadmin.fsms import *

from contrib import restful
from contrib import RegEx


class HostQueryView(SingleObjectMixin, ListView):
    
    form_class = HostQueryForm
    paginate_by = 40
    template_name = "mcadmin/host_display.html"
    model = MemcacheHost
    request = None
    
    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        self.request = request
        self.post_data = request.POST
        self.object = self.get_queryset()
        if self.request.POST.has_key('page'):
            page = self.request.POST['page'][0]
            self.kwargs['page'] = page
            return super(HostQueryView, self).get(request, *args, **kwargs)
        return super(HostQueryView, self).get(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super(HostQueryView, self).get_context_data(**kwargs)
        csrf_token = csrf(self.request)      
        context.update(csrf_token)
        form = self.form_class(initial=self.request.POST)
        context.update({'form': form })
        if self.request.GET.has_key('msg'):
            context.update({'msg':self.request.GET['msg']})
        if self.request.GET.has_key('msg_type'):
            context.update({'msg_type':self.request.GET['msg_type']})
        return context
        
    def get_queryset(self):
        queryset = self.model.object.exclude(status=5)
        if self.request.method == 'POST':
            if self.request.POST['server_code'] != u'':
                server_code_list = []
                for i in self.request.POST['server_code'].split():
                    try:
                        server_code_list.append(int(i))
                    except:
                        pass
                queryset = queryset.filter(server_code__in=server_code_list)
            if self.request.POST['interip'] != u'':
                interip_list = self.request.POST['interip'].split()
                queryset = queryset.filter(interip__in=interip_list)
            if self.request.POST['idc_fullname'] != u'':
                queryset = queryset.filter(idc_fullname=self.request.POST['idc_fullname'])
            return queryset
        if self.request.method == 'GET':
            return queryset
    
    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        context = {}
        csrf_token = csrf(request)
        context.update(csrf_token)
        form = self.form_class()
        context.update({'form': form })
        if request.GET.has_key('msg'):
            context.update({'msg':request.GET['msg']})
        if request.GET.has_key('msg_type'):
            context.update({'msg_type':request.GET['msg_type']})
        return render_to_response(self.template_name, context_instance=RequestContext(request, context))


class HostCreateView(View):
    form_class = HostCreateFrom
    template_name = 'mcadmin/host_create.html'
    
    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        c = {}
        c.update(csrf(request))
        form = self.form_class()
        c.update({'form': form })
        return render_to_response(self.template_name, context_instance=RequestContext(request, c))
    
    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        server_code = request.POST["server_code"]
        ipaddress = request.POST["ipaddress"]
        description = request.POST["description"]
        query_dict = {}
        if server_code != u'':
            try:
                query_dict['server_code'] = [long(server_code),]
            except:
                pass
        if ipaddress != u'':
            query_dict['ips'] = [ipaddress,]
        if len(query_dict) > 0:
            backend = CmdbBackend()
            server_info_list = backend.get_serverinfo(query_dict)
        else:
            return HttpResponseRedirect("/mcadmin/host/display?msg_type=warning&msg=需要serverid或ip地址")
        if len(server_info_list) != 1:
            return HttpResponseRedirect("/mcadmin/host/display?msg_type=warning&msg=查询不到主机数据，请检查CMDB确认该主机是否存在")
        server_info = server_info_list[0]
        host_fsm = MemcacheHostFSM()
        try:
            mc_host = MemcacheHost.object.get(server_code=server_info[u'server_code'])
            if mc_host.status != 5:
                return HttpResponse('111')
                return HttpResponseRedirect("/mcadmin/host/display?msg_type=warning&msg=查询到memcache宿主机存在，且状态为" + str(mc_host.status) + ',拒绝添加.')
            mc_host.status = 0
            host_fsm.add_by_model(mc_host)
        except MemcacheHost.DoesNotExist:
            server_code = server_info[u'server_code']
            interip = None
            if server_info.has_key(u'ips'):
                for item in server_info[u'ips']:
                    if item[0] == u'inter':
                        interip = item[1]
                        break
            if not interip:
                return HttpResponseRedirect("/mcadmin/host/display?msg_type=warning&msg=主机内网ip不存在，无法添加为memcache宿主机")
            status = 0
            version = '1.4.14'
            idc_code = server_info[u'idc_code']
            idc_fullname = server_info[u'idc_fullname']
            mc_host = MemcacheHost(server_code=server_code, interip=interip, status=status, version=version,
                                   idc_code=idc_code, idc_fullname=idc_fullname, description=description)
            host_fsm.add_by_model(mc_host)
        except Exception, e:
            return HttpResponse(str(e))
            return HttpResponseRedirect("/mcadmin/host/display?msg_type=warning&msg=发生未知错误")
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
            return HttpResponseRedirect("/mcadmin/host/display?msg_type=danger&msg=未部署agent或agent工作异常,部署失败")
        request_data = {'host':mc_host.interip}
        request_url = 'http://' + agent_info.bind_host + ':' + str(agent_info.bind_port)
        request_application = 'mcadmin'
        request_controller = 'memcache_host'
        try:
            do_create_mamcachehost = restful.create(request_url, request_application, request_controller, data=request_data)
        except:
            if host_fsm.cheage_status_to(mc_host.server_code, 0):
                mc_host.status = 0
                mc_host.save()
            return HttpResponseRedirect("/mcadmin/host/display?msg_type=warning&msg=访问agent异常,部署失败")
        if do_create_mamcachehost.status_code == 200:
            rs = do_create_mamcachehost.json()
        else:
            return HttpResponseRedirect("/mcadmin/group/display?msg_type=warning&msg=响应码:" + str(do_create_mamcachehost.status_code) \
                                        + "响应内容" + str(do_create_mamcachehost.text))
        failures = rs.get('stdout', {}).get(mc_host.interip, {}).get('failures', None)
        unreachable = rs.get('stdout', {}).get(mc_host.interip, {}).get('unreachable', None)
        if failures != 0 or unreachable != 0:
            if host_fsm.cheage_status_to(mc_host.server_code, 0):
                mc_host.status = 0
                mc_host.save()
            return HttpResponseRedirect("/mcadmin/host/display?msg_type=warning&msg=部署过程发现错误")
        if host_fsm.cheage_status_to(mc_host.server_code, 2):
            mc_host.status = 2
            mc_host.save()
        else:
            return HttpResponseRedirect("/mcadmin/host/display?msg_type=warning&msg=Memcached宿主机" + str(mc_host.interip) + "切换为Ready状态失败.")
        if host_fsm.cheage_status_to(mc_host.server_code, 3):
            mc_host.status = 3
            mc_host.save()
        else:
            return HttpResponseRedirect("/mcadmin/host/display?msg_type=warning&msg=Memcached宿主机" + str(mc_host.interip) + "切换为Online状态失败.")
        return HttpResponseRedirect("/mcadmin/host/display?msg_type=success&msg=Memcached宿主机" + str(mc_host.interip) + "初始化完成.")


class HostDeleteView(View):
    
    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        if request.POST.has_key("server_code"):
            try:
                server_code = long(request.POST["server_code"])
            except:
                return HttpResponseRedirect("/mcadmin/host/display?msg_type=warning&msg=serverid只能是数字")
        try:
            mc_host = MemcacheHost.object.get(server_code=server_code)
        except MemcacheHost.DoesNotExist:
            return HttpResponseRedirect("/mcadmin/host/display?msg_type=warning&msg=宿主机不存在.")
        if MemcacheInstance.object.filter(host=mc_host).exclude(status=5).exists():
            return HttpResponseRedirect("/mcadmin/host/display?msg_type=warning&msg=宿主机存在活动实例，请先删除")
        if mc_host.status != 2 and mc_host.status != 0:
            return HttpResponseRedirect("/mcadmin/host/display?msg_type=warning&msg=只能删除处于准备中状态的宿主机")
        host_fsm = MemcacheHostFSM()
        host_fsm.add_by_model(mc_host)
        if host_fsm.cheage_status_to(server_code, 4):
            mc_host.status = 4
            mc_host.save()
        else:
            return HttpResponseRedirect("/mcadmin/host/display?msg_type=danger&msg=宿主机删除失败")
        if host_fsm.cheage_status_to(server_code, 5):
            mc_host.status = 5
            mc_host.save()
        else:
            return HttpResponseRedirect("/mcadmin/host/display?msg_type=danger&msg=宿主机删除失败")
        return HttpResponseRedirect("/mcadmin/host/display?msg_type=success&msg=宿主机删除成功")


class HostOfflineView(View):
    
    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        if request.POST.has_key("server_code"):
            try:
                server_code = long(request.POST["server_code"])
            except:
                return HttpResponseRedirect("/mcadmin/host/display?msg_type=warning&msg=serverid只能是数字")
        try:
            mc_host = MemcacheHost.object.get(server_code=server_code)
        except MemcacheHost.DoesNotExist:
            return HttpResponseRedirect("/mcadmin/host/display?msg_type=warning&msg=宿主机不存在.")
        if MemcacheInstance.object.filter(host=mc_host).exclude(status=5).exists():
            return HttpResponseRedirect("/mcadmin/host/display?msg_type=warning&msg=宿主机存在活动实例，请先删除")
        if mc_host.status != 3:
            return HttpResponseRedirect("/mcadmin/host/display?msg_type=warning&msg=只能下线在线状态的宿主机")
        host_fsm = MemcacheHostFSM()
        host_fsm.add_by_model(mc_host)
        if host_fsm.cheage_status_to(server_code, 2):
            mc_host.status = 2
            mc_host.save()
            return HttpResponseRedirect("/mcadmin/host/display?msg_type=success&msg=宿主机下线成功")
        else:
            return HttpResponseRedirect("/mcadmin/host/display?msg_type=warning&msg=宿主机下线失败")


class HostOnlineView(View):
    
    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        if request.POST.has_key("server_code"):
            try:
                server_code = long(request.POST["server_code"])
            except:
                return HttpResponseRedirect("/mcadmin/host/display?msg_type=warning&msg=serverid只能是数字")
        try:
            mc_host = MemcacheHost.object.get(server_code=server_code)
        except MemcacheHost.DoesNotExist:
            return HttpResponseRedirect("/mcadmin/host/display?msg_type=warning&msg=宿主机不存在.")
        if mc_host.status != 2:
            return HttpResponseRedirect("/mcadmin/host/display?msg_type=warning&msg=只能上线准备状态的宿主机")
        host_fsm = MemcacheHostFSM()
        host_fsm.add_by_model(mc_host)
        if host_fsm.cheage_status_to(server_code, 3):
            mc_host.status = 3
            mc_host.save()
            return HttpResponseRedirect("/mcadmin/host/display?msg_type=success&msg=宿主机上线成功")
        else:
            return HttpResponseRedirect("/mcadmin/host/display?msg_type=warning&msg=宿主机上线失败")



