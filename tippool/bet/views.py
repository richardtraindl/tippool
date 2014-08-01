# -*- coding: utf-8 -*-

from django.shortcuts import render, render_to_response
from django.http import HttpResponseRedirect, HttpResponse
from django.template import RequestContext
from itertools import chain
from django.db import models
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
    def __init__(self, event=None):
        self.event = event
        self.sublist = []

class MyRanking(object):
    def __init__(self, pool=None, event=None, user=None, account=None):
        self.pool = pool
        self.event = event
        self.user = user
        self.account = account



def mybets(request, eventid=None):
    context = RequestContext(request)

    # all pools where user is member
    pools = Pool.objects.filter(membership__user_id=request.user.id, active=1)
    if len(pools) == 0:
        # todo redirect to error page
        return HttpResponseRedirect('/bet/admin')

    # all events where user is registered through pools
    events = Event.objects.filter(models.Q(poolevent__pool__membership__user_id=request.user.id), models.Q(active=1), (models.Q(event_type=10) | models.Q(event_type=20))).distinct()
    if len(events) == 0:
        # todo redirect to error page
        return HttpResponseRedirect('/bet/admin')

    myevents = []
    for event in events:
        myevent = MyEvent()
        myevent.event = event
        if event.event_type == 20:
            myevent.sublist = Event.objects.filter(parent_id=event.id, active=1)
        myevents.append(myevent)

    # event
    if eventid == None:
        if myevents[0].event.event_type == 20:
            event = myevents[0].sublist[0]
        else:
            event = myevents[0]
    else:
        event = Event.objects.get(id=eventid)

    if event == None:
        # todo redirect to error page
        return HttpResponseRedirect('/bet/admin')


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

    if pool == None:
        # todo redirect to error page
        return HttpResponseRedirect('/bet/admin')


    # event/events
    events = Event.objects.filter(models.Q(poolevent__pool_id=pool.id), models.Q(active=1), (models.Q(event_type=10) | models.Q(event_type=20))).distinct()
    if len(events) == 0:
        # todo redirect to error page
        return HttpResponseRedirect('/bet/admin')

    myevents = []
    for event in events:
        myevent = MyEvent()
        myevent.event = event
        if event.event_type == 20:
            myevent.sublist = Event.objects.filter(parent_id=event.id, active=1)
        myevents.append(myevent)

    if eventid == None:
        if myevents[0].event.event_type == 20:
            event = myevents[0].sublist[0]
        else:
            event = myevents[0]
    else:
        event = Event.objects.get(id=eventid)

    if event == None:
        # todo redirect to error page
        return HttpResponseRedirect('/bet/admin')


    # all pools where user is member
    pools = Pool.objects.filter(membership__user_id=request.user.id, active=1)


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
            bet.calc_points()

    return render_to_response('bet/admin.html', {'body_id': 'admin', 'matches': matches}, context )



def calc_points(request, eventid=None):
    context = RequestContext(request)

    if eventid == None:
        # todo redirect to error page
        return HttpResponseRedirect('/bet/mybets')
    else:
        event = Event.objects.get(id=eventid)

    if event == None:
        # todo redirect to error page
        return HttpResponseRedirect('/bet/mybets')

    pools = Pool.objects.filter(poolevent__event_id=event.id)

    for pool in pools:
        accounts = Account.objects.filter(event_id=event.id, membership__pool_id=pool.id)
        for account in accounts:
            account.calc_points()
        #if event.event_type == 10:
        #    for account in accounts:
        #        account.calc_points()
        #if event.event_type == 20:
        #    pts = 0
        #    for account in accounts:
        #        subaccounts = Account.objects.filter(membership_id=account.membership_id)
        #        for subaccount in subaccounts:
        #            pts += subaccount.calc_points()
        #        account.points = pts
        #        account.save()

    return HttpResponseRedirect('/bet/mybets')



def ranking(request, poolid=None, eventid=None):
    context = RequestContext(request)

    # pool/pools
    pools = Pool.objects.filter(active=1)
    if poolid == None:
        if len(pools) == 0:
            # todo redirect to error page
            return HttpResponseRedirect('/bet/admin')
        else:
            pool = pools[0]
    else:
        pool = Pool.objects.get(id=poolid)


    # event/events
    events = Event.objects.filter(models.Q(poolevent__pool_id=pool.id), models.Q(active=1), (models.Q(event_type=10) | models.Q(event_type=20))).distinct()
    myevents = []
    for event in events:
        myevent = MyEvent()
        myevent.event = event
        if event.event_type == 20:
            myevent.sublist = Event.objects.filter(parent_id=event.id, active=1)
        myevents.append(myevent)

    if eventid == None:
        if len(events) == 0:
            # todo redirect to error page
            return HttpResponseRedirect('/bet/admin')
        else:
            event = myevents[0].event
    else:
        event = Event.objects.get(id=eventid)


    try:
        accounts = Account.objects.filter(event_id=event.id, membership__pool_id=pool.id)
    except Account.DoesNotExist:
        return HttpResponseRedirect('/bet/mybets')

    myrankings = []
    for account in accounts:
        # account.calc_points()
        membership = Membership.objects.get(id=account.membership_id)
        user = User.objects.get(id=membership.user_id)
        myranking = MyRanking(pool, event, user, account)
        myrankings.append(myranking)

    rankings = sorted(myrankings, key=lambda myranking: myranking.account.points, reverse=True)

    return render(request, 'bet/ranking.html', {'body_id': 'ranking', 'pools': pools, 'pool': pool, 'myevents': myevents, 'event': event, 'myrankings': rankings } )

