from django.shortcuts import render, redirect
from tweepy import API
from tweepy import Cursor
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
import tweepy
from textblob import TextBlob

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import urllib, base64
import io
import numpy as np
import pandas as pd
import re
import locale

ACCESS_TOKEN = "724965973032235009-lYNBcUIr0ZYD5f2zS82TeOuyyIuO1kw"
ACCESS_TOKEN_SECRET = "r72tD0v52o4xexbFkbi84CpdC1R6yA8aYdCVRKxop58eR"
CONSUMER_KEY = "yOnth8w49CMcQdQBDeQT9xfm2"
CONSUMER_SECRET = "7LZN0fhTeQNu0kPbeeOPb2OUMfUsG892vOVf3YOovD8kNcBznD"

class TwitterClient():

    def __init__(self, twitter_user=None):
        self.auth = TwitterAuthenticator().authenticate_twitter_app()
        self.twitter_client = API(self.auth)

        self.twitter_user = twitter_user

    def get_twitter_client_api(self):
        return self.twitter_client

    def get_user_timeline_tweets(self, num_tweets):
        tweets = []
        for tweet in Cursor(self.twitter_client.user_timeline, id=self.twitter_user).items(num_tweets):
            tweets.append(tweet)
        return tweets

    def get_friend_list(self, num_friends):
        friend_list = []
        for friend in Cursor(self.twitter_client.friends, id=self.twitter_user).items(num_friends):
            friend_list.append(friend)
        return friend_list

    def get_home_timeline_tweets(self, num_tweets):
        home_timeline_tweets = []
        for tweet in Cursor(self.twitter_client.home_timeline, id=self.twitter_user).items(num_tweets):
            home_timeline_tweets.append(tweet)
        return home_timeline_tweets


#  twitter authenticator
class TwitterAuthenticator():
    def authenticate_twitter_app(self):
        auth = OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
        auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
        return auth


# Twitter streamer
class TwitterStreamer():
    # class for streaming and processing live tweets
    def __init__(self):
        self.twitter_authenticator = TwitterAuthenticator()

    def stream_tweets(self, fetched_tweets_filename, hash_tag_list):
        # This handles twitter authentication and the connection to the Twitter streaming API
        listener = TwitterListener(fetched_tweets_filename)
        auth = self.twitter_authenticator.authenticate_twitter_app()
        stream = Stream(auth, listener)
        stream.filter(track=hash_tag_list)


# twitter stream listener
class TwitterListener(StreamListener):
    # this a basic listener class that just prints received tweets to stdout
    def init(self, fetched_tweets_filename):
        self.fetched_tweets_filename = fetched_tweets_filename

    def on_data(self, data):
        try:
            print(data)
            with open(self.fetched_tweets_filename, 'a') as tf:
                tf.write(data)
            return True
        except BaseException as e:
            print("error on data %s" % str(e))
        return True

    def on_error(self, status):
        if status == 420:
            # returning false on data method in case rate limit occurs
            return False
        print(status)


class TweetAnalyzer():
    # functinality for analyzing and categorizing content from tweets

    def clean_tweet(self, tweet):
        return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split())

    def analyze_sentiment(self, tweet):
        analysis = TextBlob(self.clean_tweet(tweet))

        if analysis.sentiment.polarity > 0:
            return 1
        elif analysis.sentiment.polarity == 0:
            return 0
        else:
            return -1

    def tweets_to_data_frame(self, tweets):
        df = pd.DataFrame(data=[tweet.text for tweet in tweets], columns=['tweets'])

        df['id'] = np.array([tweet.id for tweet in tweets])
        df['len'] = np.array([len(tweet.text) for tweet in tweets])
        df['date'] = np.array([tweet.created_at for tweet in tweets])
        df['source'] = np.array([tweet.source for tweet in tweets])
        df['likes'] = np.array([tweet.favorite_count for tweet in tweets])
        df['retweets'] = np.array([tweet.retweet_count for tweet in tweets])

        return df


# Create your views here.
def home_view(request):
    return render(request, 'index.html')

def num(count):
    f_count = str(count)

    if (int(len(count))) == 12:
        x = f_count[:3] + '.' + f_count[3] + 'B'

    if (int(len(count))) == 11:
        x = f_count[:2] + '.' + f_count[2] + 'B'

    if (int(len(count))) == 10:
        x = f_count[:1] + '.' + f_count[1] + 'B'

    if (int(len(count))) == 9:
        x = f_count[:3] + '.' + f_count[3] + 'M'

    if (int(len(count))) == 8:
        x = f_count[:2] + '.' + f_count[2] + 'M'

    if (int(len(count))) == 7:
        x = f_count[:1] + '.' + f_count[1] + 'M'

    if (int(len(count))) == 6:
        x = f_count[:3] + '.' + f_count[3] + 'K'

    if (int(len(count))) == 5:
        x = f_count[:2] + '.' + f_count[2] + 'K'

    if (int(len(count))) == 4:
        x = f_count[:1] + '.' + f_count[1] + 'K'

    if (int(len(count)) <= 3) and (int(len(count)) >= 4):
        x = f_count[:2] + '.' + f_count[2] + 'K'

    if int(len(count)) < 4:
        x = f_count

    return x

def search_view(request):
    context = {}
    twitter_client = TwitterClient()
    tweet_analyzer = TweetAnalyzer()

    if request.GET:
        search_query = request.GET['search_query']
        tweet_results = request.GET['results']

        api = twitter_client.get_twitter_client_api()

        try:
            description = api.get_user(screen_name=search_query).description

            tweets_count = api.get_user(screen_name=search_query).statuses_count
            tweet_count = num(str(tweets_count))

            followers = api.get_user(screen_name=search_query).followers_count
            followers_count = num(str(followers))

            following = api.get_user(screen_name=search_query).friends_count
            following_count = num(str(following))

            display_pic = api.get_user(screen_name=search_query).profile_image_url_https
            bigger_pic = display_pic.replace('_normal', '')

            tweets = api.user_timeline(screen_name=search_query, count=tweet_results)

            df = tweet_analyzer.tweets_to_data_frame(tweets)
            df['sentiment'] = np.array([tweet_analyzer.analyze_sentiment(tweet) for tweet in df['tweets']])

            plt.clf()

            time_retweets = pd.Series(data=df['retweets'].values, index=df['date'])
            time_retweets.plot(figsize=(16, 4), label="retweets", legend=True)

            time_likes = pd.Series(data=df['likes'].values, index=df['date'])
            time_likes.plot(figsize=(16, 4), label="likes", legend=True)

            buf = io.BytesIO()
            plt.savefig(buf, format='png', dpi=300)
            image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8').replace('\n', '')
            buf.close()

            context = {
                'username': search_query,
                'display_pic': bigger_pic,
                'description': description,
                'tweet_count': tweet_count,
                'followers': followers_count,
                'following': following_count,
                'data': df.itertuples(),
                'data_try': df.itertuples(),
                'results': tweet_results,
                'retweet_graph': image_base64
            }

            return render(request, 'twitter_analysis.html', context)

        except tweepy.TweepError as e:
            context = {'username': 'user_not_found'}
            return render(request, 'twitter_analysis.html', context)


# def analysis_view(request):
#     return render(request, 'twitter[p_analysis.html')