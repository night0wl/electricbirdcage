#!/usr/bin/env python

import redis
import sys

from bots import StreamBot
from responders import SimpleResponse, ServerResponse

def get_creds(botname):
    base_key = "%s:" % botname.lower()
    red = redis.StrictRedis()
    return (
        red.get(base_key + "consumer_key"),
        red.get(base_key + "consumer_secret"),
        red.get(base_key + "access_token"),
        red.get(base_key + "access_token_secret")
        )

def main():
    simple_replies = {
            "^.*achoo.*$": "Bless You"
            }

    try:
        botname = sys.argv[1]
        responders = [
            SimpleResponse(botname, simple_replies),
            ServerResponse(botname)
            ]
        creds = get_creds(botname)
        bot = StreamBot(botname, creds, responders)
        bot.listen(None, ['@' + botname])
    except KeyboardInterrupt:
        print
        print "Quitting..."
        sys.exit(0)

if __name__ == "__main__":
    main()
