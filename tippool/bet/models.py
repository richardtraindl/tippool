from django.db import models
from django.contrib.auth.models import User, Group
from django.core.urlresolvers import reverse
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models.signals import post_save
import datetime
from dateutil.tz import tzlocal



class Status(models.Model):
    key = models.IntegerField(null=False, unique=True)
    value = models.CharField(max_length=20, unique=True)

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



class Pool(models.Model):
    label = models.CharField(max_length=100, unique=True)
    active = models.BooleanField(default=True)
    users = models.ManyToManyField(User, through='Membership')
    scorerule = models.ForeignKey(ScoreRule)

    def __unicode__(self):
        return self.label



class Membership(models.Model):
    pool = models.ForeignKey(Pool)
    user = models.ForeignKey(User)
    admin = models.BooleanField(null=False, default=False)
    active = models.BooleanField(null=False, default=True)

    class Meta:
        unique_together = (("pool", "user"),)

    def __unicode__(self):
        return self.pool.label + "/" + self.user.username 

    @staticmethod
    def create_accounts(sender, instance, **kwargs):
        try:
            events = Event.objects.filter(poolevent__pool_id=instance.pool_id, active=True)
        except Event.DoesNotExist:
            return

        for event in events:
            try:
                account = Account.objects.get(membership_id=instance.id, event_id=event.id)
            except Account.DoesNotExist:
                account = Account(instance.id, event.id, None)
                account.membership_id = instance.id
                account.event_id = event.id
                account.save()

post_save.connect(Membership.create_accounts, sender=Membership)



class EventManager(models.Manager):
    def get_by_natural_key(self, label):
        return self.get(label=label)

class Event(models.Model):
    objects = EventManager()

    pools = models.ManyToManyField(Pool, through='PoolEvent')
    is_super = models.BooleanField(null=False, default=False)
    parent = models.ForeignKey('self', null=True, blank=True)
    label = models.CharField(max_length=100, unique=True,  null=False)
    active = models.BooleanField(default=True)

    def __unicode__(self): 
        return self.label


class PoolEvent(models.Model):
    pool = models.ForeignKey(Pool)
    event = models.ForeignKey(Event)

    class Meta:
        unique_together = (("pool", "event"),)

    @staticmethod
    def create_accounts(sender, instance, **kwargs):
        memberships = Membership.objects.filter(pool_id=instance.pool_id)
        for membership in memberships:
            try:
                account = Account.objects.get(event_id=instance.event_id, membership_id=membership.id)
            except Account.DoesNotExist:
                account = Account()
                account.membership_id = membership.id
                account.event_id = instance.event_id
                account.save()

    def __unicode__(self):
        return self.pool.label + '-' + self.event.label

post_save.connect(PoolEvent.create_accounts, sender=PoolEvent)



class AccountManager(models.Manager):
    def get_by_natural_key(self, name):
        return self.get(name=name)

class Account(models.Model):
    objects = AccountManager()

    event = models.ForeignKey(Event)
    membership = models.ForeignKey(Membership)
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
    status = models.ForeignKey(Status)
    has_overtime = models.BooleanField(null=False, default=False)
    has_penalties = models.BooleanField(null=False, default=False)
    team1 = models.ForeignKey(Team, related_name='match_team1')
    team1_score_regular = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(99)])
    team1_score_overtime = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(99)])
    team1_score_penalties = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(99)])
    team2 = models.ForeignKey(Team, related_name='match_team2')
    team2_score_regular = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(99)])
    team2_score_overtime = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(99)])
    team2_score_penalties = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(99)])

    class Meta:
        unique_together = (("event", "team1", "team2"),)

    def __unicode__(self): 
        return self.begin.strftime('%d.%m.%Y') + "/" + "/" + self.event.label  +  "/" + self.team1.name + " : " + self.team2.name

    def get_one_two_draw(self):
        if self.status_id != 30 or self.team1_score_regular == None or self.team2_score_regular == None:
            return None
        elif self.team1_score_regular > self.team2_score_regular:
            return 1
        elif self.team1_score_regular < self.team2_score_regular:
            return 2
        else:
            return 0



class BetManager(models.Manager):
    def get_by_natural_key(self, name):
        return self.get(name=name)

class Bet(models.Model):
    objects = BetManager()

    match= models.ForeignKey(Match)
    account= models.ForeignKey(Account)
    overtime= models.BooleanField(null=False, default=False)
    penalties = models.BooleanField(null=False, default=False)
    team1_score_regular = models.IntegerField(null=True, blank=False, validators=[MinValueValidator(0), MaxValueValidator(99)])
    team1_score_overtime = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(99)])
    team1_score_penalties = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(99)])
    team2_score_regular = models.IntegerField(null=True, blank=False, validators=[MinValueValidator(0), MaxValueValidator(99)])
    team2_score_overtime = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(99)])
    team2_score_penalties = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(99)])
    rating = models.IntegerField(null=True, blank=True)

    class Meta:
        unique_together = (("account", "match"),)  


    def __unicode__(self):
        return  self.account.membership.user.username + " / " + \
                self.account.membership.pool.label + " / " + \
                self.account.event.label + " / " + \
                self.match.team1.name + " - " + \
                self.match.team2.name


    def get_one_two_draw(self):
        if self.team1_score_regular == None or self.team2_score_regular == None:
            return None
        if self.team1_score_regular > self.team2_score_regular:
            return 1
        elif self.team1_score_regular < self.team2_score_regular:
            return 2
        else:
            return 0


    def accept(self):
        match = Match.objects.get(id=self.match_id)

        return match.status_id == 10 and datetime.datetime.now(tzlocal()) < match.begin


    def rate(self):
        score = 0
        b_one_two_draw = self.get_one_two_draw()
        
        match = Match.objects.get(id=self.match_id)
        
        m_one_two_draw = match.get_one_two_draw()

        if b_one_two_draw == None or m_one_two_draw == None:
            self.rating = score
            return None

        account = Account.objects.get(id=self.account_id)
        membership = Membership.objects.get(id=account.membership_id)
        pool = Pool.objects.get(id=membership.pool_id)
        scorerule = ScoreRule.objects.get(id=pool.scorerule_id)

        if b_one_two_draw == m_one_two_draw:
            score += scorerule.one_two_draw

            if self.result_equal("regular"):
                score += scorerule.regular
            if match.has_overtime:
                if self.result_equal("overtime"):
                    score += scorerule.overtime
            if match.has_penalties:
                if self.result_equal("penalties"):
                    score += scorerule.penalties

        self.rating = score
        self.save()
        return score


    def result_equal(self, _switch):
        match = Match.objects.get(id=self.match_id)

        if _switch == "regular":
            return self.team1_score_regular == match.team1_score_regular and \
                    self.team2_score_regular == match.team2_score_regular
        elif _switch == "overtime":
            return self.team1_score_overtime == match.team1_score_overtime and \
                    self.team2_score_overtime == match.team2_score_overtime
        elif _switch == "penalties":
            return self.team1_score_penalties == match.team1_score_penalties and \
                    self.team2_score_penalties == match.team2_score_penalties
        else:
            return False

