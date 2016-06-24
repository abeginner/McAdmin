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
    paginate_by = 15
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
            bussiness_code_list = []
            try:
                for i in self.request.POST['bussiness_code'].split():
                    bussiness_code_list.append(int(i))
            except:
                pass
            queryset = queryset.filter(bussiness_code__in=bussiness_code_list)
        if self.request.POST['bussiness_shortname'] != u'':
            bussiness_shortname_list = self.request.POST['bussiness_shortname'].split()
            queryset = queryset.filter(bussiness_shortname__in=bussiness_shortname_list)
        if self.request.POST['bussiness_fullname'] != u'':
            bussiness_fullname_list = self.request.POST['bussiness_fullname'].split()
            queryset = queryset.filter(bussiness_fullname__in=bussiness_fullname_list)
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
            return HttpResponseRedirect("/mcadmin/bussiness/display?msg_type=warning&msg=项目代号和项目名称为必填")
        if not RegEx.RegBussinessShortname(bussiness_shortname):
            return HttpResponseRedirect("/mcadmin/bussiness/display?msg_type=warning&msg=项目代号只能使用数字字母和下划线")
        try:
            bussiness_code = MemcacheBussiness.object.latest('bussiness_code').bussiness_code
        except MemcacheBussiness.DoesNotExist:
            bussiness_code = 1000
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
        return HttpResponseRedirect("/mcadmin/bussiness/display?msg_type=success&msg=项目模块添加成功")


class BussinessDeleteView(View):
    
    def post(self, request, *args, **kwargs):
        if request.POST.has_key('bussiness_code'):
            try:
                bussiness_code = int(request.POST["bussiness_code"])
            except:
                return HttpResponseRedirect("/mcadmin/bussiness/display?msg_type=warning&msg=项目id必须是数字")
            try:
                mc_bussiness = MemcacheBussiness.object.get(bussiness_code=bussiness_code)
            except MemcacheBussiness.DoesNotExist:
                return HttpResponseRedirect("/mcadmin/bussiness/display?msg_type=warning&msg=项目模块不存在")
            if MemcacheSubsystem.object.filter(bussiness=mc_bussiness).exists():
                return HttpResponseRedirect("/mcadmin/bussiness/display?msg_type=warning&msg=项目存在子系统模块，请先删除所有子系统模块")
            try:
                mc_bussiness.delete()
                return HttpResponseRedirect("/mcadmin/bussiness/display?msg_type=success&msg=项目模块删除成功")
            except Exception, e:
                return HttpResponseRedirect("/mcadmin/bussiness/display?msg_type=danger&msg=" + str(e))
        else:
            return HttpResponseRedirect("/mcadmin/bussiness/display?msg_type=warning&msg=没有项目id参数")
        

class BussinessUpdateView(View):
    form_class = BussinessUpdateForm
    template_name = 'mcadmin/bussiness_update.html'
    
    def get(self, request, *args, **kwargs):
        c = {}
        c.update(csrf(request))
        if request.GET.has_key('bussiness_code') and request.GET.has_key('bussiness_fullname'):
            c.update({'bussiness_code': request.GET['bussiness_code']})
            data = {'bussiness_fullname': request.GET['bussiness_fullname'] }
            c.update(data)
            form = self.form_class(initial=data)
            c.update({'form': form })
            return render_to_response(self.template_name, context_instance=RequestContext(request, c))
        else:
            return HttpResponseRedirect("/mcadmin/bussiness/display?msg_type=warning&msg=没有项目id参数")
    
    def post(self, request, *args, **kwargs):
        if request.POST.has_key('bussiness_code') and request.POST.has_key('bussiness_fullname'):
            bussiness_code = request.POST['bussiness_code']
            bussiness_fullname = request.POST['bussiness_fullname']
        else:
            return HttpResponseRedirect("/mcadmin/bussiness/display?msg_type=warning&msg=没有项目id参数")
        try:
            bussiness_code = int(bussiness_code)
        except:
            return HttpResponseRedirect("/mcadmin/bussiness/display?msg_type=warning&msg=没有项目id只能是数字")
        try:
            mc_bussiness = MemcacheBussiness.object.get(bussiness_code=bussiness_code)
        except MemcacheSubsystem.DoesNotExist:
            return HttpResponseRedirect("/mcadmin/bussiness/display?msg_type=warning&msg=项目不存在")
        if bussiness_fullname == mc_bussiness.bussiness_fullname:
            return HttpResponseRedirect("/mcadmin/bussiness/display?msg_type=warning&msg=项目名称不需要改变")
        if bussiness_fullname == u"":
            return HttpResponseRedirect("/mcadmin/bussiness/display?msg_type=warning&msg=项目名称不能为空")
        try:
            mc_bussiness.bussiness_fullname = bussiness_fullname
            mc_bussiness.save()
        except Exception, e:
            return HttpResponse(str(e))
        return HttpResponseRedirect("/mcadmin/bussiness/display?msg_type=success&msg=项目名称修改成功")
            

class SubsystemCreateView(View):
    form_class = SubsystemCreateForm
    template_name = 'mcadmin/subsystem_create.html'
    
    def get(self, request, *args, **kwargs):
        c = {}
        c.update(csrf(request))
        if request.GET.has_key("bussiness_code") and request.GET.has_key("bussiness_shortname") and request.GET.has_key("bussiness_fullname"):
            message = request.GET["bussiness_fullname"] + u'(项目代号:' + request.GET["bussiness_shortname"] + u')'
            bussiness_code = request.GET["bussiness_code"]
            c.update({'message': message })
            c.update({'bussiness_code': bussiness_code })
            form = self.form_class()
            c.update({'form': form })
            return render_to_response(self.template_name, context_instance=RequestContext(request, c))
        else:
            return HttpResponseRedirect("/mcadmin/bussiness/display?msg_type=warning&msg=缺少参数项目id")
    
    def post(self, request, *args, **kwargs):
        if request.POST.has_key("subsystem_fullname") and request.POST.has_key("bussiness_code"):
            subsystem_fullname = request.POST["subsystem_fullname"]
            try:
                bussiness_code = request.POST["bussiness_code"]
            except:
                return HttpResponseRedirect("/mcadmin/bussiness/display?msg_type=warning&msg=项目id必须为数字")
        else:
            return HttpResponseRedirect("/mcadmin/bussiness/display?msg_type=warning&msg=创建子系统失败，缺少参数subsystem_fullname或bussiness_code")
        try:
            mc_bussiness = MemcacheBussiness.object.get(bussiness_code=bussiness_code)
        except MemcacheBussiness.DoesNotExist:
            return HttpResponseRedirect("/mcadmin/bussiness/display?msg_type=warning&msg=项目id不存在")
        if subsystem_fullname == u"":
            return HttpResponseRedirect("/mcadmin/bussiness/display?msg_type=warning&msg=项目代号不能为空")
        try:
            subsystem_code = MemcacheSubsystem.object.latest('subsystem_code').subsystem_code
        except MemcacheSubsystem.DoesNotExist:
            subsystem_code = 1000
        except Exception, e:
            return HttpResponseRedirect("/mcadmin/bussiness/display?msg_type=danger&msg=无法获取子系统编号")
        subsystem_code += 1
        try:
            mc_subsystem = MemcacheSubsystem(subsystem_code=subsystem_code, bussiness=mc_bussiness,
                                             subsystem_fullname=subsystem_fullname)
            mc_subsystem.save()
        except Exception, e:
            return HttpResponse(str(e))
        return HttpResponseRedirect("/mcadmin/bussiness/display?msg_type=success&msg=项目子系统添加成功")


class SubsystemQueryView(SingleObjectMixin, ListView):

    paginate_by = 20
    form_class = SubsystemQueryForm
    template_name = "mcadmin/subsystem_display.html"
    model = MemcacheSubsystem
    query_list = {}
    request = None
    
    def get(self, request, *args, **kwargs):
        self.request = request
        if request.GET.has_key('bussiness_code'):
            self.query_list['bussiness_code'] = request.GET['bussiness_code']
            self.object = self.get_queryset()
            self.request.POST = self.request.GET
            return super(SubsystemQueryView, self).get(request, *args, **kwargs)
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
        return super(SubsystemQueryView, self).get(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super(SubsystemQueryView, self).get_context_data(**kwargs)
        csrf_token = csrf(self.request)      
        context.update(csrf_token)
        form = self.form_class(initial=self.request.POST)
        context.update({'form': form })
        return context
        
    def get_queryset(self):
        queryset = MemcacheSubsystem.object.all()
        if self.query_list.has_key('bussiness_code') and self.query_list['bussiness_code'] != u'':
            bussiness_code_list = []
            for i in self.query_list['bussiness_code'].split():
                try:
                    bussiness_code_list.append(int(i))
                except:
                    pass
            queryset = queryset.filter(bussiness__bussiness_code__in=bussiness_code_list)
        if self.query_list.has_key('bussiness_shortname') and self.query_list['bussiness_shortname'] != u'':
            bussiness_shortname_list = self.query_list['bussiness_shortname'].split()
            queryset = queryset.filter(bussiness__bussiness_shortname__in=bussiness_shortname_list)
        if self.query_list.has_key('bussiness_fullname') and self.query_list['bussiness_fullname'] != u'':
            bussiness_fullname_list = self.query_list['bussiness_fullname'].split()
            queryset = queryset.filter(bussiness__bussiness_fullname__in=bussiness_fullname_list)
        if self.query_list.has_key('subsystem_code') and self.query_list['subsystem_code'] != u'':
            subsystem_code_list = []
            for i in self.query_list['subsystem_code'].split():
                try:
                    subsystem_code_list.append(int(i))
                except:
                    pass
            queryset = queryset.filter(subsystem_code__in=subsystem_code_list)
        if self.query_list.has_key('subsystem_fullname') and self.query_list['subsystem_fullname'] != u'':
            subsystem_fullname_list = self.query_list['subsystem_fullname'].split()
            queryset = queryset.filter(subsystem_fullname__in=subsystem_fullname_list)
        return queryset


class SubsystemDeleteView(View):
    
    def post(self, request, *args, **kwargs):
        if request.POST.has_key('subsystem_code'):
            try:
                subsystem_code = int(request.POST["subsystem_code"])
            except:
                return HttpResponseRedirect("/mcadmin/subsystem/display?msg_type=warning&msg=子系统id必须是数字")
            try:
                mc_subsystem = MemcacheSubsystem.object.get(subsystem_code=subsystem_code)
            except MemcacheSubsystem.DoesNotExist:
                return HttpResponseRedirect("/mcadmin/subsystem/display?msg_type=warning&msg=子系统模块不存在")
            if MemcacheGroup.object.filter(subsystem=mc_subsystem).exists():
                return HttpResponseRedirect("/mcadmin/subsystem/display?msg_type=warning&msg=子系统模块存在实例组，请先删除所有实例组")
            try:
                mc_subsystem.delete()
                return HttpResponseRedirect("/mcadmin/subsystem/display?msg_type=success&msg=子系统模块删除成功")
            except Exception, e:
                return HttpResponseRedirect("/mcadmin/subsystem/display?msg_type=danger&msg=" + str(e))
        else:
            return HttpResponseRedirect("/mcadmin/subsystem/display?msg_type=warning&msg=没有项目子系统id参数")


class SubsystemUpdateView(View):
    form_class = SubsystemUpdateForm
    template_name = "mcadmin/subsystem_update.html"
    
    def get(self, request, *args, **kwargs):
        c = {}
        c.update(csrf(request))
        if request.GET.has_key('subsystem_code') and request.GET.has_key('subsystem_fullname'):
            c.update({'subsystem_code': request.GET['subsystem_code']})
            data = {'subsystem_fullname': request.GET['subsystem_fullname'] }
            c.update(data)
            form = self.form_class(initial=data)
            c.update({'form': form })
            return render_to_response(self.template_name, context_instance=RequestContext(request, c))
        else:
            return HttpResponseRedirect("/mcadmin/subsystem/display?msg_type=warning&msg=没有子系统id参数")
    
    def post(self, request, *args, **kwargs):
        if request.POST.has_key('subsystem_code') and request.POST.has_key('subsystem_fullname'):
            subsystem_code = request.POST['subsystem_code']
            subsystem_fullname = request.POST['subsystem_fullname']
        else:
            return HttpResponseRedirect("/mcadmin/subsystem/display?msg_type=warning&msg=没有项目id参数")
        try:
            subsystem_code = int(subsystem_code)
        except:
            return HttpResponseRedirect("/mcadmin/subsystem/display?msg_type=warning&msg=没有项目id只能是数字")
        try:
            mc_subsystem = MemcacheSubsystem.object.get(subsystem_code=subsystem_code)
        except MemcacheSubsystem.DoesNotExist:
            return HttpResponseRedirect("/mcadmin/subsystem/display?msg_type=warning&msg=子系统不存在")
        if subsystem_fullname == mc_subsystem.subsystem_fullname:
            return HttpResponseRedirect("/mcadmin/subsystem/display?msg_type=warning&msg=子系统名称不需要改变")
        if subsystem_fullname == u"":
            return HttpResponseRedirect("/mcadmin/subsystem/display?msg_type=warning&msg=子系统名称不能为空")
        try:
            mc_subsystem.subsystem_fullname = subsystem_fullname
            mc_subsystem.save()
        except Exception, e:
            return HttpResponse(str(e))
        return HttpResponseRedirect("/mcadmin/subsystem/display?msg_type=success&msg=实例组名称修改成功")


class GroupCreateView(View):
    form_class = GroupCreateForm
    template_name = 'mcadmin/group_create.html'
    
    def get(self, request, *args, **kwargs):
        c = {}
        c.update(csrf(request))
        if request.GET.has_key("subsystem_code") and request.GET.has_key("subsystem_fullname") and request.GET.has_key("bussiness_fullname"):
            message = u'项目名称:' + request.GET["bussiness_fullname"] + u'，子系统名称:' + request.GET["subsystem_fullname"]
            subsystem_code = request.GET["subsystem_code"]
            c.update({'message': message })
            c.update({'subsystem_code': subsystem_code })
            form = self.form_class()
            c.update({'form': form })
            return render_to_response(self.template_name, context_instance=RequestContext(request, c))
        else:
            return HttpResponseRedirect("/mcadmin/subsystem/display?msg_type=warning&msg=缺少参数子系统id")
    
    def post(self, request, *args, **kwargs):
        print request
        if request.POST.has_key("group_name") and request.POST.has_key("subsystem_code"):
            group_name = request.POST["group_name"]
            try:
                subsystem_code = request.POST["subsystem_code"]
            except:
                return HttpResponseRedirect("/mcadmin/subsystem/display?msg_type=warning&msg=子系统id必须为数字")
        else:
            return HttpResponseRedirect("/mcadmin/subsystem/display?msg_type=warning&msg=创建子系统失败，缺少参数group_name或subsystem_code")
        try:
            mc_subsystem = MemcacheSubsystem.object.get(subsystem_code=subsystem_code)
        except MemcacheBussiness.DoesNotExist:
            return HttpResponseRedirect("/mcadmin/subsystem/display?msg_type=warning&msg=子系统id不存在")
        if group_name == u"":
            return HttpResponseRedirect("/mcadmin/subsystem/display?msg_type=warning&msg=组名称不能为空")
        try:
            group_code = MemcacheGroup.object.latest('group_code').group_code
        except MemcacheGroup.DoesNotExist:
            group_code = 1000
        except Exception, e:
            return HttpResponseRedirect("/mcadmin/subsystem/display?msg_type=danger&msg=无法获取组编号")
        group_code += 1
        try:
            mc_group = MemcacheGroup(group_code=group_code, subsystem=mc_subsystem, group_name=group_name)
            mc_group.save()
        except Exception, e:
            return HttpResponse(str(e))
        return HttpResponseRedirect("/mcadmin/subsystem/display?msg_type=success&msg=实例组添加成功")


class GroupQueryView(SingleObjectMixin, ListView):

    paginate_by = 30
    form_class = GroupQueryForm
    template_name = "mcadmin/group_display.html"
    model = MemcacheSubsystem
    query_list = {}
    request = None
    
    def get(self, request, *args, **kwargs):
        self.request = request
        if request.GET.has_key('group_code'):
            self.query_list['group_code'] = request.GET['group_code']
            self.object = self.get_queryset()
            return super(GroupQueryView, self).get(request, *args, **kwargs)
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
        return super(GroupQueryView, self).get(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super(GroupQueryView, self).get_context_data(**kwargs)
        csrf_token = csrf(self.request)      
        context.update(csrf_token)
        form = self.form_class(initial=self.query_list)
        context.update({'form': form })
        return context
        
    def get_queryset(self):
        queryset = MemcacheGroup.object.all()
        if self.query_list.has_key('bussiness_code') and self.query_list['bussiness_code'] != u'':
            bussiness_code_list = []
            for i in self.query_list['bussiness_code'].split():
                try:
                    bussiness_code_list.append(int(i))
                except:
                    pass
            queryset = queryset.filter(subsystem__bussiness__bussiness_code__in=bussiness_code_list)
        if self.query_list.has_key('bussiness_shortname') and self.query_list['bussiness_shortname'] != u'':
            bussiness_shortname_list = self.query_list['bussiness_shortname'].split()
            queryset = queryset.filter(subsystem__bussiness__bussiness_shortname__in=bussiness_shortname_list)
        if self.query_list.has_key('bussiness_fullname') and self.query_list['bussiness_fullname'] != u'':
            bussiness_fullname_list = self.query_list['bussiness_fullname'].split()
            queryset = queryset.filter(subsystem__bussiness__bussiness_fullname__in=bussiness_fullname_list)
        if self.query_list.has_key('subsystem_code') and self.query_list['subsystem_code'] != u'':
            subsystem_code_list = []
            for i in self.query_list['subsystem_code'].split():
                try:
                    subsystem_code_list.append(int(i))
                except:
                    pass
            queryset = queryset.filter(subsystem__subsystem_code__in=subsystem_code_list)
        if self.query_list.has_key('subsystem_fullname') and self.query_list['subsystem_fullname'] != u'':
            subsystem_fullname_list = self.query_list['subsystem_fullname'].split()
            queryset = queryset.filter(subsystem__subsystem_fullname__in=subsystem_fullname_list)
        if self.query_list.has_key('group_code') and self.query_list['group_code'] != u'':
            group_code_list = []
            for i in self.query_list['group_code'].split():
                try:
                    group_code_list.append(int(i))
                except:
                    pass
            queryset = queryset.filter(group_code__in=group_code_list)
        if self.query_list.has_key('group_name') and self.query_list['group_name'] != u'':
            group_name_list = self.query_list['group_name'].split()
            queryset = queryset.filter(group_name__in=group_name_list)
        return queryset
















        
















