from django.views.generic.base import TemplateResponseMixin
from django.views.generic import ListView, FormView

from display_tweets.forms import TwitterSearchForm
from display_tweets.models import TwitterSearch

import client


class ListSearchHistory(ListView):
    queryset = TwitterSearch.objects.all().order_by('-lastsearch')
    template_name = 'list_search_history.html'


class GetTwitterFeeds(FormView):
    form_class = TwitterSearchForm
    template_name = 'search_tweet.html'

    def form_valid(self, form):
        save_it = form.save(commit=False)
        save_it.phrase = save_it.phrase.lower()
        obj, created = TwitterSearch.objects.get_or_create(phrase=save_it.phrase)
        obj.count += 1
        obj.save()
        tweets = client.get_tweets(save_it.phrase)
        self.template_name = 'list_tweets.html'
        return TemplateResponseMixin.render_to_response(self, {
            'object_list': tweets,
            'key_phrase': save_it.phrase,
            'error': False,
        })

    def form_invalid(self, form):
        return super(GetTwitterFeeds, self).form_invalid(form)
