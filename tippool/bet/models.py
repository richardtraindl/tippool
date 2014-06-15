from django.db import models
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User, Group



#class User(models.Model):
#    username = models.CharField(max_length=30, unique=True)
#    password = models.CharField(max_length=30)
#    admin = models.BooleanField(default=False)



class Status(object):
    def __init__(self, key=None, value=None):
        self.key = key
        self.value = value

    def __unicode__(self): 
        return self.value

status_scheduled = Status(10, "scheduled")
status_running   = Status(20, "running")
status_finished  = Status(30, "finished")
status_cancelled = Status(40, "cancelled")



class ScoreRule(models.Model):
    label = models.CharField(max_length=100, unique=True)
    one_two_draw = models.IntegerField(null=False, default=0)
    regular = models.IntegerField(null=False, default=0)
    overtime = models.IntegerField(null=False, default=0)
    penalties = models.IntegerField(null=False, default=0)

    def __unicode__(self): 
        return self.label



class Pool(models.Model):
    label = models.CharField(max_length=100, unique=True)
    active = models.BooleanField(default=True)
    users = models.ManyToManyField(User, through='Membership')

    def __unicode__(self):
        return self.label



class Membership(models.Model):
    pool = models.ForeignKey(Pool)
    user = models.ForeignKey(User)
    admin = models.BooleanField(null=False, default=False)
    active = models.BooleanField(null=False, default=True)

    def __unicode__(self):
        return self.pool.label + "/" + self.user.username 



class EventManager(models.Manager):
    def get_by_natural_key(self, label):
        return self.get(label=label)

class Event(models.Model):
    objects = EventManager()

    label = models.CharField(max_length=100, unique=True,  null=False)
    status = models.IntegerField(null=False)
    parent = models.ForeignKey('self', null=True)
    active = models.BooleanField(default=True)
    pools = models.ManyToManyField(Pool, through='PoolEvent')

    def __unicode__(self): 
        return self.label


class PoolEvent(models.Model):
    pool = models.ForeignKey(Pool)
    event = models.ForeignKey(Event)
    scorerule = models.ForeignKey(ScoreRule)

    def __unicode__(self):
        return self.pool.label + '-' + self.event.label



class AccountManager(models.Manager):
    def get_by_natural_key(self, name):
        return self.get(name=name)

class Account(models.Model):
    objects = AccountManager()

    membership = models.ForeignKey(Membership)
    poolevent = models.ForeignKey(PoolEvent)
    rating = models.IntegerField(null=True)

    def __unicode__(self):
        return  self.poolevent.pool.label + " / " + \
                self.poolevent.event.label + " / " + \
                self.membership.pool.label + " / " + \
                self.membership.user.username



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



class ScoreManager(models.Manager):
    def get_by_natural_key(self, id):
        return self.get(id=id)

class Score(models.Model):
    objects = ScoreManager()

    regular = models.IntegerField(null=True)
    overtime = models.IntegerField(null=True)
    penalties = models.IntegerField(null=True)

    def __unicode__(self):
        return str(self.id)



class Match(models.Model):
    event = models.ForeignKey(Event)
    begin = models.DateTimeField()
    status = models.IntegerField(null=False)
    has_overtime = models.BooleanField(null=False, default=False)
    has_penalties = models.BooleanField(null=False, default=False)
    team1 = models.ForeignKey(Team, related_name='match_team1')
    team1_score = models.ForeignKey(Score, related_name='match_team1_score')
    team2 = models.ForeignKey(Team, related_name='match_team2')
    team2_score = models.ForeignKey(Score, related_name='match_team2_score')

    def __unicode__(self): 
        return self.begin.strftime('%m.%d.%Y') + " - " + self.team1.name + " : " + self.team2.name




class BetManager(models.Manager):
    def get_by_natural_key(self, name):
        return self.get(name=name)

class Bet(models.Model):
    objects = BetManager()

    account= models.ForeignKey(Account)
    match= models.ForeignKey(Match)
    overtime= models.BooleanField(null=False, default=False)
    penalties = models.BooleanField(null=False, default=False)
    rating = models.IntegerField(null=True)
    team1_score = models.ForeignKey(Score, related_name='bet_team1_score')
    team2_score = models.ForeignKey(Score, related_name='bet_team2_score')

    def __unicode__(self):
        return  self.account.poolevent.pool.label + " / " + \
                self.account.poolevent.event.label + " / " + \
                self.match.team1.name + " - " + \
                self.match.team2.name + " / " + \
                self.account.membership.user.username

