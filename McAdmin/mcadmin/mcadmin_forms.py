from django import forms

class HostQueryForm(forms.Form):
    server_code = forms.CharField(label=u'server id')
    interip = forms.CharField(label=u'内网ip')
    idc_fullname = forms.CharField(label=u'机房')
    
class BussinessQueryForm(forms.Form):
    bussiness_code = forms.CharField(label=u'业务id')
    bussiness_shortname = forms.CharField(label=u'业务简写')
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

class BussinessCreateForm(forms.Form):
    bussiness_shortname = forms.CharField(label=u'业务简写')
    bussiness_fullname = forms.CharField(label=u'业务名称')

class SubsystemCreateForm(forms.Form):
    subsystem_fullname  = forms.CharField(label=u'子系统名称')

class GroupCreateForm(forms.Form):
    group_name = forms.CharField(label=u'实例组名称')

class SubsystemUpdateForm(forms.Form):
    subsystem_fullname  = forms.CharField(label=u'子系统名称')

class GroupUpdateForm(forms.Form):
    group_name = forms.CharField(label=u'实例组名称')

class InstanceCreateForm(forms.Form):
    interip = forms.CharField(label=u'内网ip')
    port = forms.IntegerField(label=u'端口号', min_value=11211, max_value=11250, initial=11211)
    max_memory = forms.IntegerField(label=u'最大内存', min_value=256, max_value=65535, initial=1024)
    max_connection = forms.IntegerField(label=u'最大连接数', min_value=1024, max_value=65535, initial=10240)
    is_bind = forms.BooleanField(label=u'绑定内网')
    tech_admin = forms.CharField(label=u'研发负责人')
    sysop_admin = forms.CharField(label=u'运维负责人')
    description = forms.CharField(label=u'备注', widget=forms.Textarea())





