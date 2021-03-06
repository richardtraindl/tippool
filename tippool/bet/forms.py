# -*- coding: utf-8 -*-

from django import forms
from django.forms import ModelForm
from django.core.exceptions import ValidationError
from bet.models import Bet, Match



class BetForm(ModelForm):
    class Meta:
        model = Bet

        fields = ( 'team1_score_regular', 'team1_score_overtime', 'team1_score_penalties', 'team2_score_regular', 'team2_score_overtime', 'team2_score_penalties', 'points')
    
    def is_valid(self):
        # run the parent validation first
        valid = super(BetForm, self).is_valid()
 
        # we're done now if not valid
        if not valid:
            return valid

        match = Match.objects.get(id=self.instance.match_id)

        team1_score_regular = self.cleaned_data['team1_score_regular']
        team2_score_regular = self.cleaned_data['team2_score_regular']
        if team1_score_regular == None or team2_score_regular == None:
            self._errors['team1_score_regular'] = ': number expected'
            self._errors['team2_score_regular'] = ': number expected'
            return False
 
        if match.has_overtime == 1 and (team1_score_regular == team2_score_regular):
            team1_score_overtime = self.cleaned_data['team1_score_overtime']
            team2_score_overtime = self.cleaned_data['team2_score_overtime']
            if team1_score_overtime == None or team2_score_overtime == None:
                self._errors['team1_score_overtime'] = ': number expected'
                self._errors['team2_score_overtime'] = ': number expected'
                return False

            if match.has_penalties == 1 and (team1_score_overtime == team2_score_overtime):
                team1_score_penalties = self.cleaned_data['team1_score_penalties']
                team2_score_penalties = self.cleaned_data['team2_score_penalties']
                if team1_score_penalties == None or team2_score_penalties == None:
                    self._errors['team1_score_penalties'] = ': number expected'
                    self._errors['team2_score_penalties'] = ': number expected'
                    return False

        return True

