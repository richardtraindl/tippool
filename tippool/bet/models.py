from django.db import models
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User, Group



#class User(models.Model):
#    username = models.CharField(max_length=30, unique=True)
#    password = models.CharField(max_length=30)
#    admin = models.BooleanField(default=False)



class Status(models.Model):
    key = models.IntegerField(null=False, unique=True)
    value = models.CharField(max_length=100, null=False)
    
    def __unicode__(self): 
        return self.value



class ScoreRule(models.Model):
    label = models.CharField(max_length=100, unique=True)
    one_two_draw = models.IntegerField(null=False, default=0)
    regular = models.IntegerField(null=False, default=0)
    overtime = models.IntegerField(null=False, default=0)
    penalties = models.IntegerField(null=False, default=0)

    def __unicode__(self): 
        return self.label



class Betpool(models.Model):
    label = models.CharField(max_length=100, unique=True)
    active = models.BooleanField(default=True)
    users = models.ManyToManyField(User, through='Membership')

    def __unicode__(self):
        return self.label



class Membership(models.Model):
    betpool = models.ForeignKey(Betpool)
    user = models.ForeignKey(User)
    admin = models.BooleanField(null=False, default=False)
    active = models.BooleanField(null=False, default=True)

    def __unicode__(self):
        return self.betpool.label + "/" + self.user.username 



class EventManager(models.Manager):
    def get_by_natural_key(self, label):
        return self.get(label=label)

class Event(models.Model):
    objects = EventManager()

    label = models.CharField(max_length=100, unique=True,  null=False)
    status = models.ForeignKey(Status)
    parent = models.ForeignKey('self', null=True)
    active = models.BooleanField(default=True)
    betpools = models.ManyToManyField(Betpool, through='PoolEvent')

    def __unicode__(self): 
        return self.label


class PoolEvent(models.Model):
    betpool = models.ForeignKey(Betpool)
    event = models.ForeignKey(Event)
    scorerule = models.ForeignKey(ScoreRule)

    def __unicode__(self):
        return self.betpool.label + '-' + self.event.label


class Account(models.Model):
    membership = models.ForeignKey(Membership)
    poolevent = models.ForeignKey(PoolEvent)
    rating = models.IntegerField(null=True)



class TeamManager(models.Manager):
    def get_by_natural_key(self, name):
        return self.get(name=name)

class Team(models.Model):
    objects = TeamManager()

    name = models.CharField(max_length=100, unique=True)
    logo = models.BinaryField()
    active = models.BooleanField(default=True)

    def __unicode__(self):
        return self.name



class Match(models.Model):
    event = models.ForeignKey(Event)
    begin = models.DateTimeField()
    status = models.ForeignKey(Status)
    has_overtime = models.BooleanField(null=False, default=False)
    has_penalties = models.BooleanField(null=False, default=False)
    teams = models.ManyToManyField(Team, through='Opponent')

    def __unicode__(self): 
        opp1 = Opponent.objects.get(match_id=self.id, rank=1)
        opp2 = Opponent.objects.get(match_id=self.id, rank=2)
        if opp1 == None or opp2 == None:
            return self.begin.strftime('%m.%d.%Y')
        else:
            return self.begin.strftime('%m.%d.%Y') + " - " + opp1.team.name + " : " + opp2.team.name



class Opponent(models.Model):
    match = models.ForeignKey(Match)
    team = models.ForeignKey(Team)
    rank = models.IntegerField(default=1)
    score_regular = models.IntegerField(null=True)
    score_overtime = models.IntegerField(null=True)
    score_penalties = models.IntegerField(null=True)


class Bet(models.Model):
    account= models.ForeignKey(Account)
    match= models.ForeignKey(Match)
    teams = models.ManyToManyField(Team, through='BetOpponent')
    overtime= models.BooleanField(null=False, default=False)
    penalties = models.BooleanField(null=False, default=False)
    rating = models.IntegerField(null=True)


class BetOpponent(models.Model):
    bet = models.ForeignKey(Bet)
    team = models.ForeignKey(Team)
    rank = models.IntegerField(default=1, unique=True)
    score_regular = models.IntegerField(null=False)
    score_overtime = models.IntegerField(null=True)
    score_penalties = models.IntegerField(null=True)


