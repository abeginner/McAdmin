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
        try:
            instance_del = MemcacheInstance.object.get(host=mc_host, port=port)
            if instance_del.status is 5:
                instance_code = instance_del.instance_code
            else:
                return HttpResponse(u"无法添加实例，实例" + interip + u":" + str(port) + u"已存在.")
        except MemcacheInstance.DoesNotExist:
            try:
                instance_code = MemcacheInstance.object.latest('instance_code').instance_code
                instance_code += 1
            except:
                return HttpResponse(u"无法获取实例ID.")
        try:
            mc_instance = MemcacheInstance(instance_code=instance_code, host=mc_host, group = mc_group,
                port=port, max_memory=max_memory, max_connection=max_connection, is_bind=is_bind,
                tech_admin=tech_admin, sysop_admin=sysop_admin, creator=u'dw_lijie1', status=0,
                description=description)
            mc_instance.save()
        except:
            return HttpResponse(u"无法创建memcache实例.")
        
        












   