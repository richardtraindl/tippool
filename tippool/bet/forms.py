# -*- coding: utf-8 -*-

from django import forms
from django.forms import ModelForm
from django.core.exceptions import ValidationError
from bet.models import Bet, Match



class BetForm(ModelForm):
    class Meta:
        model = Bet

        fields = ( 'team1_score_regular', 'team1_score_overtime', 'team1_score_penalties', 'team2_score_regular', 'team2_score_overtime', 'team2_score_penalties')
    
    def is_valid(self):
        # run the parent validation first
        valid = super(BetForm, self).is_valid()
 
        # we're done now if not valid
        if not valid:
            return valid

        team1_score_regular = self.cleaned_data['team1_score_regular']
        team2_score_regular = self.cleaned_data['team2_score_regular']
        if team1_score_regular == None or team2_score_regular == None:
            return False
 
        if self.instance.overtime:
            team1_score_overtime = self.cleaned_data['team1_score_overtime']
            team2_score_overtime = self.cleaned_data['team2_score_overtime']
            if team1_score_overtime == None or team2_score_overtime == None:
                return False

        if self.instance.penalties:
            team1_score_penalties = self.cleaned_data['team1_score_penalties']
            team2_score_penalties = self.cleaned_data['team2_score_penalties']
            if team1_score_penalties == None or team2_score_penalties == None:
                return False

        return True

