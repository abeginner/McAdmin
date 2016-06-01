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
        c = {}
        c.update(csrf(request))
        form = self.form_class()
        c.update({'form': form })
        return render_to_response(self.template_name, context_instance=RequestContext(request, c))
    





   
