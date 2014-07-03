# -*- coding: utf-8 -*-

from django import forms
from django.core.exceptions import ValidationError
from bet.models import Bet, Match



class BetForm(forms.ModelForm):
    class Meta:
        model = Bet
        # 'account', 'match', \
        fields = ( 'team1_score_regular', 'team1_score_overtime', 'team1_score_penalties', \
                   'team2_score_regular', 'team2_score_overtime', 'team2_score_penalties')

