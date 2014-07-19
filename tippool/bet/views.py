# -*- coding: utf-8 -*-

from django.shortcuts import render, render_to_response
from django.http import HttpResponseRedirect, HttpResponse
from django.template import RequestContext
from itertools import chain
from django.shortcuts import get_object_or_404
import datetime
from dateutil.tz import tzlocal
from django.contrib.auth.models import User, Group
from bet.models import Event, EventManager, Match, Team, Membership, Pool, PoolEvent, Account, Bet
from bet.forms import BetForm



class MyBet(object):
    def __init__(self, pool=None, user=None, frmbet=None):
        self.pool = pool
        self.user = user
        self.frmbet = frmbet

class MatchBet(object):
    def __init__(self, match=None):
        self.match = match
        self.mybetlist = []

class MyEvent(object):
    def __init__(self, parent=None):
        self.parent = parent
        self.sublist = []

class MyRanking(object):
    def __init__(self, pool=None, event=None, user=None, account=None):
        self.pool = pool
        self.event = event
        self.user = user
        self.account = account



def mybets(request, eventid=None):
    context = RequestContext(request)
    print(eventid)

    # all pools where user is member
    pools = Pool.objects.filter(membership__user_id=request.user.id, active=1)

    # all events where user is registered through pools
    superevents = Event.objects.filter(poolevent__pool__membership__user_id=request.user.id, \
                                        active=1, is_super=1).distinct()
    myevents = []
    for event in superevents:
        myevent = MyEvent()
        myevent.parent = event
        myevent.sublist = Event.objects.filter(parent_id=event.id, active=1)
        myevents.append(myevent)
    
    standaloneevents = Event.objects.filter(poolevent__pool__membership__user_id=request.user.id, \
                                    active=1, is_super=0).exclude(parent_id__isnull=False).distinct()
    for event in standaloneevents:
        myevent = MyEvent()
        myevent.parent = None
        myevent.sublist.append(event)
        myevents.append(myevent)

    # event
    if eventid == None:
        event = myevents[0].sublist[0]
    else:
        event = Event.objects.get(id=eventid)

    # all matches for choosen event
    matches = Match.objects.filter(event_id=event.id)

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
                mybet = MyBet(pool, request.user, BetForm(instance=bet))
                #mybet.pool = pool
                #mybet.user = request.user
                #mybet.frmbet = BetForm(instance=bet)
                matchbet.mybetlist.append(mybet)
            except Bet.DoesNotExist:
                bet = Bet()
                bet.match_id = match.id
                bet.account_id = account.id
                bet.save()
                mybet = MyBet(pool, request.user, BetForm(instance=bet))
                matchbet.mybetlist.append(mybet)
        
        matchbets.append(matchbet)

    return render(request, 'bet/mybets.html', {'body_id': 'mybets', 'myevents': myevents, 'event': event,  'matchbets': matchbets, 'user': request.user } )



def bets(request, poolid=None, eventid=None):
    context = RequestContext(request)

    # pool
    if poolid == None:
        pool = Pool.objects.filter(membership__user_id=request.user.id, active=True)[:1].get()
    else:
        pool = Pool.objects.get(id=poolid)

    # all events for choosen pool
    superevents = Event.objects.filter(poolevent__pool_id=pool.id, active=1, \
                        is_super=1).distinct()
    myevents = []
    for event in superevents:
        myevent = MyEvent()
        myevent.parent = event
        myevent.sublist = Event.objects.filter(parent_id=event.id, active=1)
        myevents.append(myevent)

    standaloneevents = Event.objects.filter(poolevent__pool_id=pool.id, active=1, \
                            is_super=0).exclude(parent_id__isnull=False).distinct()
    for event in standaloneevents:
        myevent = MyEvent()
        myevent.parent = None
        myevent.sublist.append(event)
        myevents.append(myevent)

    # event
    if eventid == None:
        # event = Event.objects.filter(poolevent__pool_id=pool.id, active=True)[:1].get()
        event = myevents[0].sublist[0]
    else:
        event = Event.objects.get(id=eventid)

    # all pools where user is member
    pools = Pool.objects.filter(membership__user_id=request.user.id, active=1)

    # all events for choosen pool
    # events = Event.objects.filter(poolevent__pool_id=pool.id, active=True)

    # all matches for choosen event
    matches = Match.objects.filter(event_id=event.id)

    # all bets for choosen pool and event
    matchbets = []
    for match in matches:
        matchbet = MatchBet(match)

        try:
            bets = Bet.objects.filter(match_id=match.id, account__membership__pool_id=pool.id)
            for bet in bets:
                mybet = MyBet()
                mybet.pool = pool
                # mybet.user = request.user
                mybet.user = User.objects.get(membership__account__id=bet.account_id)
                mybet.frmbet = BetForm(instance=bet)
                matchbet.mybetlist.append(mybet)
        except Bet.DoesNotExist:
            continue

        matchbets.append(matchbet)

    return render(request, 'bet/bets.html', {'body_id': 'bets', 'pools': pools, 'pool': pool, 'myevents': myevents, 'event': event, 'matchbets': matchbets, 'user': request.user } )



def do_bet(request):
    # Get the context from the request.
    context = RequestContext(request)

    # A HTTP POST?
    if request.method == 'POST':
        bet_id = request.POST['bet']
        url = request.POST['url']

        bet = Bet.objects.get(id=bet_id)

        if bet.is_acceptable() == False:
            match = Match.objects.get(id=bet.match_id)
            if match.status == 10:
                match.status = 20
                match.save()

            return HttpResponseRedirect(url)

        form = BetForm(request.POST, instance=bet)
        if form.is_valid():
            form.save(commit=True)
            return HttpResponseRedirect(url)
        else:
            error_list = "<ul>"
            for field in form:
                if len(field.errors) > 0:
                    error_list += "<li>"
                    error_list += str(field.name)
                    error_list += str(field.errors)
                    error_list += "</li>"
            error_list += "</ul>"

            msg = "<html><body>\
                    <h2>Fehler bei Tippabgabe:</h2>" + \
                    error_list + \
                    "<p><a href=" + url + ">back</a></p>\
                   </body></html>"
            return HttpResponse(msg)
    else:
        return HttpResponse("error")



def admin(request):
    # Get the context from the request.
    context = RequestContext(request)

    matches = Match.objects.filter(id=30)
    for match in matches:
        bets = Bet.objects.filter(match_id = match.id)
        for bet in bets:
            bet.rate()

    return render_to_response('bet/admin.html', {'body_id': 'admin', 'matches': matches}, context )



def calc_points(request, req_username=None):
    context = RequestContext(request)

    # users
    users = []
    if req_username == None:
        users = User.objects.filter()
    else:
        try:
            users.append(User.objects.get(username=req_username))
        except User.DoesNotExist:
            users = User.objects.filter()

    for user in users:
        bets = Bet.objects.filter(account__membership__user_id=user.id)

        for bet in bets:
            bet.calc_points()

    return HttpResponseRedirect('/bet/mybets')



def ranking(request, poolid=None, eventid=None):
    context = RequestContext(request)

    if poolid == None:
        return HttpResponseRedirect('/bet/ranking')
    else:
        pool = Pool.objects.get(id=poolid)
        pools = Pool.objects.filter()

    if eventid == None:
        return HttpResponseRedirect('/bet/ranking')
    else:
        event = Event.objects.get(id=eventid)
        events = Event.objects.filter()

    try:
        accounts = Account.objects.filter(event_id=event.id, membership__pool_id=pool.id)
    except Account.DoesNotExist:
        return HttpResponseRedirect('/bet/ranking')

    myrankings = []
    for account in accounts:
        bets = Bet.objects.filter(account_id=account.id)
        pts = 0

        for bet in bets:
            bet.calc_points()
            pts += bet.points

        account.points = pts
        membership = Membership.objects.get(id=account.membership_id)
        user = User.objects.get(id=membership.user_id)
        myranking = MyRanking(pool, event, user, account)
        myrankings.append(myranking)

    rankings = sorted(myrankings, key=lambda myranking: myranking.account.points, reverse=True)

    return render(request, 'bet/ranking.html', {'body_id': 'ranking', 'pools': pools, 'pool': pool, 'events': events, 'event': event, 'myrankings': rankings } )

