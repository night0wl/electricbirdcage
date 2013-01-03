#!/usr/bin/env python

DB_FILE = "/home/perseus/twitter_bots/stream_bot/stream_bot.db"

import sys
import sqlite3 as lite

import tweepy

class StreamListener(tweepy.StreamListener):
    def __init__(self, stream_bot):
        self.stream_bot = stream_bot
        tweepy.StreamListener.__init__(self)

    def on_status(self, status):
        self.stream_bot.respond(status)
        print "%s\t%s\t%s" % (
                status.created_at,
                status.author.screen_name,
                status.text.encode("ascii", "replace")
                )



class StreamBot(object):
    def __init__(self, botname):
        self.botname = botname
        self.db = lite.connect(DB_FILE)
        self.api = self.get_api()


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

    def respond(self, tweet):
        if "achoo" in tweet.text.lower():
            self.api.update_status(
                        "@%s Bless You!" % tweet.author.screen_name
                        )




def main():
    streambot = StreamBot(sys.argv[1])
    streambot.listen()

if __name__ == "__main__":
    main()
