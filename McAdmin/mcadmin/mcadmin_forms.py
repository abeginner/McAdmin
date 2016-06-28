# coding=utf-8

from django import forms

class HostQueryForm(forms.Form):
    server_code = forms.CharField(label=u'server id')
    interip = forms.CharField(label=u'内网ip')
    idc_fullname = forms.CharField(label=u'机房')
    
class BussinessQueryForm(forms.Form):
    bussiness_code = forms.CharField(label=u'项目id')
    bussiness_shortname = forms.CharField(label=u'项目代号')
    bussiness_fullname = forms.CharField(label=u'项目名称')
    
class InstanceQueryForm(forms.Form):
    instance_code = forms.CharField(label=u'实例id')
    hosts = forms.CharField(label=u'ip')
    port = forms.CharField(label=u'端口')
    bussiness_shortname = forms.CharField(label=u'项目代号')
    bussiness_fullname = forms.CharField(label=u'项目名称')
    subsystem_fullname  = forms.CharField(label=u'子系统名称')
    group_name = forms.CharField(label=u'组名称')
    tech_admin = forms.CharField(label=u'技术负责人')
    sysop_admin = forms.CharField(label=u'运维负责人')

class HostCreateFrom(forms.Form):
    server_code = forms.CharField(label=u'server id')
    ipaddress = forms.CharField(label=u'内网ip')
    description = forms.CharField(label=u'备注',  widget=forms.Textarea(attrs={'cols': '40', 'rows': '3'}))

class BussinessCreateForm(forms.Form):
    bussiness_shortname = forms.CharField(label=u'项目代号')
    bussiness_fullname = forms.CharField(label=u'项目名称')
    
class BussinessUpdateForm(forms.Form):
    bussiness_fullname  = forms.CharField(label=u'项目名称')
    
class SubsystemQueryForm(forms.Form):
    bussiness_code = forms.CharField(label=u'项目id')
    bussiness_shortname = forms.CharField(label=u'项目代号')
    bussiness_fullname = forms.CharField(label=u'项目名称')
    subsystem_code  = forms.CharField(label=u'子系统id')
    subsystem_fullname  = forms.CharField(label=u'子系统名称')
    
class SubsystemCreateForm(forms.Form):
    subsystem_fullname  = forms.CharField(label=u'子系统名称')

class GroupCreateForm(forms.Form):
    group_name = forms.CharField(label=u'实例组名称')

class SubsystemUpdateForm(forms.Form):
    subsystem_fullname  = forms.CharField(label=u'子系统名称')

class GroupQueryForm(forms.Form):
    bussiness_code = forms.CharField(label=u'项目id')
    subsystem_code  = forms.CharField(label=u'子系统id')
    group_code = forms.CharField(label=u'组id')
    bussiness_shortname = forms.CharField(label=u'项目代号')
    bussiness_fullname = forms.CharField(label=u'项目名称')
    subsystem_fullname  = forms.CharField(label=u'子系统名称')
    group_name = forms.CharField(label=u'组名称')

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
    description = forms.CharField(label=u'备注', widget=forms.Textarea(attrs={'cols': '40', 'rows': '3'}))

class InstanceUpdateForm(forms.Form):
    max_memory = forms.IntegerField(label=u'最大内存', min_value=256, max_value=65535)
    max_connection = forms.IntegerField(label=u'最大连接数', min_value=1024, max_value=65535)
    is_bind = forms.BooleanField(label=u'绑定内网')
    tech_admin = forms.CharField(label=u'研发负责人')
    sysop_admin = forms.CharField(label=u'运维负责人')
    description = forms.CharField(label=u'备注', widget=forms.Textarea(attrs={'cols': '40', 'rows': '3'}))

class LoginForm(forms.Form):
    username = forms.CharField(label='用户名:')
    password = forms.CharField(label='密码:', widget = forms.PasswordInput)
    check_code = forms.CharField(label='验证码:')

class RegisterForm(forms.Form):
    username = forms.CharField(label='用户名:')
    password = forms.CharField(label='密码:', widget = forms.PasswordInput)
    verify_password = forms.CharField(label='确认密码:', widget = forms.PasswordInput)
    email = forms.EmailField(label='电子邮箱:')
    realname = forms.CharField(label='真实姓名:')
    department = forms.CharField(label='部门:')
    check_code = forms.CharField(label='验证码:')

