from django.conf.urls import patterns, include, url



urlpatterns = patterns('bet.views',
    url(r'^games/$', 'games'),
    url(r'^games/(?P<event>\w+)/$', 'games'),
    url(r'^bets/$', 'bets'),
    url(r'^bets/(?P<betpool>\w+)/(?P<event>\w+)/$', 'bets'),
    url(r'^ranking/$', 'ranking'),
)