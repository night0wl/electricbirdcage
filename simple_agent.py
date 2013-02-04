#!/usr/bin/env python

#   A simple botwit agent
#
#   Author: Matt Revell

import redis
import sys

from botwit.bots import StreamBot
from botwit.responders import SimpleResponse


def get_creds(botname):
    """
    Get Twitter API credetials from redis

    Returns (
        consumer_key,
        consumer_secret,
        access_token,
        access_token_secret
        )
    """
    base_key = "%s:" % botname.lower()
    red = redis.StrictRedis()
    return (
        red.get(base_key + "consumer_key"),
        red.get(base_key + "consumer_secret"),
        red.get(base_key + "access_token"),
        red.get(base_key + "access_token_secret")
        )


def main():
    """
    Run the botwit agent
    """
    simple_replies = {
        "^.*achoo.*$": "Bless You"
        }

    try:
        botname = sys.argv[1]
        responders = [
            SimpleResponse(botname, simple_replies)
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
