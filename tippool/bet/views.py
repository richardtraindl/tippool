from django.shortcuts import render, render_to_response
from django.http import HttpResponseRedirect, HttpResponse
from django.template import RequestContext
from itertools import chain
from django.shortcuts import get_object_or_404
from bet.models import Event, EventManager, Match, Team, Membership, Pool, PoolEvent, Account, Bet
from bet.forms import BetForm



def add_bet(request):
    # Get the context from the request.
    context = RequestContext(request)

    # A HTTP POST?
    if request.method == 'POST':
        form = BetForm(request.POST)

        # Have we been provided with a valid form?
        if form.is_valid():
            # Save the new category to the database.
            form.save(commit=True)

            # Now call the index() view.
            # The user will be shown the homepage.
            return bets(request)
        else:
            # The supplied form contained errors - just print them to the terminal.
            print form.errors
    else:
        # If the request was not a POST, display the form to enter details.
        form = BetForm()

    # Bad form (or form details), no form supplied...
    # Render the form with error messages (if any).
    return render_to_response('bet/add_bet.html', {'form': form}, context)



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

