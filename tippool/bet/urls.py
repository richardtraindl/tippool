from django.conf.urls import patterns, include, url



urlpatterns = patterns('bet.views',
    url(r'^mybets/$', 'mybets'),
    url(r'^mybets/(?P<eventid>\w+)/$', 'mybets'),
    url(r'^bets/$', 'bets'),
    url(r'^bets/(?P<poolid>\w+)/$', 'bets'),
    url(r'^bets/(?P<poolid>\w+)/(?P<eventid>\w+)/$', 'bets'),
    url(r'^do_bet/$', 'do_bet'),
    url(r'^ranking/(?P<poolid>\w+)/(?P<eventid>\w+)/$', 'ranking'),
    url(r'^ranking/$', 'ranking'),
    url(r'^admin/$', 'admin'),
    url(r'^calc_points/(?P<eventid>\w+)/$', 'calc_points'),
    # url(r'^calc_points/$', 'calc_points'),
    # url(r'^calc_points/(?P<eventlabel>\w+\.*\w+)/$', 'calc_points'),
    # url(r'^calc_points/(?P<eventlabel>\w+)/$', 'calc_points'),
    # url(r'^calc_points/(?P<eventlabel>[A-Za-z0-9 ]+)/$', 'calc_points'),
)