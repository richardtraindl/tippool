# -*- coding: utf-8 -*-

from django.shortcuts import render, render_to_response
from django.http import HttpResponseRedirect, HttpResponse
from django.template import RequestContext
from itertools import chain
from django.shortcuts import get_object_or_404
import datetime
from dateutil.tz import tzlocal
from bet.models import Event, EventManager, Match, Team, Membership, Pool, PoolEvent, Account, Bet
from bet.forms import BetForm




class PoolUserBet(object):
    def __init__(self, pool=None, user=None, bet=None):
        self.pool = pool
        self.user = user
        self.bet = bet

class MatchBet(object):
    def __init__(self, match=None):
        self.match = match
        self.betlist = []



def mybets(request, eventid=1):
    context = RequestContext(request)

    # all pools where user is member
    pools = Pool.objects.filter(membership__user_id=request.user.id, active=True)

    # event
    if eventid == None:
        event = Event.objects.get(poolevent__pool_id=pools[0].id, active=True)
    else:
        event = Event.objects.get(id=eventid)


    # all events for choosen pool
    events = Event.objects.filter(poolevent__pool__membership__user_id=request.user.id, \
                                    active=True).distinct()

    # all matches for choosen event
    matches = Match.objects.all().filter(event_id=event.id)

    # all bets for choosen pool and event
    matchbets = []
    for match in matches:
        matchbet = MatchBet(match)

        for pool in pools:
            try:
                membership = Membership.objects.get(pool_id=pool.id, user_id=request.user.id)
            except Membership.DoesNotExist:
                continue
            
            try:
                account= Account.objects.get(event_id=match.event_id, membership_id=membership.id)
            except Account.DoesNotExist:
                account= Account(match.event_id, membership.id)

            try:
                bet = Bet.objects.get(match_id=match.id, account_id=account.id)
                pooluserbet = PoolUserBet()
                pooluserbet.pool = pool
                pooluserbet.user = request.user
                pooluserbet.bet = bet
                matchbet.betlist.append(pooluserbet)
            except Bet.DoesNotExist:
                bet = Bet()
                bet.match_id = match.id
                bet.account_id = account.id
                bet.save()
                pooluserbet = PoolUserBet(pool, request.user, bet)
                matchbet.betlist.append(pooluserbet)

        matchbets.append(matchbet)

    return render(request, 'bet/mybets.html', {'body_id': 'mybets', 'events': events, 'event': event,  'matchbets': matchbets, 'user': request.user } )



def bets(request, poolid=1, eventid=1):
    context = RequestContext(request)

    # pool
    if poolid == None:
        pool = Pool.objects.filter(membership__user_id=request.user.id, active=True)[:1].get()
    else:
        pool = Pool.objects.get(id=poolid)

    # event
    if eventid == None:
        event = Event.objects.get(poolevent__pool_id=pool.id, active=True)
    else:
        event = Event.objects.get(id=eventid)

    # all pools where user is member
    pools = Pool.objects.filter(membership__user_id=request.user.id, active=True)

    # all events for choosen pool
    events = Event.objects.filter(poolevent__pool_id=pool.id, active=True)

    # all matches for choosen event
    matches = Match.objects.filter(event_id=event.id)

    # all bets for choosen pool and event
    matchbets = []
    for match in matches:
        matchbet = MatchBet(match)

        try:
            bets = Bet.objects.filter(match_id=match.id, account__membership__pool_id=pool.id)
            for bet in bets:
                pooluserbet = PoolUserBet()
                pooluserbet.pool = pool
                pooluserbet.user = request.user
                pooluserbet.bet = bet
                matchbet.betlist.append(pooluserbet)
        except Bet.DoesNotExist:
            continue

        matchbets.append(matchbet)

    return render(request, 'bet/bets.html', {'body_id': 'bets', 'pools': pools, 'pool': pool, 'events': events, 'event': event, 'matchbets': matchbets, 'user': request.user } )



def ranking(request):
    return render(request, 'bet/ranking.html', {'body_id': 'ranking'} )



def games(request, eventid=1):
    context = RequestContext(request)
    
    if eventid == None:
        event = Event.objects.filter(parent_id=None, active=True)[:1].get()
    else:
        event = Event.objects.get(id=eventid)

    events = Event.objects.all().filter(active=True)

    matches = Match.objects.all().filter(event_id=event.id)

    return render_to_response('bet/games.html', {'body_id': 'games', 'event': event, 'events': events, 'matches': matches, 'user': request.user }, context )



def do_bet(request):
    # Get the context from the request.
    context = RequestContext(request)

    # A HTTP POST?
    if request.method == 'POST':
        bet_id = request.POST['bet']
        url = request.POST['url']

        bet = Bet.objects.get(id=bet_id)

        if bet.accept() == False:
            match = Match.objects.get(id=bet.match_id)
            if match.status == 10:
                match.status = 20
                match.save()

            return HttpResponseRedirect(url)

        form = BetForm(request.POST, instance=bet)
        if form.is_valid():
            form.save(commit=True)
            return HttpResponseRedirect(url)
            # return HttpResponseRedirect("/bet/mybets/" + str(match.event_id))
        else:
            # The supplied form contained errors - just print them to the terminal.
            print form.errors
            return HttpResponse(form.errors)
    else:
        return HttpResponse("error")



def admin(request):
    # Get the context from the request.
    context = RequestContext(request)

    matches = Match.objects.filter(status=30)
    for match in matches:
        bets = Bet.objects.filter(match_id = match.id)
        for bet in bets:
            bet.rate()

    return render_to_response('bet/admin.html', {'body_id': 'admin', 'matches': matches}, context )
