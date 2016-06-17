#! coding: utf-8

from django.conf.urls import url
from McAdmin.mcadmin.mcadmin_views import *, HostCreateView, HostDeleteView,\
    BussinessCreateView, BussinessQueryView, SubsystemCreateView,\
    SubsystemQueryView, SubsystemUpdateView, GroupCreateView, GroupQueryView
from McAdmin.mcadmin.user_views import *
from McAdmin.mcadmin.models import Bussiness
from McAdmin.mcadmin.mcadmin_forms import GroupCreateForm
from McAdmin.mcadmin.mcadmin_instances_views import InstanceCreateView

urlpatterns = [
    url(r'^host/display$', HostQueryView.as_view()),
    url(r'^user/checkcode$', CheckCodeView.as_view()),
    url(r'^user/login$', LoginView.as_view()),
    url(r'^host/create$', HostCreateView.as_view()),
    url(r'^host/delete$', HostDeleteView.as_view()),
    url(r'^bussiness/create$', BussinessCreateView.as_view()),
    url(r'^bussiness/display$', BussinessQueryView.as_view()),
    url(r'^sybsystem/create$', SubsystemCreateView.as_view()),
    url(r'^sybsystem/display$', SubsystemQueryView.as_view()),
    url(r'^sybsystem/update$', SubsystemUpdateView.as_view()),
    url(r'^group/update$', GroupUpdateView.as_view()),
    url(r'^group/create$', GroupCreateView.as_view()),
    url(r'^group/display$', GroupQueryView.as_view()),
    url(r'^instance/display$', InstanceQueryView.as_view()),
    url(r'^instance/create$', InstanceCreateView.as_view()),
    url(r'^instance/delete$', InstanceDeleteView.as_view()),
]





