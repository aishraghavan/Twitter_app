from django.contrib import admin
from display_tweets.models import TwitterSearch


class TwitterSearchAdmin(admin.ModelAdmin):
    class Meta:
        model = TwitterSearch

admin.site.register(TwitterSearch, TwitterSearchAdmin)
