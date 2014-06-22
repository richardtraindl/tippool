from django.conf.urls import patterns, include, url



urlpatterns = patterns('bet.views',
    url(r'^games/$', 'games'),
    url(r'^games/(?P<req_event>\w+)/$', 'games'),
    url(r'^bets/$', 'bets'),
    url(r'^bets/(?P<req_pool>\w+)/$', 'bets'),
    url(r'^bets/(?P<req_pool>\w+)/(?P<req_event>\w+)/$', 'bets'),
    url(r'^add_bet/$', 'add_bet'),
    url(r'^add_bet/(?P<req_pool>\w+)/(?P<req_match>\w+)/$', 'add_bet'),
    url(r'^ranking/$', 'ranking'),
)