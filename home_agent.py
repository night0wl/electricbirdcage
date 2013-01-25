#!/usr/bin/env python

# A botwit agent for home automation.
# Currently supports monitoring temperature and controlling heating and servers
#
# Author: Matt Revell

import redis
import sys

from multiprocessing import Process, Pipe

from botwit.bots import StreamBot
from botwit.monitors import TemperatureMonitor
from botwit.responders import SimpleResponse, ServerResponse, HeatingResponse

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
        mon = TemperatureMonitor()
        parent, child = Pipe()
        p = Process(target=mon.run, args=(child,))
        p.start()
        responders = [
            SimpleResponse(botname, simple_replies),
            ServerResponse(botname),
            HeatingResponse(botname, parent)
            ]
        creds = get_creds(botname)
        bot = StreamBot(botname, creds, responders)
        bot.listen(None, ['@' + botname])
    except KeyboardInterrupt:
        parent.send("halt")
        p.join()
        print
        print "Quitting..."
        sys.exit(0)

if __name__ == "__main__":
    main()
