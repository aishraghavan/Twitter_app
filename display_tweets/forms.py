from django import forms
from display_tweets.models import TwitterSearch


class TwitterSearchForm(forms.ModelForm):
    class Meta:
        model = TwitterSearch
        fields = ['phrase']