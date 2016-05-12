from django.db import models


class TwitterSearch(models.Model):
    phrase = models.CharField(max_length=1000)
    count = models.IntegerField(default=0)
    lastsearch = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.phrase
