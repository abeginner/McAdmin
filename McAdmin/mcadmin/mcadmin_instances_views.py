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

from McAdmin.mcadmin.mcadmin_forms import *
from McAdmin.mcadmin.models import *
from McAdmin.mcadmin.backends import CmdbBackend
from McAdmin.mcadmin.fsms import *

from contrib import restful
from contrib import RegEx

class InstanceQueryView(SingleObjectMixin, ListView):

    paginate_by = 30
    form_class = InstanceQueryForm
    template_name = "mcadmin/instance_display.html"
    model = MemcacheInstance
    query_list = {}
    request = None
    
    def get(self, request, *args, **kwargs):
        self.request = request
        if request.GET.has_key('group_code') or request.GET.has_key('hosts'):
            self.query_list['group_code'] = request.GET.get("group_code", u'')
            self.query_list['hosts'] = request.GET.get("hosts", u'')
            self.object = self.get_queryset()
            return super(InstanceQueryView, self).get(request, *args, **kwargs)
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
    
    def post(self, request, *args, **kwargs):
        self.request = request
        self.query_list = self.request.POST            
        self.object = self.get_queryset()
        if self.request.POST.has_key('page'):
            self.kwargs['page'] = self.request.POST['page'][0]
        return super(InstanceQueryView, self).get(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super(InstanceQueryView, self).get_context_data(**kwargs)
        csrf_token = csrf(self.request)      
        context.update(csrf_token)
        form = self.form_class(initial=self.query_list)
        context.update({'form': form })
        return context
        
    def get_queryset(self):
        queryset = self.model.object.exclude(status=5)
        if self.query_list.has_key('bussiness_code') and self.query_list['bussiness_code'] != u'':
            bussiness_code_list = []
            for i in self.query_list['bussiness_code'].split():
                try:
                    bussiness_code_list.append(int(i))
                except:
                    pass
            queryset = queryset.filter(group__subsystem__bussiness__bussiness_code__in=bussiness_code_list)
        if self.query_list.has_key('bussiness_shortname') and self.query_list['bussiness_shortname'] != u'':
            bussiness_shortname_list = self.query_list['bussiness_shortname'].split()
            queryset = queryset.filter(group__subsystem__bussiness__bussiness_shortname__in=bussiness_shortname_list)
        if self.query_list.has_key('bussiness_fullname') and self.query_list['bussiness_fullname'] != u'':
            bussiness_fullname_list = self.query_list['bussiness_fullname'].split()
            queryset = queryset.filter(group__subsystem__bussiness__bussiness_fullname__in=bussiness_fullname_list)
        if self.query_list.has_key('subsystem_code') and self.query_list['subsystem_code'] != u'':
            subsystem_code_list = []
            for i in self.query_list['subsystem_code'].split():
                try:
                    subsystem_code_list.append(int(i))
                except:
                    pass
            queryset = queryset.filter(group__subsystem__subsystem_code__in=subsystem_code_list)
        if self.query_list.has_key('subsystem_fullname') and self.query_list['subsystem_fullname'] != u'':
            subsystem_fullname_list = self.query_list['subsystem_fullname'].split()
            queryset = queryset.filter(group__subsystem__subsystem_fullname__in=subsystem_fullname_list)
        if self.query_list.has_key('group_code') and self.query_list['group_code'] != u'':
            group_code_list = []
            for i in self.query_list['group_code'].split():
                try:
                    group_code_list.append(int(i))
                except:
                    pass
            queryset = queryset.filter(group__group_code__in=group_code_list)
        if self.query_list.has_key('group_name') and self.query_list['group_name'] != u'':
            group_name_list = self.query_list['group_name'].split()
            queryset = queryset.filter(group__group_name__in=group_name_list)
        if self.query_list.has_key('instance_code') and self.query_list['instance_code'] != u'':
            instance_code_list = []
            for i in self.query_list['instance_code'].split():
                try:
                    instance_code_list.append(int(i))
                except:
                    pass
            queryset = queryset.filter(instance_code__in=instance_code_list)      
        if self.query_list.has_key('hosts') and self.query_list['hosts'] != u'':
            hosts_list = self.query_list['hosts'].split()
            queryset = queryset.filter(host__interip__in=hosts_list)
        if self.query_list.has_key('port') and self.query_list['port'] != u'':
            try:
                port = int(self.query_list['port'])
                queryset = queryset.filter(port=port)
            except:
                pass
        if self.query_list.has_key('sysop_admin') and self.query_list['sysop_admin'] != u'':
            queryset = queryset.filter(sysop_admin=self.query_list['sysop_admin'])
        if self.query_list.has_key('tech_admin') and self.query_list['tech_admin'] != u'':
            queryset = queryset.filter(tech_admin=self.query_list['tech_admin'])
        return queryset  
    
class InstanceCreateView(View):
    form_class = InstanceCreateForm
    template_name = 'mcadmin/instance_create.html'
    
    def get(self, request, *args, **kwargs):
        c = {}
        c.update(csrf(request))
        if request.GET.has_key("group_code") and request.GET.has_key("subsystem_fullname") and \
        request.GET.has_key("group_name") and request.GET.has_key("bussiness_fullname"):
            message = u'实例组:' + request.GET["bussiness_fullname"] + u'->' + request.GET["subsystem_fullname"] \
            + u'->' + request.GET["group_name"]
            group_code = request.GET["group_code"]
            c.update({'message': message })
            c.update({'group_code': group_code })
            form = self.form_class()
            c.update({'form': form })
            return render_to_response(self.template_name, context_instance=RequestContext(request, c))
        else:
            return HttpResponseRedirect("/mcadmin/group/display?msg_type=warning&msg=缺少参数组id")
    
    def post(self, request, *args, **kwargs):
        if request.POST.has_key("group_code") and request.POST.has_key("interip") and request.POST.has_key("port") \
        and request.POST.has_key("max_memory") and request.POST.has_key("max_connection") \
        and request.POST.has_key("tech_admin") and request.POST.has_key("sysop_admin") and request.POST.has_key("description"):
            group_code = request.POST["group_code"]
            interip = request.POST["interip"]
            port = request.POST["port"]
            max_memory = request.POST["max_memory"]
            max_connection = request.POST["max_connection"]
            tech_admin = request.POST["tech_admin"]
            sysop_admin = request.POST["sysop_admin"]
            description = request.POST["description"]
        else:
            return HttpResponseRedirect("/mcadmin/group/display?msg_type=warning&msg=缺少参数组")
        if request.POST.has_key("is_bind"):
            is_bind = '1'
        else:
            is_bind = '0'
        try:
            mc_group = MemcacheGroup.object.get(group_code=group_code)
            mc_host = MemcacheHost.object.get(interip=interip)
        except MemcacheGroup.DoesNotExist:
            return HttpResponseRedirect("/mcadmin/group/display?msg_type=warning&msg=实例组不存在")
        except MemcacheHost.DoesNotExist:
            return HttpResponseRedirect("/mcadmin/group/display?msg_type=warning&msg=宿主机不存在")
        is_exist = 0
        try:
            instance_del = MemcacheInstance.object.get(host=mc_host, port=port)
            if instance_del.status == 5 or instance_del.status == 0:
                is_exist = 1
            else:
                return HttpResponseRedirect("/mcadmin/group/display?msg_type=warning&msg=无法添加实例，实例" \
                                            + interip.encode("utf-8") + ":" + str(port) + "已存在")
        except MemcacheInstance.DoesNotExist:
            try:
                instance_code = MemcacheInstance.object.latest('instance_code').instance_code
                instance_code += 1
            except MemcacheInstance.DoesNotExist:
                instance_code = 10000
            except:
                return HttpResponseRedirect("/mcadmin/group/display?msg_type=warning&msg=无法获取实例ID")
        except:
            return HttpResponseRedirect("/mcadmin/group/display?msg_type=warning&msg=发生未知错误")
        try:
            if is_exist == 1:
                mc_instance = instance_del
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
            return HttpResponseRedirect("/mcadmin/group/display?msg_type=warning&msg=无法创建memcache实例.")
        if instance_fsm.cheage_status_to(mc_instance.instance_code, 1):
            mc_instance.status = 1
            mc_instance.save()
        try:
            agent_info = MemcacheAgent.object.get(idc_code=mc_instance.host.idc_code)
        except MemcacheAgent.DoesNotExist:
            if instance_fsm.cheage_status_to(mc_instance.instance_code, 0):
                mc_instance.status = 0
                mc_instance.save()
            return HttpResponseRedirect("/mcadmin/group/display?msg_type=warning&msg=未部署agent或agent工作异常,部署失败")
        request_data = {'host':mc_instance.host.interip,
                        'port':port, 'max_memory':max_memory,
                        'max_connection':max_connection, 'is_bind':is_bind}
        print request_data
        request_url = 'http://' + agent_info.bind_host + ':' + str(agent_info.bind_port)
        request_application = 'mcadmin'
        request_controller = 'memcache_instance'
        try:
            do_create_mamcacheinstance = restful.create(request_url, request_application, request_controller, data=request_data)
        except Exception, e:
            if instance_fsm.cheage_status_to(mc_instance.instance_code, 0):
                mc_instance.status = 0
                mc_instance.save()
            return HttpResponseRedirect("/mcadmin/group/display?msg_type=warning&msg=创建memcache实例配置失败")
        if do_create_mamcacheinstance.status_code == 200:
            rs = do_create_mamcacheinstance.json()
        else:
            return HttpResponseRedirect("/mcadmin/group/display?msg_type=warning&msg=响应码:" + str(do_create_mamcacheinstance.status_code) \
                                        + "响应内容" + str(do_create_mamcacheinstance.text))
        failures = rs.get('stdout', {}).get(interip, {}).get('failures', None)
        unreachable = rs.get('stdout', {}).get(interip, {}).get('unreachable', None)
        if failures != 0 or unreachable != 0:
            if instance_fsm.cheage_status_to(mc_instance.instance_code, 0):
                mc_instance.status = 0
                mc_instance.save()
            return HttpResponse(u"创建memcache实例过程发现错误")
        if instance_fsm.cheage_status_to(mc_instance.instance_code, 2):
            mc_instance.status = 2
            mc_instance.save()
        else:
            return HttpResponse(u"Memcached实例" + str(interip) + ':' + str(port) + u"切换为Ready状态失败.")
        request_controller = "memcache_instance_manage_single"
        request_id = str(mc_instance.instance_code)
        request_data = {'host':interip, 'port':port, 'operation':'start'}
        try:
            do_start_mamcacheinstance = restful.update(request_url, request_application, request_controller, request_id, data=request_data)
        except:
            return HttpResponse(u"memcache实例启动失败")
        if do_create_mamcacheinstance.status_code == 200:
            rs = do_create_mamcacheinstance.json()
        else:
            return HttpResponseRedirect("/mcadmin/group/display?msg_type=warning&msg=响应码:" + str(do_create_mamcacheinstance.status_code) \
                                        + "响应内容" + str(do_create_mamcacheinstance.text))
        failures = rs.get('stdout', {}).get(interip, {}).get('failures', None)
        unreachable = rs.get('stdout', {}).get(interip, {}).get('unreachable', None)
        if failures != 0 or unreachable != 0:
            return HttpResponseRedirect("/mcadmin/group/display?msg_type=danger&msg=实例启动失败")
        if not instance_fsm.cheage_status_to(mc_instance.instance_code, 3):
            return HttpResponseRedirect("/mcadmin/group/display?msg_type=danger&msg=实例启动失败")   
        mc_instance.status = 3
        mc_instance.save()
        return HttpResponseRedirect("/mcadmin/group/display?msg_type=success&msg=实例创建完成，启动成功")
    
    
class InstanceDeleteView(View):

    def post(self, request, *args, **kwargs):
        instance_code = request.POST.get("instance_code", None)
        if not instance_code or instance_code == u"":
            return HttpResponseRedirect("/mcadmin/instance/display?msg_type=warning&msg=实例不存在")
        try:
            instance_code = int(instance_code)
        except:
            return HttpResponseRedirect("/mcadmin/instance/display?msg_type=warning&msg=实例id必须为整数")
        try:
            mc_instance = MemcacheInstance.object.get(instance_code=instance_code)
        except MemcacheInstance.DoesNotExist:
            return HttpResponseRedirect("/mcadmin/instance/display?msg_type=warning&msg=实例不存在")
        if mc_instance.status == 3:
            return HttpResponseRedirect("/mcadmin/instance/display?msg_type=warning&msg=无法删除运行中实例")
        try:
            agent_info = MemcacheAgent.object.get(idc_code=mc_instance.host.idc_code)
        except MemcacheAgent.DoesNotExist:
            return HttpResponseRedirect("/mcadmin/group/display?msg_type=danger&msg=未部署agent或agent工作异常,部署失败")
        instance_fsm = MemcacheInstanceFSM()
        instance_fsm.add_by_model(mc_instance)
        if instance_fsm.cheage_status_to(mc_instance.instance_code, 4):
            mc_instance.status = 4
            mc_instance.save()
        request_url = 'http://' + agent_info.bind_host + ':' + str(agent_info.bind_port)
        request_application = 'mcadmin'
        request_controller = "memcache_instance"
        request_id = str(mc_instance.instance_code)
        interip = mc_instance.host.interip
        port = mc_instance.port
        request_data = {'host':interip, 'port':port}
        try:
            do_del_mamcacheinstance = restful.show(request_url, request_application, request_controller, request_id, params=request_data)
        except Exception, e:
            raise e
            return HttpResponseRedirect("/mcadmin/instance/display?msg_type=danger&msg=memcache实例删除失败")
        if do_del_mamcacheinstance.status_code == 200:
            rs = do_del_mamcacheinstance.json()
        else:
            return HttpResponseRedirect("/mcadmin/instance/display?msg_type=warning&msg=响应码:" + str(do_del_mamcacheinstance.status_code) \
                                        + "响应内容" + str(do_del_mamcacheinstance.text))
        failures = rs.get('stdout', {}).get(interip, {}).get('failures', None)
        unreachable = rs.get('stdout', {}).get(interip, {}).get('unreachable', None)
        if failures != 0 or unreachable != 0:
            return HttpResponseRedirect("/mcadmin/instance/display?msg_type=warning&msg=实例删除失败")
        if instance_fsm.cheage_status_to(mc_instance.instance_code, 5):
            mc_instance.status = 5
            mc_instance.save()
            return HttpResponseRedirect("/mcadmin/instance/display?msg_type=success&msg=实例删除成功")
        else:
            return HttpResponseRedirect("/mcadmin/instance/display?msg_type=warning&msg=实例删除失败")
        

class InstanceStopView(View):
    
    def post(self, request, *args, **kwargs):
        instance_code = request.POST.get("instance_code", None)
        if not instance_code:
            return HttpResponseRedirect("/mcadmin/instance/display?msg_type=warning&msg=实例不存在")
        try:
            instance_code = int(instance_code)
        except:
            return HttpResponseRedirect("/mcadmin/instance/display?msg_type=warning&msg=非法输入")
        try:
            mc_instance = MemcacheInstance.object.get(instance_code=instance_code)
        except MemcacheInstance.DoesNotExist:
            return HttpResponseRedirect("/mcadmin/instance/display?msg_type=warning&msg=实例不存在")
        if mc_instance.status != 3:
            return HttpResponseRedirect("/mcadmin/instance/display?msg_type=warning&msg=实例不是运行状态 ，实例停止失败")
        instance_fsm = MemcacheInstanceFSM()
        instance_fsm.add_by_model(mc_instance)
        if instance_fsm.cheage_status_to(mc_instance.instance_code, 2):
            try:
                agent_info = MemcacheAgent.object.get(idc_code=mc_instance.host.idc_code)
            except MemcacheAgent.DoesNotExist:
                return HttpResponseRedirect("/mcadmin/instance/display?msg_type=warning&msg=未部署agent或agent工作异常,部署失败")
            request_url = 'http://' + agent_info.bind_host + ':' + str(agent_info.bind_port)
            request_application = 'mcadmin'
            request_controller = "memcache_instance_manage_single"
            request_id = str(mc_instance.instance_code)
            interip = mc_instance.host.interip
            port = mc_instance.port
            request_data = {'host':interip, 'port':port, 'operation':'stop'}
            try:
                do_stop_mamcacheinstance = restful.update(request_url, request_application, request_controller, request_id, data=request_data)
            except:
                return HttpResponseRedirect("/mcadmin/instance/display?msg_type=danger&msg=实例停止失败")
            if do_stop_mamcacheinstance.status_code == 200:
                rs = do_stop_mamcacheinstance.json()
            else:
                return HttpResponseRedirect("/mcadmin/instance/display?msg_type=warning&msg=响应码:" + str(do_stop_mamcacheinstance.status_code) \
                                        + "响应内容" + str(do_stop_mamcacheinstance.text))
            failures = rs.get('stdout', {}).get(interip, {}).get('failures', None)
            unreachable = rs.get('stdout', {}).get(interip, {}).get('unreachable', None)
            if failures != 0 or unreachable != 0:
                return HttpResponseRedirect("/mcadmin/instance/display?msg_type=warning&msg=实例停止失败")
            mc_instance.status = 2 
            mc_instance.save()
            return HttpResponseRedirect("/mcadmin/instance/display?msg_type=success&msg=实例已停止")
        else:
            return HttpResponseRedirect("/mcadmin/instance/display?msg_type=warning&msg=无法停止实例")
        

class InstanceStartView(View):
    
    def post(self, request, *args, **kwargs):
        instance_code = request.POST.get("instance_code", None)
        if not instance_code:
            return HttpResponseRedirect("/mcadmin/instance/display?msg_type=warning&msg=实例不存在")
        try:
            instance_code = int(instance_code)
        except:
            return HttpResponseRedirect("/mcadmin/instance/display?msg_type=warning&msg=非法输入")
        try:
            mc_instance = MemcacheInstance.object.get(instance_code=instance_code)
        except MemcacheInstance.DoesNotExist:
            return HttpResponseRedirect("/mcadmin/instance/display?msg_type=warning&msg=实例不存在")
        if mc_instance.status != 2:
            return HttpResponseRedirect("/mcadmin/instance/display?msg_type=warning&msg=实例不是准备状态 ，实例启动失败")
        instance_fsm = MemcacheInstanceFSM()
        instance_fsm.add_by_model(mc_instance)
        if instance_fsm.cheage_status_to(mc_instance.instance_code, 3):
            try:
                agent_info = MemcacheAgent.object.get(idc_code=mc_instance.host.idc_code)
            except MemcacheAgent.DoesNotExist:
                return HttpResponseRedirect("/mcadmin/instance/display?msg_type=warning&msg=未部署agent或agent工作异常,部署失败")
            request_url = 'http://' + agent_info.bind_host + ':' + str(agent_info.bind_port)
            request_application = 'mcadmin'
            request_controller = "memcache_instance_manage_single"
            request_id = str(mc_instance.instance_code)
            interip = mc_instance.host.interip
            port = mc_instance.port
            request_data = {'host':interip, 'port':port, 'operation':'start'}
            try:
                do_stop_mamcacheinstance = restful.update(request_url, request_application, request_controller, request_id, data=request_data)
            except:
                return HttpResponseRedirect("/mcadmin/instance/display?msg_type=danger&msg=实例启动失败")
            if do_stop_mamcacheinstance.status_code == 200:
                rs = do_stop_mamcacheinstance.json()
            else:
                return HttpResponseRedirect("/mcadmin/instance/display?msg_type=warning&msg=响应码:" + str(do_stop_mamcacheinstance.status_code) \
                                        + "响应内容" + str(do_stop_mamcacheinstance.text))
            failures = rs.get('stdout', {}).get(interip, {}).get('failures', None)
            unreachable = rs.get('stdout', {}).get(interip, {}).get('unreachable', None)
            if failures != 0 or unreachable != 0:
                return HttpResponseRedirect("/mcadmin/instance/display?msg_type=warning&msg=实例启动失败")
            mc_instance.status = 3
            mc_instance.save()
            return HttpResponseRedirect("/mcadmin/instance/display?msg_type=success&msg=实例已启动")
        else:
            return HttpResponseRedirect("/mcadmin/instance/display?msg_type=warning&msg=无法启动实例")


class InstanceUpdateView(View):
    form_class = InstanceUpdateForm
    template_name = 'mcadmin/instance_update.html'
        
    def get(self, request, *args, **kwargs):
        c = {}
        c.update(csrf(request))
        if request.GET.has_key("instance_code"):
            try:
                instance_code = long(request.GET['instance_code'])
            except:
                return HttpResponse(u"实例id只能为数字")  
            try:
                mc_instance = MemcacheInstance.object.get(instance_code=instance_code)
            except:
                return HttpResponse(u"实例不存在")
            if mc_instance.status != 2:
                return HttpResponse(u"只允许修改准备中状态的实例")
            message = u'[' + mc_instance.group.group_name + u']' + mc_instance.host.interip + ':' \
            + str(mc_instance.port)
            data = {'max_memory':mc_instance.max_memory, 'max_connection':mc_instance.max_connection, \
                    'max_connection':mc_instance.max_connection, 'is_bind':mc_instance.is_bind, \
                    'tech_admin':mc_instance.tech_admin, 'sysop_admin':mc_instance.sysop_admin, \
                    'description':mc_instance.description}
            c = {}
            c.update(csrf(request))
            c.update({'message': message })
            c.update({'instance_code':instance_code })
            form = self.form_class(initial=data)
            c.update({'form': form })
            return render_to_response(self.template_name, context_instance=RequestContext(request, c))
        else:
            return HttpResponse(u"缺少参数组id")

    def post(self, request, *args, **kwargs):
        if request.POST.has_key("max_memory") and request.POST.has_key("max_connection") and request.POST.has_key("is_bind")\
        and request.POST.has_key("tech_admin") and request.POST.has_key("sysop_admin") and request.POST.has_key("description") \
        and request.POST.has_key("instance_code"):
            instance_code = request.POST["instance_code"]
            max_memory = request.POST["max_memory"]
            is_bind = request.POST["is_bind"]
            max_connection = request.POST["max_connection"]
            tech_admin = request.POST["tech_admin"]
            sysop_admin = request.POST["sysop_admin"]
            description = request.POST["description"]
        else:
            return HttpResponseRedirect("/mcadmin/group/display?msg_type=warning&msg=缺少参数组")
        try:
            mc_instance = MemcacheInstance.object.get(instance_code=instance_code)
        except MemcacheInstance.DoesNotExist:
            return HttpResponseRedirect("/mcadmin/instance/display?msg_type=warning&msg=实例不存在")
        if mc_instance.status != 2:
            return HttpResponseRedirect("/mcadmin/instance/display?msg_type=warning&msg=只能更改准备中状态的实例")
        if mc_instance.max_memory != max_memory or mc_instance.is_bind != is_bind or mc_instance.max_connection != max_connection:
            
            mc_instance.max_memory = max_memory
            mc_instance.is_bind = is_bind
            mc_instance.max_connection = max_connection
            port = mc_instance.port
            interip = mc_instance.host.interip
            try:
                agent_info = MemcacheAgent.object.get(idc_code=mc_instance.host.idc_code)
            except MemcacheAgent.DoesNotExist:
                return HttpResponseRedirect("/mcadmin/group/display?msg_type=warning&msg=未部署agent或agent工作异常,部署失败")
            request_data = {'host':mc_instance.host.interip,
                        'port':port, 'max_memory':max_memory,
                        'max_connection':max_connection, 'is_bind':is_bind}
            print request_data
            request_url = 'http://' + agent_info.bind_host + ':' + str(agent_info.bind_port)
            request_application = 'mcadmin'
            request_controller = 'memcache_instance'
            try:
                do_create_mamcacheinstance = restful.create(request_url, request_application, request_controller, data=request_data)
            except Exception, e:
                return HttpResponseRedirect("/mcadmin/group/display?msg_type=warning&msg=创建memcache实例配置失败")
            if do_create_mamcacheinstance.status_code == 200:
                rs = do_create_mamcacheinstance.json()
            else:
                return HttpResponseRedirect("/mcadmin/group/display?msg_type=warning&msg=响应码:" + str(do_create_mamcacheinstance.status_code) \
                                        + "响应内容" + str(do_create_mamcacheinstance.text))
            failures = rs.get('stdout', {}).get(interip, {}).get('failures', None)
            unreachable = rs.get('stdout', {}).get(interip, {}).get('unreachable', None)
            if failures != 0 or unreachable != 0:
                return HttpResponseRedirect("/mcadmin/group/display?msg_type=danger&msg=实例配置更改失败")
        if mc_instance.tech_admin != tech_admin or mc_instance.sysop_admin != sysop_admin or \
        mc_instance.description != description:
            mc_instance.tech_admin = tech_admin
            mc_instance.sysop_admin = sysop_admin
            mc_instance.description = description
        mc_instance.save()
        return HttpResponseRedirect("/mcadmin/group/display?msg_type=success&msg=实例配置更改成功")




   