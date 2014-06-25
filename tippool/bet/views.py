from django.shortcuts import render, render_to_response
from django.http import HttpResponseRedirect, HttpResponse
from django.template import RequestContext
from itertools import chain
from django.shortcuts import get_object_or_404
from bet.models import Event, EventManager, Match, Team, Membership, Pool, PoolEvent, Account, Bet
from bet.forms import BetForm




class MatchBets(object):
    def __init__(self, match=None):
        self.match = match
        self.betlist = []

    def add_bet(self, bets):
        for bet in bets:
            self.betlist.append(bet)


def mybets(request, eventid=1):
    context = RequestContext(request)

    # all pools where user is member
    pools = Pool.objects.filter(membership__user__id=request.user.id, active=True)

    # event
    if eventid == None:
        event = Event.objects.get(poolevent__pool_id=pools[0].id, active=True)
    else:
        event = Event.objects.get(id=eventid)


    # all events for choosen pool
    events = Event.objects.filter(poolevent__pool__membership__user_id=request.user.id, active=True)

    # all matches for choosen event
    matches = Match.objects.all().filter(event_id=event.id)

    # all bets for choosen pool and event
    match_bets = []
    for match in matches:
        match_bet = MatchBets(match)

        for pool in pools:
            try:
                membership = Membership.objects.get(pool_id=pool.id, user_id=request.user.id)
                account= Account.objects.get(event_id=match.event_id, membership_id=membership.id)
                bet = Bet.objects.get(match_id=match.id, account_id=account.id)
                match_bet.betlist.append(bet)
            except Bet.DoesNotExist:
                bet = Bet()
                bet.account_id = account.id
                bet.match_id = match.id
                bet.overtime = False
                bet.penalties = False
                bet.team1_score_regular = 0
                bet.team2_score_regular = 0
                bet.save()
                match_bet.betlist.append(bet)
                continue

        match_bets.append(match_bet)

    return render(request, 'bet/mybets.html', {'body_id': 'mybets', 'events': events, 'event': event,  'match_bets': match_bets } )



def bets(request, poolid=1, eventid=1):
    context = RequestContext(request)

    # pool
    if poolid == None:
        pool = Pool.objects.filter(membership__user__id=request.user.id, active=True)[:1].get()
    else:
        pool = Pool.objects.get(id=poolid)

    # event
    if eventid == None:
        event = Event.objects.get(poolevent__pool_id=pool.id, active=True)
    else:
        event = Event.objects.get(id=eventid)

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
            bets = Bet.objects.filter(match__id=match.id, account__membership__pool__id=pool.id)
            match_bet.add_bet(bets)
        except Bet.DoesNotExist:
            continue
            
        match_bets.append(match_bet)

    return render(request, 'bet/bets.html', {'body_id': 'bets', 'pool': pool, 'pools': pools, 'event': event, 'events': events, 'match_bets': match_bets, 'user': request.user } )



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

    pool = Pool.objects.filter(membership__user__id=request.user.id, active=True)[:1].get()

    return render_to_response('bet/games.html', {'body_id': 'games', 'event': event, 'events': events, 'matches': matches, 'pool': pool, 'user': request.user }, context )



def add_bet2(request, poolid=1, matchid=1):
    # Get the context from the request.
    context = RequestContext(request)

    # A HTTP POST?
    if request.method == 'POST':
        pool_id = request.POST['pool']
        match_id = request.POST['match']
        bet_id = request.POST['bet']

        match = Match.objects.get(id=match_id)
        bet = Bet.objects.get(id=bet_id)

        form = BetForm(request.POST, instance=bet)
        if form.is_valid():
            form.save(commit=True)
            return HttpResponseRedirect("/bet/bets/" + str(pool_id) + "/" + str(match.event_id))
        else:
            # The supplied form contained errors - just print them to the terminal.
            print form.errors
            return HttpResponse(form.errors)
    else:
        # If the request was not a POST, display the form to enter details.
        form = BetForm()

        if matchid == None:
            match = Match.objects.filter(status=10, event__poolevent__membership__user__id=request.user.id)[:1].get()
        else:
            match = Match.objects.get(id=matchid)

        pools = Pool.objects.filter(membership__user__id=request.user.id, poolevent__event__match__id=match.id)

        if poolid == None:
            pool = pools[0]
        else:
            pool = Pool.objects.get(id=poolid)

        try:
            membership = Membership.objects.get(pool_id=pool.id, user_id=request.user.id)
        except Membership.DoesNotExist:
            print("error membership")
            return HttpResponse("<html></html>")

        try:
            account = Account.objects.get(membership_id=membership.id, event__match__id=match.id)
        except Account.DoesNotExist:
            event = Event.objects.get(id=match.event_id)
            account = Account(membership.id, event.id, None)
            account.save

        try:
            bet = Bet.objects.get(account_id=account.id, match_id=match.id)
        except Bet.DoesNotExist:
            bet = Bet(account.id, match.id, False, False, 0, None, None, 0, None, None, None, None)
            bet.account_id = account.id
            bet.match_id = match.id
            bet.team1_score_regular = 0
            bet.team2_score_regular = 0
            bet.save()

        return render_to_response('bet/add_bet.html', {'form': form, 'body_id': 'add_bet', 'bet': bet, 'match': match, 'pool': pool }, context)


def add_bet(request, betid=1):
    # Get the context from the request.
    context = RequestContext(request)

    # A HTTP POST?
    if request.method == 'POST':
        bet_id = request.POST['bet']
        match_id = request.POST['match']

        bet = Bet.objects.get(id=bet_id)
        match = Match.objects.get(id=match_id)

        form = BetForm(request.POST, instance=bet)
        if form.is_valid():
            form.save(commit=True)
            return HttpResponseRedirect("/bet/mybets/" + str(match.event_id))
        else:
            # The supplied form contained errors - just print them to the terminal.
            print form.errors
            return HttpResponse(form.errors)
    else:
        # If the request was not a POST, display the form to enter details.
        form = BetForm()

        if betid == None:
            return HttpResponse(form.errors)
        else:
            bet = Bet.objects.get(id=betid)

        match = Match.objects.get(id=bet.match_id)

        return render_to_response('bet/add_bet.html', {'form': form, 'body_id': 'add_bet', 'bet': bet, 'match': match }, context)
