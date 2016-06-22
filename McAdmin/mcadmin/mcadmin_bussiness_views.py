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
   

class BussinessQueryView(SingleObjectMixin, ListView):

    form_class = BussinessQueryForm
    paginate_by = 20
    template_name = "mcadmin/bussiness_display.html"
    model = MemcacheBussiness
    request = None
    
    def post(self, request, *args, **kwargs):
        self.request = request
        self.object = self.get_queryset()
        if self.request.POST.has_key('page'):
            self.kwargs['page'] = self.request.POST['page'][0]
        return super(BussinessQueryView, self).get(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super(BussinessQueryView, self).get_context_data(**kwargs)
        csrf_token = csrf(self.request)      
        context.update(csrf_token)
        form = self.form_class(initial=self.request.POST)
        context.update({'form': form })
        return context
        
    def get_queryset(self):
        queryset = self.model.object.all()
        if self.request.POST['bussiness_code'] != u'':
            try:
                bussiness_code = int(self.request.POST['sbussiness_code'])
            except:
                pass
            queryset = queryset.filter(bussiness_code=bussiness_code)
        if self.request.POST['bussiness_fullname'] != u'':
            queryset = queryset.filter(bussiness_fullname=self.request.POST['bussiness_fullname'])
        return queryset
    
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
            return HttpResponseRedirect("/mcadmin/bussiness/display?msg_type=warning&msg=业务简写和业务名称为必填")
        if not RegEx.RegBussinessShortname(bussiness_shortname):
            return HttpResponseRedirect("/mcadmin/bussiness/display?msg_type=warning&msg=业务简写只能使用数字和字母")
        try:
            bussiness_code = MemcacheBussiness.object.latest('bussiness_code').bussiness_code
        except Exception, e:
            return HttpResponseRedirect("/mcadmin/bussiness/display?msg_type=danger&msg=" + str(e))
        bussiness_code += 1
        try:
            mc_bussiness = MemcacheBussiness(bussiness_code=bussiness_code, 
                                         bussiness_shortname=bussiness_shortname,
                                         bussiness_fullname=bussiness_fullname)
            mc_bussiness.save()
        except Exception, e:
            return HttpResponseRedirect("/mcadmin/bussiness/display?msg_type=danger&msg=" + str(e))
        return HttpResponseRedirect("/mcadmin/bussiness/display?msg_type=success&msg=业务模块添加成功")


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



        
















