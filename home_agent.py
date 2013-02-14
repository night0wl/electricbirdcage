#!/usr/bin/env python

# A ElectricBirdcage agent for home automation.
# Currently supports monitoring temperature and controlling heating and servers
#
# Author: Matt Revell

import atexit
import logging
import redis
import sys

from multiprocessing import Process, Pipe
from signal import signal, SIGTERM

from ElectricBirdcage.bots import StreamBot
from ElectricBirdcage.monitors import TemperatureMonitor
from ElectricBirdcage.responders import SimpleResponse, ServerResponse, HeatingResponse


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

def sig_handler(signum, frame):
    logging.info("Received SIGTERM, quitting...")
    sys.exit(0)

def on_exit(p):
    logging.info("Terminating monitors...")
    p.terminate()
    logging.info("Shutdown successful")

def main():
    """
    Run the ElectricBirdcage agent
    """
    simple_replies = {
        "^.*achoo.*$": "Bless You"
        }

    logging.basicConfig(
            format='%(levelname)s: %(asctime)s %(message)s',
            datefmt='%Y-%m-%d %I:%M:%S %p',
            filename='/var/log/electricbirdcage.log',
            level=logging.DEBUG
            )

    signal(SIGTERM, sig_handler)

    logging.info('ElectricBirdcage Starting...')
    try:
        botname = sys.argv[1]
        mon = TemperatureMonitor()
        parent, child = Pipe()
        p = Process(target=mon.run, args=(child,))
        p.start()
        logging.info("Started child process, PID: %s" % p.pid)
        atexit.register(on_exit, p)
        responders = [
            SimpleResponse(botname, simple_replies),
            ServerResponse(botname),
            HeatingResponse(botname, parent)
            ]
        creds = get_creds(botname)
        bot = StreamBot(botname, creds, responders)
        bot.listen(None, ['@' + botname])
    except KeyboardInterrupt:
        logging.info("Received Ctrl+C, quitting...")
        sys.exit(0)

if __name__ == "__main__":
    main()
