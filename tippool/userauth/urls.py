from django.conf.urls import patterns, include, url



urlpatterns = patterns('userauth.views',
    url(r'^bye/$', 'bye'),
    url(r'^login/$', 'user_login'),
    url(r'^logout/$', 'user_logout'),
    url(r'^password_change/$', 'user_password_change'),
)