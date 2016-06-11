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


class MemcacheInstance(object):
    pass
    

class HostQueryView(SingleObjectMixin, ListView):
    
    form_class = HostQueryForm
    paginate_by = 20
    template_name = "mcadmin/host_display.html"
    model = MemcacheHost
    request = None
    
    def post(self, request, *args, **kwargs):
        self.request = request
        self.object = self.get_queryset()
        return super(HostQueryView, self).get(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super(HostQueryView, self).get_context_data(**kwargs)
        csrf_token = csrf(self.request)      
        context.update(csrf_token)
        form = self.form_class()
        context.update({'form': form })
        return context
        
    def get_queryset(self):
        queryset = self.model.object.all()
        if self.request.POST['server_code'] != u'':
            queryset = queryset.filter(server_code=int(self.request.POST['server_code']))
        if self.request.POST['interip'] != u'':
            queryset = queryset.filter(interip=self.request.POST['interip'])
        if self.request.POST['idc_fullname'] != u'':
            queryset = queryset.filter(idc_fullname=self.request.POST['idc_fullname'])
        return queryset
    
    def get(self, request, *args, **kwargs):
        context = {}
        csrf_token = csrf(request)
        context.update(csrf_token)
        form = self.form_class()
        context.update({'form': form })
        return render_to_response(self.template_name, context_instance=RequestContext(request, context))
    

class BussinessQueryView(SingleObjectMixin, ListView):

    form_class = BussinessQueryForm
    paginate_by = 20
    template_name = "mcadmin/bussiness_display.html"
    model = MemcacheBussiness
    request = None
    
    def post(self, request, *args, **kwargs):
        self.request = request
        self.object = self.get_queryset()
        return super(HostQueryView, self).get(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super(HostQueryView, self).get_context_data(**kwargs)
        csrf_token = csrf(self.request)      
        context.update(csrf_token)
        form = self.form_class()
        context.update({'form': form })
        return context
        
    def get_queryset(self):
        queryset = self.model.object.all()
        if self.request.POST['bussiness_code'] != u'':
            queryset = queryset.filter(bussiness_code=int(self.request.POST['sbussiness_code']))
        if self.request.POST['bussiness_fullname'] != u'':
            queryset = queryset.filter(bussiness_fullname=self.request.POST['bussiness_fullname'])
        return queryset
    
    def get(self, request, *args, **kwargs):
        context = {}
        csrf_token = csrf(request)
        context.update(csrf_token)
        form = self.form_class()
        context.update({'form': form })
        return render_to_response(self.template_name, context_instance=RequestContext(request, context))


class SubsystemQueryView(SingleObjectMixin, ListView):

    paginate_by = 20
    template_name = "mcadmin/subsystem_display.html"
    model = MemcacheSubsystem
    request = None
    
    def get(self, request, *args, **kwargs):
        self.request = request
        self.object = self.get_queryset()
        return super(HostQueryView, self).get(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super(HostQueryView, self).get_context_data(**kwargs)
        return context
        
    def get_queryset(self):
        queryset = None
        if self.request.GET['bussiness_code']:
            queryset = queryset.filter(bussiness__bussiness_code=int(self.request.GET['sbussiness_code']))
        if self.request.GET['bussiness_fullname'] != u'':
            queryset = queryset.filter(bussiness__bussiness_fullname=self.request.GET['bussiness_fullname'])
        return queryset


class GroupQueryView(SingleObjectMixin, ListView):

    paginate_by = 20
    template_name = "mcadmin/group_display.html"
    model = MemcacheGroup
    request = None

    def get(self, request, *args, **kwargs):
        self.request = request
        self.object = self.get_queryset()
        return super(HostQueryView, self).get(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super(HostQueryView, self).get_context_data(**kwargs)
        return context
        
    def get_queryset(self):
        queryset = None
        if self.request.GET['subsystem_code']:
            queryset = queryset.filter(subsystem__subsystem_code=int(self.request.GET['subsystem_code']))
        if self.request.GET['subsystem_fullname'] != u'':
            queryset = queryset.filter(subsystem__subsystem_fullname=self.request.GET['subsystem_fullname'])
        return queryset


class InstanceQueryView(SingleObjectMixin, ListView):

    form_class = InstanceQueryForm
    paginate_by = 20
    template_name = "mcadmin/instance_display.html"
    model = MemcacheInstance
    request = None
    
    def post(self, request, *args, **kwargs):
        self.request = request
        self.object = self.get_queryset()
        return super(HostQueryView, self).get(request, *args, **kwargs)
    
    def get(self, request, *args, **kwargs):
        self.request = request
        self.object = self.get_queryset()
        if not self.object:
            context = {}
            csrf_token = csrf(self.request)
            context.update(csrf_token)
            form = self.form_class()
            context.update({'form': form })
            return context   
        return super(HostQueryView, self).get(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super(HostQueryView, self).get_context_data(**kwargs)
        csrf_token = csrf(self.request)
        context.update(csrf_token)
        form = self.form_class()
        context.update({'form': form })
        return context
        
    def get_queryset(self):
        queryset = None     
        if self.request.method == 'GET':
            if self.request.GET['subsystem_code']:
                queryset = self.model.object.filter(group__group_code=self.request.GET['subsystem_code'])
                return queryset
        if self.request.method == 'POST':
            queryset = self.model.all()
            if self.request.POST['instance_code'] != u'':
                legal_input = 0
                try:
                    instance_codes = [int(code) for code in self.request.POST['instance_code'].split()]
                except ValueError:
                    legal_input = 1
                if legal_input is 0:
                    queryset = queryset.filter(instance_code__in=instance_codes)
            if self.request.POST['host'] != u'':
                legal_input = 0
                try:
                    hosts = [host for host in self.request.POST['host'].split()]
                except ValueError:
                    legal_input = 1
                if legal_input is 0:
                    queryset = queryset.filter(host__interip__in=hosts)
            if self.request.POST['bussiness'] != u'':
                queryset = queryset.filter(group__subsystem__bussiness__bussiness_fullname=self.request.POST['bussiness'])
            if self.request.POST['subsystem'] != u'':
                queryset = queryset.filter(group__subsystem__subsystem_fullname=self.request.POST['subsystem'])
            if self.request.POST['tech_admin'] != u'':
                queryset = queryset.filter(tech_admin=self.request.POST['tech_admin'])
            if self.request.POST['sysop_admin'] != u'':
                queryset = queryset.filter(sysop_admin=self.request.POST['sysop_admin'])
        return queryset


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
        if server_code is not 0:
            query_dict['server_code'] = [server_code,]
        if ipaddress is not u'':
            query_dict['ips'] = [ipaddress,]
        if len(query_dict) > 0:
            backend = CmdbBackend()
            server_info_list = backend.get_serverinfo(query_dict)
        else:
            return HttpResponse(u"需要server id或ip地址！")
        if len(server_info_list) != 1:
            return HttpResponse(u"查询不到主机数据，请检查CMDB确认该主机是否存在！")
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
                    if item[0] is 'inter':
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
        host_fsm.cheage_status_to(mc_host.server_code, 1)
        mc_host.status = 1
        mc_host.save()
        try:
            agent_info = MemcacheAgent.object.get(idc_code=mc_host.idc_code)
        except MemcacheAgent.DoesNotExist:
            host_fsm.cheage_status_to(mc_host.server_code, 1)
            mc_host.status = 0
            mc_host.save()
            return HttpResponse(u"未部署agent或agent工作异常,部署失败")
        
        

            
            
            
                
        
        
                
            










