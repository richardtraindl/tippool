from django.shortcuts import render, render_to_response
from django.http import HttpResponseRedirect, HttpResponse
from django.template import RequestContext
from itertools import chain
from django.shortcuts import get_object_or_404
from bet.models import Event, EventManager, Match, Team, Membership, Pool, PoolEvent, Account, Bet



class MatchBets(object):
    def __init__(self, match=None):
        self.match = match
        self.betlist = []

    def add_bet(self, bets):
        for bet in bets:
            self.betlist.append(bet)



def bets(request, req_pool=1, req_event=1):
    context = RequestContext(request)

    # pool
    if req_pool == None:
        pool = Pool.objects.get(membership__user__id=request.user.id, active=True)
    else:
        pool = Pool.objects.get(id=req_pool)

    # event
    if req_event == None:
        event = Event.objects.get(poolevent__pool_id=pool.id, active=True)
    else:
        event = Event.objects.get(id=req_event)

    # all pools where user is member
    pools = Pool.objects.filter(membership__user__id=request.user.id, active=True)

    # all events for choosen pool
    events = Event.objects.filter(poolevent__pool_id=pool.id, active=True)

    # all matches for choosen event
    matches = Match.objects.all().filter(event_id=event.id)

    # all bets for choosen pool and event
    match_bets = []
    for match in matches:
        match_bet = MatchBets(match)

        try:
            bets = Bet.objects.filter(match__id=match.id, account__poolevent__pool__id=pool.id)
            match_bet.add_bet(bets)
        except Bet.DoesNotExist:
            continue
            
        match_bets.append(match_bet)

        

    return render(request, 'bet/bets.html', {'body_id': 'bets', 'pool': pool, 'pools': pools, 'event': event, 'events': events, 'match_bets': match_bets } )



def ranking(request):
    return render(request, 'bet/ranking.html', {'body_id': 'ranking'} )



def games(request, req_event=1):
    context = RequestContext(request)
    
    if req_event == None:
        event = Event.objects.filter(parent_id=None, active=True)[:1].get()
    else:
        event = Event.objects.get(id=req_event)

    events = Event.objects.all().filter(active=True)

    matches = Match.objects.all().filter(event_id=event.id)

    return render_to_response('bet/games.html', {'body_id': 'games', 'event': event, 'events': events, 'matches': matches }, context )

