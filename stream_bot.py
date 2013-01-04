#!/usr/bin/env python

DB_FILE = "/home/perseus/twitter_bots/stream_bot/stream_bot.db"

import re, sys
import sqlite3 as lite

import tweepy

class StreamListener(tweepy.StreamListener):
    def __init__(self, stream_bot):
        self.stream_bot = stream_bot
        tweepy.StreamListener.__init__(self)

    def on_status(self, status):
        print "Found a mention"
        self.stream_bot.process(status)


class ResponseHandler(object):
    def __init__(self, match_terms=[]):
        self.match_terms = [(x, re.compile(x, re.IGNORECASE)) for x in match_terms]

    def matches(self, tweet):
        """ Called to determine if a tweet matches """
        print tweet.text
        matches =  [p[0] for p in self.match_terms if p[1].match(tweet.text)]
        print matches
        return matches


class MI1ResponseHandler(ResponseHandler):
    def __init__(self, stream_bot):
        self.stream_bot = stream_bot
        self.replies = {
                "^.*you fight like a dairy([ -])?farmer.*$":
                "How appropriate. You fight like a cow."
                }
        ResponseHandler.__init__(self, self.replies.keys())

    def respond(self, tweet, match_str):
        self. stream_bot.api.update_status(
                    "@%s %s" % (
                        tweet.author.screen_name,
                        self.replies[match_str]
                        ),
                    tweet.id
                    )
        print "Replied to: %s\t\t%s" % (
                tweet.author.screen_name,
                self.replies[match_str]
                )


class StreamBot(object):
    def __init__(self, botname):
        self.botname = botname
        self.db = lite.connect(DB_FILE)
        self.api = self.get_api()
        self.responders = [MI1ResponseHandler(self)]

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
    streambot = StreamBot(sys.argv[1])
#    streambot.add_responder(MI1ResponseHandler(streambot))
    streambot.listen()

if __name__ == "__main__":
    main()
