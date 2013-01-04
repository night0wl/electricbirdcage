#!/usr/bin/env python

DB_FILE = "/home/perseus/twitter_bots/stream_bot/stream_bot.db"

import re, sys
import sqlite3 as lite

import tweepy

from listeners import StreamListener
from responders import ReplyResponse

class StreamBot(object):
    def __init__(
            self, botname,
            consumer_key, consumer_secret,
            access_token, access_token_secret
            ):
        self.botname = botname
        self.api = self.get_api(
                consumer_key, consumer_secret,
                access_token, access_token_secret
                )
        self.responders = [ReplyResponse(self)]

    def add_responder(self, responder):
        self.responders.append(responder)

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
                    responder.respond(tweet, match)


def main():
    try:
        streambot = StreamBot(sys.argv[1])
        streambot.listen()
    except KeyboardInterrupt:
        print "Quitting..."
        sys.exit(0)

if __name__ == "__main__":
    main()
