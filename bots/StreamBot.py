#!/usr/bin/env python

import re
import tweepy

from listeners import StreamListener
from responders import SimpleResponse

class StreamBot(object):
    def __init__(self, botname, creds, responders):
        self.botname = botname
        self.api = self.get_api(*creds)
        self.responders = responders
        for responder in self.responders:
            responder.set_twitter_bot(self)

    def get_api(
            self,
            consumer_key, consumer_secret,
            access_token, access_token_secret
            ):

        auth0 = tweepy.auth.OAuthHandler(consumer_key, consumer_secret)
        auth0.set_access_token(access_token, access_token_secret)
        return tweepy.API(auth0)

    def listen(self, to_follow, to_track):
        streamer = tweepy.Stream(
                self.api.auth, StreamListener(self), timeout=300
                )
        streamer.filter(to_follow, to_track)

    def process(self, tweet):
        for responder in self.responders:
            matches = responder.matches(tweet)
            if len(matches):
                print "%s\t%s\t%s" % (
                        tweet.created_at,
                        tweet.author.screen_name,
                        tweet.text.encode("ascii", "replace")
                        )
                for match in matches:
                    responder.react(tweet, match)
