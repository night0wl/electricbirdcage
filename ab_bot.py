#!/usr/bin/env python

DB_FILE = "/home/perseus/twitter_bots/stream_bot/ab_bot.db"

import sys
import sqlite3 as lite

from bots import StreamBot
from responders import ABReplyResponse

def sql_get_one(db, sql, args):
    return sql_exec(db, sql, args, num=1)

def sql_exec(db, sql, args, num=0, commit=False, first_column_only=True):
    cur = db.cursor()
    cur.execute(sql, args)

    if commit:
        db.commit()
        return True
    elif num == 1:
        return cur.fetchone()
    else:
        result = cur.fetchall()
        if first_column_only:
            return [x[0] for x in result]
        else:
            return [x for x in result]

def get_creds(db, botname):
    string = ''.join([
        "SELECT consumer_key, consumer_secret, access_token,",
        "access_token_secret FROM accounts WHERE account = ?"
        ])

    return sql_get_one(db, string, [botname])

def main():
    replies = {
        "^.*(what the.*((f.{2}k)|(hell)))|(wtf).*$": ''.join([
            "@%s It's called ageplay. It's been around for ages and isn't ",
            "anything to worry about"
            ])
        }
    responders = [
        ABReplyResponse(replies)
        ]

    try:
        botname = sys.argv[1]
        db = lite.connect(DB_FILE)
        creds = get_creds(db, botname)
        bot = StreamBot(botname, creds, responders)
        bot.listen(None, ["15 stone babies"])
    except KeyboardInterrupt:
        print
        print "Quitting..."
        sys.exit(0)

if __name__ == "__main__":
    main()
