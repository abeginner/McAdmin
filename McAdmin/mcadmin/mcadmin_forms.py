#! coding: utf-8

from django import forms
from McAdmin.mcadmin.models import *

class HostQueryForm(forms.Form):
    server_code = forms.IntegerField(label=u'server id')
    interip = forms.CharField(label=u'内网ip')
    idc_fullname = forms.ModelChoiceField(label=u'机房', empty_label=u"选择机房", queryset=IdcMirror.objects.all().values('idc_fullname'))