from django.conf.urls import patterns, include, url



urlpatterns = patterns('bet.views',
    url(r'^games/$', 'games'),
    url(r'^games/(?P<eventid>\w+)/$', 'games'),
    url(r'^mybets/$', 'mybets'),
    url(r'^mybets/(?P<eventid>\w+)/$', 'mybets'),
    url(r'^bets/$', 'bets'),
    url(r'^do_bet/$', 'do_bet'),
    url(r'^bets/(?P<poolid>\w+)/$', 'bets'),
    url(r'^bets/(?P<poolid>\w+)/(?P<eventid>\w+)/$', 'bets'),
    url(r'^add_bet/$', 'add_bet'),
    url(r'^add_bet/(?P<betid>\w+)/$', 'add_bet'),
    url(r'^add_bet/(?P<poolid>\w+)/(?P<eventid>\w+)/(?P<betid>\w+)/$', 'add_bet'),
    url(r'^ranking/$', 'ranking'),
)