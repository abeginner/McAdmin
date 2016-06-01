#! coding: utf-8

from django.conf.urls import url
from McAdmin.mcadmin.mcadmin_views import *

urlpatterns = [
    url(r'^host/host_display$', HostQueryView.as_view()),
]