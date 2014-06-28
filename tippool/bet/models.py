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



class Winner(object):
    def __init__(self, key=None, value=None):
        self.key = key
        self.value = value

    def __unicode__(self): 
        return self.value

winner_none  = Winner(0, "none")
winner_team1 = Winner(1, "team1")
winner_team2   = Winner(2, "team2")



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

    class Meta:
        unique_together = (("pool", "user"),)

    def __init__(self, *args, **kwargs):
        super(Membership, self).__init__(*args, **kwargs)
        events = Event.objects.filter(poolevent__pool_id=self.pool_id, active=True)
        for event in events:
            try:
                account = Account.objects.get(event_id=event.id, membership_id=self.id)
            except Account.DoesNotExist:
                account = Account()
                account.membership_id = self.id
                account.event_id = event.id
                account.save()

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

    class Meta:
        unique_together = (("pool", "event"),)

    def __init__(self, *args, **kwargs):
        super(PoolEvent, self).__init__(*args, **kwargs)
        memberships = Membership.objects.filter(pool_id=self.pool_id)
        for membership in memberships:
            try:
                account = Account.objects.get(event_id=self.event_id, membership_id=membership.id)
            except Account.DoesNotExist:
                account = Account.objects.get()
                account.membership_id = membership.id
                account.event_id = self.event_id
                account.save()

    def __unicode__(self):
        return self.pool.label + '-' + self.event.label



class AccountManager(models.Manager):
    def get_by_natural_key(self, name):
        return self.get(name=name)

class Account(models.Model):
    objects = AccountManager()

    membership = models.ForeignKey(Membership)
    event = models.ForeignKey(Event)
    rating = models.IntegerField(null=True)

    class Meta:
        unique_together = (("membership", "event"),)

    def __unicode__(self):
        return  self.membership.user.username + " / " + \
                self.membership.pool.label + " / " + \
                self.event.label



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
    status = models.IntegerField(null=False)
    has_overtime = models.BooleanField(null=False, default=False)
    has_penalties = models.BooleanField(null=False, default=False)
    team1 = models.ForeignKey(Team, related_name='match_team1')
    team1_score_regular = models.IntegerField(null=True, blank=True)
    team1_score_overtime = models.IntegerField(null=True, blank=True)
    team1_score_penalties = models.IntegerField(null=True, blank=True)
    team2 = models.ForeignKey(Team, related_name='match_team2')
    team2_score_regular = models.IntegerField(null=True, blank=True)
    team2_score_overtime = models.IntegerField(null=True, blank=True)
    team2_score_penalties = models.IntegerField(null=True, blank=True)
    winner = models.IntegerField(null=True, blank=True)

    class Meta:
        unique_together = (("event", "team1", "team2"),)

    def __unicode__(self): 
        return self.begin.strftime('%d.%m.%Y') + "/" + "/" + self.event.label  +  "/" + self.team1.name + " : " + self.team2.name




class BetManager(models.Manager):
    def get_by_natural_key(self, name):
        return self.get(name=name)

class Bet(models.Model):
    objects = BetManager()

    account= models.ForeignKey(Account)
    match= models.ForeignKey(Match)
    overtime= models.BooleanField(null=False, default=False)
    penalties = models.BooleanField(null=False, default=False)
    team1_score_regular = models.IntegerField(null=False)
    team1_score_overtime = models.IntegerField(null=True, blank=True)
    team1_score_penalties = models.IntegerField(null=True, blank=True)
    team2_score_regular = models.IntegerField(null=False)
    team2_score_overtime = models.IntegerField(null=True, blank=True)
    team2_score_penalties = models.IntegerField(null=True, blank=True)
    winner = models.IntegerField(null=True, blank=True)
    rating = models.IntegerField(null=True, blank=True)

    class Meta:
        unique_together = (("account", "match"),)  

    def __unicode__(self):
        return  self.account.membership.user.username + " / " + \
                self.account.membership.pool.label + " / " + \
                self.account.event.label + " / " + \
                self.match.team1.name + " - " + \
                self.match.team2.name

