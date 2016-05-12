from django.conf.urls import patterns, url
from views import ListSearchHistory, GetTwitterFeeds

urlpatterns = patterns('',
    url(r'^$', GetTwitterFeeds.as_view(), name='search_tweets'),
    url(r'^searchhistory/$', ListSearchHistory.as_view(), name='search_history'),
)