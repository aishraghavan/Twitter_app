from tweepy import OAuthHandler
import tweepy

from twitter_project import apikeys


def get_tweets(word):
    """
    This method is to set access for the Twitter api and retrieve all tweets for the given search phrase.
    """
    auth = OAuthHandler(apikeys.TWITTER_CONSUMER_KEY, apikeys.TWITTER_CONSUMER_SECRET)
    auth.set_access_token(apikeys.TWITTER_ACCESS_TOKEN, apikeys.TWITTER_ACCESS_KEY)
    api = tweepy.API(auth)
    results = [tweet.text for tweet in api.search(q=word, count=20)]
    return results