from django.test import TestCase
from django.core.urlresolvers import reverse
from mock import patch

from tweepy import OAuthHandler
import datetime
import pytz
import tweepy

from display_tweets.models import TwitterSearch
from display_tweets.forms import TwitterSearchForm
from twitter_project import apikeys
from display_tweets.client import get_tweets


class TestDisplayTweetsModel(TestCase):

    def setUp(self):
        self.phrase = u"Test"
        self.test_item = TwitterSearch.objects.create(phrase=self.phrase)

    def test_model_get_default_values(self):
        """
        Tests all fields for the TwitterSearch model to the assigned values in the setup method.
        """
        self.assertEqual(self.test_item.phrase, "Test")
        self.assertEqual(self.test_item.count, 0)
        self.assertEqual(self.test_item.lastsearch.date(), datetime.datetime.now(tz=pytz.UTC).date())

    def test_model_valid_phrase(self):
        """
        Tests str() method to return the valid search phrase.
        """
        search = TwitterSearch(phrase='Robots')
        self.assertEqual(str(search), 'Robots')

    def test_model_empty_phrase(self):
        """
        Tests str() method for empty search phrase.
        """
        search = TwitterSearch(phrase="")
        self.assertEquals(str(search), "")
        self.assertIsNotNone(str(search))


class TestViews(TestCase):
    def test_tweet_index_exists(self):
        """
        Tests if the index page is available.
        """
        response = self.client.post('/tweets/')
        self.assertEqual(response.status_code, 200)

    def test_search_history_exists(self):
        """
        Tests if the searchhistory page is available.
        """
        response = self.client.get('/tweets/searchhistory/')
        self.assertEqual(response.status_code, 200)

    def test_admin_exists(self):
        """
        Tests if the admin page is available.
        """
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 200)

    def test_search_history_for_list_view(self):
        """
        Tests if the ListView fetches all the twitter search history.
        """
        search_phrase = "search phrase"
        list_ = TwitterSearch.objects.create(phrase=search_phrase)
        response = self.client.get('/tweets/searchhistory/')
        self.assertContains(response, search_phrase)
        self.assertEquals(TwitterSearch.objects.all().count(), 1)

    @patch('display_tweets.client.get_tweets')
    def test_list_of_tweet_results_returned_by_get_tweets(self, get_tweets):
        """
        Tests if the client.get_tweets() method returns a list of tweets.
        """
        tweet_results = [u"Tweet1", u"Tweet2"]
        get_tweets.return_value = tweet_results
        form_data = {'phrase': 'chennai'}
        self.url = reverse("search_tweets")
        response = self.client.post(self.url, form_data)
        self.assertEqual(response.status_code, 200)
        for tweet in tweet_results:
            self.assertContains(response, tweet)


class TestSearchTweetsView(TestCase):

    def setUp(self):
        self.url = reverse("search_tweets")
        self.form_data = {'phrase': 'Garden'}
        self.form = TwitterSearchForm(data=self.form_data)
        self.response = self.client.post(self.url, self.form_data)

    def test_form_is_valid(self):
        """
        Checks if the requested url is available and the form is valid.
        """
        self.assertEqual(self.response.status_code, 200)
        self.assertTrue(self.form.is_valid())

    def test_form_returned_data(self):
        """
        When the form is valid, checks if the phrase field can be retrieved from it.
        """
        form_returned_data = self.form.save(commit=False)
        form_returned_data.phrase = form_returned_data.phrase.lower()
        self.assertEqual(form_returned_data.phrase, "garden")

    def test_form_is_invalid(self):
        """
        When the user submits the form without entering any value for phrase,
        it throws an error indicating "This field is required.
        """
        form_data = {'phrase': ''}
        form = TwitterSearchForm(data=form_data)
        response = self.client.post(self.url, form_data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {'phrase': ['This field is required.']})


class TestTwitterApiClient(TestCase):
    def test_get_tweets_for_valid_phrase(self):
        """
        When a valid phrase is passed in, it returns a list of tweets.
        """
        tweets = get_tweets("word")
        self.assertIsNotNone(tweets)

    def test_get_tweets_returns_no_tweets_for_random_phrase(self):
        """
        When a random phrase is entered, no tweets can be retrieved.
        """
        tweets = get_tweets("dsgfdgdfgfdgfdgfsdg")
        self.assertEquals(tweets, [])


class TestTweepyAuthentication(TestCase):

    def setUp(self):
        self.auth = OAuthHandler(apikeys.TWITTER_CONSUMER_KEY, apikeys.TWITTER_CONSUMER_SECRET)
        self.auth.set_access_token(apikeys.TWITTER_ACCESS_TOKEN, apikeys.TWITTER_ACCESS_KEY)
        self.invalid_auth = OAuthHandler("WRONG_CONSUMER_KEY", "WRONG_CONSUMER_SECRET")
        self.invalid_auth.set_access_token("WRONG_ACCESS_TOKEN", "WRONG_ACCESS_KEY")
        self.blank_auth = OAuthHandler("", "")
        self.blank_auth.set_access_token("", "")

    def test_tweepy_api_authentication_with_valid_fields(self):
        """
        When valid set of authentication keys are passed, it gets back
        Tests the tweepy api for valid set of API key.
        """
        self.assertIsNotNone(self.auth.get_authorization_url())

    def test_tweepy_api_authentication_with_invalid_fields(self):
        """
        Tests the tweepy api for invalid set of API key.
        """
        with self.assertRaises(tweepy.TweepError):
            self.invalid_auth.get_authorization_url()

    def test_tweepy_api_authentication_with_blank_fields(self):
        """
        Tests the tweepy api for set of blank fields.
        """
        with self.assertRaises(tweepy.TweepError):
            self.blank_auth.get_authorization_url()

    def test_tweepy_api__with_valid_phrase(self):
        """
        Tests the tweepy api with valid phrase.
        """
        api = tweepy.API(self.auth)
        self.assertIsNotNone(api.search(q="word"))

    def test_tweepy_api_with_empty_string(self):
        """
        Tweepy should give TweepError when query is an empty string.
        """
        api = tweepy.API(self.auth)
        with self.assertRaises(tweepy.TweepError):
            api.search(q="")

    def test_tweepy_api_with_valid_phrase_but_invalid_authentication(self):
        """
        Tweepy should give TweepError when given invalid set of API keys.
        """
        api = tweepy.API(self.invalid_auth)
        with self.assertRaises(tweepy.TweepError):
            api.search(q="word")