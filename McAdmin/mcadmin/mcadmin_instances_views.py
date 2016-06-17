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

class InstanceQueryView(SingleObjectMixin, ListView):

    form_class = InstanceQueryForm
    paginate_by = 20
    template_name = "mcadmin/instance_display.html"
    model = MemcacheInstance
    request = None
    
    def post(self, request, *args, **kwargs):
        self.request = request
        self.object = self.get_queryset()
        return super(InstanceQueryView, self).get(request, *args, **kwargs)
    
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
        return super(InstanceQueryView, self).get(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super(InstanceQueryView, self).get_context_data(**kwargs)
        csrf_token = csrf(self.request)
        context.update(csrf_token)
        form = self.form_class()
        context.update({'form': form })
        return context
        
    def get_queryset(self):
        queryset = None     
        if self.request.method == 'GET':
            if self.request.GET.has_key('subsystem_code'):
                print 1
                queryset = self.model.object.filter(group__group_code=self.request.GET['subsystem_code'])
                return queryset
            else:
                print 2
                return None
        if self.request.method == 'POST':
            queryset = self.model.all()
            if self.request.POST.has_key('instance_code') != u'':
                legal_input = 0
                try:
                    instance_codes = [int(code) for code in self.request.POST['instance_code'].split()]
                except ValueError:
                    legal_input = 1
                if legal_input == 0:
                    queryset = queryset.filter(instance_code__in=instance_codes)
            if self.request.POST['host'] != u'':
                legal_input = 0
                try:
                    hosts = [host for host in self.request.POST['host'].split()]
                except ValueError:
                    legal_input = 1
                if legal_input == 0:
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
    
    
class InstanceCreateView(View):
    form_class = InstanceCreateForm
    template_name = 'mcadmin/instance_create.html'
    
    def get(self, request, *args, **kwargs):
        c = {}
        c.update(csrf(request))
        form = self.form_class()
        c.update({'form': form })
        return render_to_response(self.template_name, context_instance=RequestContext(request, c))
    
    def post(self, request, *args, **kwargs):
        group_code = request.POST["group_code"]
        interip = request.POST["interip"]
        port = request.POST["port"]
        max_memory = request.POST["max_memory"]
        max_connection = request.POST["max_connection"]
        is_bind = request.POST["is_bind"]
        tech_admin = request.POST["tech_admin"]
        sysop_admin = request.POST["sysop_admin"]
        description = request.POST["description"]
        try:
            mc_group = MemcacheGroup.object.get(group_code=group_code)
            mc_host = MemcacheHost.object.get(interip=interip)
        except MemcacheGroup.DoesNotExist:
            return HttpResponse(u"实例组不存在.")
        except MemcacheHost.DoesNotExist:
            return HttpResponse(u"宿主机不存在.")
        is_exist = 0
        try:
            instance_del = MemcacheInstance.object.get(host=mc_host, port=port)
            if instance_del.status == 5:
                instance_code = instance_del.instance_code
                is_exist = 1
            else:
                return HttpResponse(u"无法添加实例，实例" + interip + u":" + str(port) + u"已存在.")
        except MemcacheInstance.DoesNotExist:
            try:
                instance_code = MemcacheInstance.object.latest('instance_code').instance_code
                instance_code += 1
            except:
                return HttpResponse(u"无法获取实例ID.")
        try:
            if is_exist == 1:
                mc_instance = MemcacheInstance.object.get(instance_code=instance_code)
                mc_instance.status = 0
            else:
                mc_instance = MemcacheInstance(instance_code=instance_code, host=mc_host, group = mc_group,
                                               port=port, max_memory=max_memory, max_connection=max_connection, is_bind=is_bind,
                                               tech_admin=tech_admin, sysop_admin=sysop_admin, creator=u'dw_lijie1', status=0,
                                               description=description)
            mc_instance.save()
            instance_fsm = MemcacheInstanceFSM()
            instance_fsm.add_by_model(mc_instance)
        except:
            return HttpResponse(u"无法创建memcache实例.")
        if instance_fsm.cheage_status_to(mc_instance.instance_code, 1):
            mc_instance.status = 1
            mc_instance.save()
        try:
            agent_info = MemcacheAgent.object.get(idc_code=mc_instance.host.idc_code)
        except MemcacheAgent.DoesNotExist:
            if instance_fsm.cheage_status_to(mc_instance.instance_code, 0):
                mc_instance.status = 0
                mc_instance.save()
            return HttpResponse(u"未部署agent或agent工作异常,部署失败")
        if is_bind:
            is_bind = '1'
        else:
            is_bind = '0'
        request_data = {'host':mc_instance.host.interip,
                        'port':port, 'max_memory':max_memory,
                        'max_connection':max_connection, 'is_bind':is_bind}
        request_url = 'httk://' + agent_info.bind_host + ':' + agent_info.bind_port
        request_application = 'mcadmin'
        request_controller = 'memcache_instance'
        try:
            do_create_mamcacheinstance = restful.create(request_url, request_application, request_controller, data=request_data)
        except:
            if instance_fsm.cheage_status_to(mc_instance.instance_code, 0):
                mc_instance.status = 0
                mc_instance.save()
            return HttpResponse(u"创建memcache实例配置失败")
        rs = json.loads(do_create_mamcacheinstance)
        failures = rs.get('stdout', {}).get(interip, {}).get('failures', None)
        unreachable = rs.get('stdout', {}).get(interip, {}).get('unreachable', None)
        if failures != 0 or unreachable != 0:
            if instance_fsm.cheage_status_to(mc_instance.instance_code, 0):
                instance_fsm.status = 0
                instance_fsm.save()
            return HttpResponse(u"创建memcache实例过程发现错误")
        if instance_fsm.cheage_status_to(mc_instance.instance_code, 2):
            instance_fsm.status = 2
            instance_fsm.save()
        else:
            return HttpResponse(u"Memcached实例" + str(interip) + ':' + str(port) + u"切换为Ready状态失败.")
        request_controller = "memcache_instance_manage_single"
        request_id = str(mc_instance.instance_code)
        request_data = {'host':interip, 'port':port, 'operation':'start'}
        try:
            do_start_mamcacheinstance = restful.update(request_url, request_application, request_controller, request_id, data=request_data)
        except:
            return HttpResponse(u"memcache实例启动失败")
        rs = json.loads(do_start_mamcacheinstance)
        failures = rs.get('stdout', {}).get(interip, {}).get('failures', None)
        unreachable = rs.get('stdout', {}).get(interip, {}).get('unreachable', None)
        if failures != 0 or unreachable != 0:
            return HttpResponse(u"memcache实例启动失败")
        if not instance_fsm.cheage_status_to(mc_instance.instance_code, 3):
            return HttpResponse(u"memcache实例启动失败")   
        instance_fsm.status = 3
        instance_fsm.save()
        return HttpResponse(u"memcache实例创建完成，启动成功")
        

class InstanceStopView(View):
    
    def get(self, request, *args, **kwargs):
        instance_code = request.GET["instance_code"]
        if not instance_code:
            return HttpResponse(u"memcache实例不存在")
        try:
            instance_code = int(instance_code)
        except:
            return HttpResponse(u"非法输入")
        try:
            mc_instance = MemcacheInstance.object.get(instance_code=instance_code)
        except MemcacheInstance.DoesNotExist:
            return HttpResponse(u"memcache实例不存在")
        if mc_instance.status != 3:
            return HttpResponse(u"memcache实例不是运行状态 ，实例停止失败")
        instance_fsm = MemcacheInstanceFSM()
        instance_fsm.add_by_model(mc_instance)
        if instance_fsm.cheage_status_to(mc_instance.instance_code, 6):
            instance_fsm.status = 6
            try:
                agent_info = MemcacheAgent.object.get(idc_code=mc_instance.host.idc_code)
            except MemcacheAgent.DoesNotExist:
                return HttpResponse(u"未部署agent或agent工作异常,部署失败")
            request_url = 'httk://' + agent_info.bind_host + ':' + agent_info.bind_port
            request_application = 'mcadmin'
            request_controller = "memcache_instance_manage_single"
            request_id = str(mc_instance.instance_code)
            interip = mc_instance.host.interip
            port = mc_instance.port
            request_data = {'host':interip, 'port':port, 'operation':'stop'}
            try:
                do_stop_mamcacheinstance = restful.update(request_url, request_application, request_controller, request_id, data=request_data)
            except:
                return HttpResponse(u"memcache实例停止失败")
            rs = json.loads(do_stop_mamcacheinstance)
            failures = rs.get('stdout', {}).get(interip, {}).get('failures', None)
            unreachable = rs.get('stdout', {}).get(interip, {}).get('unreachable', None)
            if failures != 0 or unreachable != 0:
                return HttpResponse(u"memcache实例停止失败")   
            instance_fsm.save()
            return HttpResponse(u"memcache实例已停止")
        else:
            return HttpResponse(u"无法停止memcache实例")
        

class InstanceStartView(View):
    
    def get(self, request, *args, **kwargs):
        instance_code = request.GET["instance_code"]
        if not instance_code:
            return HttpResponse(u"memcache实例不存在")
        try:
            instance_code = int(instance_code)
        except:
            return HttpResponse(u"非法输入")
        try:
            mc_instance = MemcacheInstance.object.get(instance_code=instance_code)
        except MemcacheInstance.DoesNotExist:
            return HttpResponse(u"memcache实例不存在")
        if mc_instance.status != 6 and mc_instance.status != 2:
            return HttpResponse(u"memcache实例不是运行状态 ，实例停止失败")
        instance_fsm = MemcacheInstanceFSM()
        instance_fsm.add_by_model(mc_instance)
        if instance_fsm.cheage_status_to(mc_instance.instance_code, 3):
            instance_fsm.status = 3
            try:
                agent_info = MemcacheAgent.object.get(idc_code=mc_instance.host.idc_code)
            except MemcacheAgent.DoesNotExist:
                return HttpResponse(u"未部署agent或agent工作异常,部署失败")
            request_url = 'httk://' + agent_info.bind_host + ':' + agent_info.bind_port
            request_application = 'mcadmin'
            request_controller = "memcache_instance_manage_single"
            request_id = str(mc_instance.instance_code)
            interip = mc_instance.host.interip
            port = mc_instance.port
            request_data = {'host':interip, 'port':port, 'operation':'start'}
            try:
                do_start_mamcacheinstance = restful.update(request_url, request_application, request_controller, request_id, data=request_data)
            except:
                return HttpResponse(u"memcache实例启动失败")
            rs = json.loads(do_start_mamcacheinstance)
            failures = rs.get('stdout', {}).get(interip, {}).get('failures', None)
            unreachable = rs.get('stdout', {}).get(interip, {}).get('unreachable', None)
            if failures != 0 or unreachable != 0:
                return HttpResponse(u"memcache实例启动失败") 
            instance_fsm.save()
            return HttpResponse(u"memcache实例已停止")
        else:
            return HttpResponse(u"无法停止memcache实例")


class InstanceDeleteView(View):

    def post(self, request, *args, **kwargs):
        instance_code = request.POST["instance_code"]
        if not instance_code:
            return HttpResponse(u"memcache实例不存在")
        try:
            instance_code = int(instance_code)
        except:
            return HttpResponse(u"非法输入")
        try:
            mc_instance = MemcacheInstance.object.get(instance_code=instance_code)
        except MemcacheInstance.DoesNotExist:
            return HttpResponse(u"memcache实例不存在")
        if mc_instance.status != 2:
            return HttpResponse(u"无法删除实例,实例必须处于下线状态")
        try:
            agent_info = MemcacheAgent.object.get(idc_code=mc_instance.host.idc_code)
        except MemcacheAgent.DoesNotExist:
            return HttpResponse(u"未部署agent或agent工作异常,部署失败")
        instance_fsm = MemcacheInstanceFSM()
        instance_fsm.add_by_model(mc_instance)
        if instance_fsm.cheage_status_to(mc_instance.instance_code, 4):
            instance_fsm.status = 4
            instance_fsm.save()
        request_url = 'httk://' + agent_info.bind_host + ':' + agent_info.bind_port
        request_application = 'mcadmin'
        request_controller = "memcache_instance"
        request_id = str(mc_instance.instance_code)
        interip = mc_instance.host.interip
        port = mc_instance.port
        request_data = {'host':interip, 'port':port}
        try:
            do_del_mamcacheinstance = restful.show(request_url, request_application, request_controller, request_id, data=request_data)
        except:
            return HttpResponse(u"memcache实例删除失败")
        rs = json.loads(do_del_mamcacheinstance)
        failures = rs.get('stdout', {}).get(interip, {}).get('failures', None)
        unreachable = rs.get('stdout', {}).get(interip, {}).get('unreachable', None)
        if failures != 0 or unreachable != 0:
            return HttpResponse(u"memcache实例停止失败")
        if instance_fsm.cheage_status_to(mc_instance.instance_code, 5):
            instance_fsm.status = 5
            instance_fsm.save()
            return HttpResponse(u"memcache实例删除成功")
        else:
            return HttpResponse(u"memcache实例删除失败")
        















   