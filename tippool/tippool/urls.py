from django.conf.urls import patterns, include, url
from django.contrib import admin



admin.autodiscover()



urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^userauth/', include('userauth.urls')),
    url(r'^bet/', include('bet.urls')),
)