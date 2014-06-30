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



class MatchForm(forms.ModelForm):
    title = forms.CharField(max_length=128, help_text="Please enter the title of the page.")
    url = forms.URLField(max_length=200, help_text="Please enter the URL of the page.")
    views = forms.IntegerField(widget=forms.HiddenInput(), initial=0)

    class Meta:
        # Provide an association between the ModelForm and a model
        model = Match

        # What fields do we want to include in our form?
        # This way we don't need every field in the model present.
        # Some fields may allow NULL values, so we may not want to include them...
        # Here, we are hiding the foreign key.
        fields = ('title', 'url', 'views')