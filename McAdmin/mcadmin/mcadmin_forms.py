from django import forms

class HostQueryForm(forms.Form):
    server_code = forms.CharField(label=u'server id')
    interip = forms.CharField(label=u'内网ip')
    idc_fullname = forms.CharField(label=u'机房')
    
class BussinessQueryForm(forms.Form):
    bussiness_code = forms.CharField(label=u'业务id')
    bussiness_fullname = forms.CharField(label=u'业务名称')
    
class InstanceQueryForm(forms.Form):
    instance_code = forms.CharField(label=u'实例id')
    host = forms.CharField(label=u'实例ip')
    bussiness = forms.CharField(label=u'业务名称')
    subsystem = forms.CharField(label=u'业务子系统')
    tech_admin = forms.CharField(label=u'技术负责人')
    sysop_admin = forms.CharField(label=u'运维负责人')

class HostCreateFrom(forms.Form):
    ipaddress = forms.CharField(label=u'内网ip')
    description = forms.CharField(label=u'备注', widget=forms.Textarea())
