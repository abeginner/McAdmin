#! coding: utf-8

from django.conf.urls import url
from McAdmin.mcadmin.user_views import *
from McAdmin.mcadmin.mcadmin_bussiness_views import *
from McAdmin.mcadmin.mcadmin_host_views import *
from McAdmin.mcadmin.mcadmin_instances_views import *


urlpatterns = [
    url(r'^host/display$', HostQueryView.as_view()),
    url(r'^host/create$', HostCreateView.as_view()),
    url(r'^host/delete$', HostDeleteView.as_view()),
    url(r'^bussiness/create$', BussinessCreateView.as_view()),
    url(r'^bussiness/display$', BussinessQueryView.as_view()),
    url(r'^bussiness/delete$', BussinessDeleteView.as_view()),
    url(r'^bussiness/update$', BussinessUpdateView.as_view()),
    url(r'^subsystem/create$', SubsystemCreateView.as_view()),
    url(r'^subsystem/display$', SubsystemQueryView.as_view()),
    url(r'^subsystem/update$', SubsystemUpdateView.as_view()),
    url(r'^subsystem/delete$', SubsystemDeleteView.as_view()),
    url(r'^group/create$', GroupCreateView.as_view()),
    url(r'^group/display$', GroupQueryView.as_view()),
    url(r'^group/delete$', GroupDeleteView.as_view()),
    url(r'^group/update$', GroupUpdateView.as_view()),
    url(r'^instance/display$', InstanceQueryView.as_view()),
    url(r'^instance/create$', InstanceCreateView.as_view()),
    url(r'^instance/delete$', InstanceDeleteView.as_view()),
    url(r'^user/checkcode$', CheckCodeView.as_view()),
    url(r'^user/login$', LoginView.as_view()),
    url(r'^user/logout$', LogoutView.as_view()),
    url(r'^user/register$', RegisterView.as_view()),
]





