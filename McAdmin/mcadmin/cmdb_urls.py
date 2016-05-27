#! coding: utf-8

from django.conf.urls import url
from McAdmin.mcadmin.cmdb_api_views import ServerInfoView

urlpatterns = [
    url(r'^server_info/$', ServerInfoView.as_view()),
]