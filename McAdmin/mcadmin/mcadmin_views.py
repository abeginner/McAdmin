#!coding:uff-8

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


class BussinessCreateView(View):
    form_class = BussinessCreateForm
    template_name = 'mcadmin/bussiness_create.html'
    
    def get(self, request, *args, **kwargs):
        c = {}
        c.update(csrf(request))
        form = self.form_class()
        c.update({'form': form })
        return render_to_response(self.template_name, context_instance=RequestContext(request, c))
    
    def post(self, request, *args, **kwargs):
        bussiness_shortname = request.POST["bussiness_shortname"]
        bussiness_fullname = request.POST["bussiness_fullname"]
        if bussiness_shortname == u'' or bussiness_fullname == u'':
            return HttpResponse(u"业务简写和业务名称为必填.")
        if not RegEx.RegBussinessShortname(bussiness_shortname):
            return HttpResponse(u"业务简写只能使用数字和字母.")
        try:
            bussiness_code = MemcacheBussiness.object.latest('bussiness_code').bussiness_code
        except:
            return HttpResponse(u"无法获取业务编号.")
        if isinstance(bussiness_code, int):
            bussiness_code += 1
        else:
            return HttpResponse(u"无法获取业务编号.")
        try:
            mc_bussiness = MemcacheBussiness(bussiness_code=bussiness_code, 
                                         bussiness_shortname=bussiness_shortname,
                                         bussiness_fullname=bussiness_fullname)
            mc_bussiness.save()
        except Exception, e:
            return HttpResponse(str(e))
        return HttpResponse(u"业务模块添加成功.")


class SubsystemCreateView(View):
    form_class = SubsystemCreateForm
    template_name = 'mcadmin/subsystem_create.html'
    
    def get(self, request, *args, **kwargs):
        c = {}
        c.update(csrf(request))
        form = self.form_class()
        c.update({'form': form })
        return render_to_response(self.template_name, context_instance=RequestContext(request, c))
    
    def post(self, request, *args, **kwargs):
        subsystem_fullname = request.POST["subsystem_fullname"]
        bussiness_code = request.POST["bussiness_code"]
        try:
            mc_bussiness = MemcacheBussiness.object.get(bussiness_code=bussiness_code)
        except MemcacheBussiness.DoesNotExist:
            return HttpResponse(u"业务编号不存在.")
        if subsystem_fullname == u"":
            return HttpResponse(u"子系统名称不能为空.")
        try:
            subsystem_code = MemcacheBussiness.object.latest('subsystem_code')
        except:
            return HttpResponse(u"无法获取子系统编号.")
        if isinstance(subsystem_code, int):
            subsystem_code += 1
        else:
            return HttpResponse(u"无法获取子系统编号.")
        try:
            mc_subsystem = MemcacheSubsystem(subsystem_code=subsystem_code, bussiness=mc_bussiness,
                                             subsystem_fullname=subsystem_fullname)
            mc_subsystem.save()
        except Exception, e:
            return HttpResponse(str(e))
        return HttpResponse(u"业务子系统添加成功.")
    
        
class GroupCreateView(View):
    form_class = GroupCreateForm
    template_name = 'mcadmin/group_create.html'
    
    def get(self, request, *args, **kwargs):
        c = {}
        c.update(csrf(request))
        form = self.form_class()
        c.update({'form': form })
        return render_to_response(self.template_name, context_instance=RequestContext(request, c))
    
    def post(self, request, *args, **kwargs):
        group_name = request.POST["group_name"]
        subsystem_code = request.POST["subsystem_code"]
        try:
            mc_subsystem = MemcacheSubsystem.object.get(subsystem_code=subsystem_code)
        except MemcacheSubsystem.DoesNotExist:
            return HttpResponse(u"业务子系统不存在.")
        if group_name == u"":
            return HttpResponse(u"实例组名不能为空.")
        try:
            group_code = MemcacheGroup.object.latest('group_code')
        except:
            return HttpResponse(u"无法获取实例组编号.")
        if isinstance(group_code, int):
            group_code += 1
        else:
            return HttpResponse(u"无法获取实例组编号.")
        try:
            mc_group = MemcacheGroup(group_code=group_code, subsystem=mc_subsystem, group_name=group_name)
            mc_group.save()
        except Exception, e:
            return HttpResponse(str(e))
        return HttpResponse(u"实例组添加成功.")

        
class SubsystemUpdateView(View):
    form_class = SubsystemUpdateForm
    template_name = 'mcadmin/subsystem_uptate.html'
    
    def get(self, request, *args, **kwargs):
        c = {}
        c.update(csrf(request))
        form = self.form_class()
        c.update({'form': form })
        return render_to_response(self.template_name, context_instance=RequestContext(request, c))
    
    def post(self, request, *args, **kwargs):
        subsystem_fullname = request.POST["subsystem_fullname"]
        subsystem_code = request.POST["subsystem_code"]
        try:
            mc_subsystem = MemcacheSubsystem.object.get(subsystem_code=subsystem_code)
        except MemcacheSubsystem.DoesNotExist:
            return HttpResponse(u"业务子系统不存在.") 
        if mc_subsystem.subsystem_fullname == subsystem_fullname:
            return HttpResponse(u"业务子系统名称不需要改变.")
        if subsystem_fullname == u"":
            return HttpResponse(u"子系统名称不能为空.")
        mc_subsystem.subsystem_fullname = subsystem_fullname
        try:
            mc_subsystem.save()
        except Exception, e:
            return HttpResponse(str(e))
        return HttpResponse(u"业务子系统名称修改成功.")                
            

class GroupUpdateView(View):
    form_class = GroupUpdateForm
    template_name = 'mcadmin/group_uptate.html'
    
    def get(self, request, *args, **kwargs):
        c = {}
        c.update(csrf(request))
        form = self.form_class()
        c.update({'form': form })
        return render_to_response(self.template_name, context_instance=RequestContext(request, c))
    
    def post(self, request, *args, **kwargs):
        group_name = request.POST["group_name"]
        group_code = request.POST["group_code"]
        try:
            mc_group = MemcacheGroup.object.get(group_code=group_code)
        except MemcacheSubsystem.DoesNotExist:
            return HttpResponse(u"实例组不存在.") 
        if mc_group.group_name == group_name:
            return HttpResponse(u"实例组名称不需要改变.")
        if group_name == u"":
            return HttpResponse(u"实例组名称不能为空.")
        try:
            group_name.save()
        except Exception, e:
            return HttpResponse(str(e))
        return HttpResponse(u"实例组名称修改成功.")


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
        
















