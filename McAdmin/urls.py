from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'McAdmin.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^cmdb/', include("McAdmin.mcadmin.cmdb_urls")),
    url(r'^mcadmin/', include("McAdmin.mcadmin.mcadmin_urls")),
)
