#!/usr/bin/env python

DB_FILE = "/home/perseus/twitter_bots/stream_bot/stream_bot.db"

import re, sys
import sqlite3 as lite

import tweepy

from listeners import StreamListener
from responders import ReplyResponse

class StreamBot(object):
    def __init__(self, botname):
        self.botname = botname
        self.db = lite.connect(DB_FILE)
        self.api = self.get_api()
        self.responders = [ReplyResponse(self)]

    def add_responder(self, responder):
        self.responders.append(responder)

    def sql_get_one(self, sql, args):
        return self.sql_exec(sql, args, num=1)


    def sql_exec(self, sql, args, num=0, commit=False, first_column_only=True):
        cur = self.db.cursor()
        cur.execute(sql, args)

        if commit:
            self.db.commit()
            return True
        elif num == 1:
            return cur.fetchone()
        else:
            result = cur.fetchall()
            if first_column_only:
                return [x[0] for x in result]
            else:
                return [x for x in result]

    def get_api(self):
        string = ''.join([
            "SELECT consumer_key, consumer_secret, access_token,",
            "access_token_secret FROM accounts WHERE account = ?"
            ])

        (
        consumer_key, consumer_secret,
        access_token, access_token_secret
        ) = self.sql_get_one(string, [self.botname])

        auth0 = tweepy.auth.OAuthHandler(consumer_key, consumer_secret)
        auth0.set_access_token(access_token, access_token_secret)
        return tweepy.API(auth0)

    def listen(self):
        streamer = tweepy.Stream(
                self.api.auth, StreamListener(self), timeout=300
                )
        streamer.filter(None,['@' + self.botname])

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


    #    if "achoo" in tweet.text.lower():
    #        self.api.update_status(
    #                    "@%s Bless You!" % tweet.author.screen_name,
    #                    tweet.id
    #                    )




def main():
    try:
        streambot = StreamBot(sys.argv[1])
        streambot.listen()
    except KeyboardInterrupt:
        print "Quitting..."
        sys.exit(0)

if __name__ == "__main__":
    main()
