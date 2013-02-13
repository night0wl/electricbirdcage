#!/usr/bin/env python

# A twitter bot for listening to the public stream
# Matches tweets and responds
#
# Author: Matt Revell

import logging
import re
import tweepy

from botwit.listeners import StreamListener
from botwit.responders import SimpleResponse

class StreamBot(object):
    """
    A twitter bot that streams the public timeline reacting to tweets matching
    terms for the responders.
    """
    def __init__(self, botname, creds, responders):
        """
        Set botname, an API handle and initialise responders.
        """
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
        """
        Retrieve a tweepy API object using the given credentials.

        Return tweepy.API
        """

        auth0 = tweepy.auth.OAuthHandler(consumer_key, consumer_secret)
        auth0.set_access_token(access_token, access_token_secret)
        return tweepy.API(auth0)

    def listen(self, to_follow, to_track):
        """
        Open a stream listener, filtering by given users and keywords.
        Runs indefinately.
        """
        streamer = tweepy.Stream(
                self.api.auth, StreamListener(self), timeout=300
                )
        logging.info("Listening...")
        streamer.filter(to_follow, to_track)

    def process(self, tweet):
        """
        Process a tweet caught by the stream listener.
        Iterates over the loaded responders to find a match and reacts.
        """
        for responder in self.responders:
            matches = responder.matches(tweet)
            if len(matches):
                logging.info(
                        "%s tweeted '%s'" % (
                            tweet.author.screen_name,
                            tweet.text.encode("ascii", "replace")
                            )
                        )

                for match in matches:
                    responder.react(tweet, match)
