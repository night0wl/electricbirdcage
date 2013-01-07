#!/usr/bin/env python

import redis
import sys
import sqlite3 as lite

from bots import StreamBot
from responders import ServerResponse

def get_creds(db, botname):
    base_key = "%s:" % botname.lower()
    red = redis.StrictRedis()
    return (
        red.get(base_key + "consumer_key"),
        red.get(base_key + "consumer_secret"),
        red.get(base_key + "access_token"),
        red.get(base_key + "access_token_secret")
        )

def main():
    try:
        botname = sys.argv[1]
        responders = [
            ServerResponse(botname)
            ]
        db = lite.connect(DB_FILE)
        creds = get_creds(db, botname)
        bot = StreamBot(botname, creds, responders)
        bot.listen(None, ['@' + botname])
    except KeyboardInterrupt:
        print
        print "Quitting..."
        sys.exit(0)

if __name__ == "__main__":
    main()
