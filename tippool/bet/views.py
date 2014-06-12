from django.shortcuts import render, render_to_response
from django.http import HttpResponseRedirect, HttpResponse
from django.template import RequestContext
from bet.models import Event, EventManager, Match, Team, Opponent, Membership, Betpool, PoolEvent, Bet, Account



class MyMatch(object):
    def __init__(self, match_id=None, begin=None, status=None, has_overtime=None, has_penalties=None, \
                team1_name=None, team1_logo=None, team1_active=None, team1_score_regular=None, team1_score_overtime=None, team1_score_penalties=None, \
                team2_name=None, team2_logo=None, team2_active=None, team2_score_regular=None, team2_score_overtime=None, team2_score_penalties=None):
        self.match_id = match_id
        self.begin = begin
        self.status = status
        self.has_overtime = has_overtime
        self.has_penalties = has_penalties
        self.team1_name = team1_name
        self.team1_logo = team1_logo
        self.team1_active = team1_active
        self.team1_score_regular = team1_score_regular
        self.team1_score_overtime = team1_score_overtime
        self.team1_score_penalties = team1_score_penalties
        self.team2_name = team2_name
        self.team2_logo = team2_logo
        self.team2_active = team2_active
        self.team2_score_regular = team2_score_regular
        self.team2_score_overtime = team2_score_overtime
        self.team2_score_penalties = team2_score_penalties


class MyTip(object):
    def __init__(self, account_id=None, match_begin=None, match_status=None, match_has_overtime=None, match_has_penalties=None, \
                team1_name=None, team1_logo=None, team1_score_regular=None, team1_score_overtime=None, team1_score_penalties=None, \
                team2_name=None, team2_logo=None, team2_score_regular=None, team2_score_overtime=None, team2_score_penalties=None, rating=None):
        self.account_id=account_id
        self.match_begin = match_begin
        self.match_status = match_status
        self.match_has_overtime = match_has_overtime
        self.match_has_penalties = match_has_penalties
        self.team1_name = team1_name
        self.team1_logo = team1_logo
        self.team1_score_regular=team1_score_regular 
        self.team1_score_overtime=team1_score_overtime 
        self.team1_score_penalties=team1_score_penalties
        self.team2_name = team2_name
        self.team2_logo = team2_logo
        self.team2_score_regular=team2_score_regular 
        self.team2_score_overtime=team2_score_overtime 
        self.team2_score_penalties=team2_score_penalties 
        self.rating=rating

    
    
class MyBetpool(object):
    def __init__(self, label=None):
        self.label=label



class MyUser(object):
    def __init__(self, username=None):
        self.username=username






def bets(request, betpool=1, event=1):
    context = RequestContext(request)

    if betpool == None:
        membership = Membership.objects.filter(user=request.user.id)[:1].get()
        mybetpool = Betpool.objects.get(id=membership.betpool_id)
    else:
        mybetpool = Betpool.objects.get(id=betpool)

    if event == None:
        mypoolevent = PoolEvent.objects.filter(betpool_id=mybetpool.id)[:1].get()
        myevent = Event.objects.get(id=mypoolevent.event_id)
    else:
        myevent = Event.objects.get(id=event)

    memberships = Membership.objects.all().filter(user_id=request.user.id)
    mybetpools = []
    for membership in memberships:
        mybetpools.append(Betpool.objects.get(id=membership.betpool_id, active=True))

    poolevents = PoolEvent.objects.all().filter(betpool_id=mybetpool.id)
    myevents = []
    for poolevent in poolevents:
        myevents.append(Event.objects.get(id=poolevent.event_id))

    return render(request, 'bet/bets.html', {'body_id': 'bets', 'betpool': mybetpool, 'betpools': mybetpools, 'event': myevent, 'betpool_tips': 'zzz' } )



def ranking(request):
    return render(request, 'bet/ranking.html', {'body_id': 'ranking'} )



def games(request, event=1):
    context = RequestContext(request)
    
    if event == None:
        myevent = Event.objects.all().filter(parent_id=None, active=True)[:1].get()
    else:
        myevent = Event.objects.get(id=event)

    myevents = Event.objects.all().filter(active=True)

    allmatches = Match.objects.all().filter(event=myevent)

    mymatches = []
    for onematch in allmatches:
        opp1 = Opponent.objects.get(match_id=onematch, rank=1)
        opp2 = Opponent.objects.get(match_id=onematch, rank=2)
        team1 = Team.objects.get(id=opp1.team_id)
        team2 = Team.objects.get(id=opp2.team_id)
        mymatches.append(MyMatch(match_id=onematch.id, begin=onematch.begin.strftime('%d.%m.%Y, %H:%M'), status=onematch.status, has_overtime=onematch.has_overtime, has_penalties=onematch.has_penalties, \
                                team1_name=team1.name, team1_logo=team1.logo, team1_active=team1.active, team1_score_regular=opp1.score_regular, team1_score_overtime=opp1.score_overtime, team1_score_penalties=opp1.score_penalties, \
                                team2_name=team2.name, team2_logo=team2.logo, team2_active=team2.active, team2_score_regular=opp2.score_regular, team2_score_overtime=opp2.score_overtime, team2_score_penalties=opp2.score_penalties))

    return render_to_response('bet/games.html', {'body_id': 'games', 'event': myevent, 'events': myevents, 'matches': mymatches }, context )

