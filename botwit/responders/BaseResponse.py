# Base class for responders
# Implements common classes and defines abstract method 'react'
#
# Author: Matt Revell

import re
import redis

from tweepy.error import TweepError

class BaseResponse(object):
    """
    Base class for responders.
    """
    def __init__(self, botname, replies):
        """
        Initialise parameters.
        """
        self.botname = botname
        self.replies = replies
        self.twitter_bot = None
        self.match_terms = [
            (x, re.compile(x, re.IGNORECASE)) for x in replies.keys()
            ]
        self.redis = redis.StrictRedis()

    def react(self, *args):
        """
        Abstract: Called by the bot to process, respond to or otherwise act
        upon the tweet it receives.
        """

    def matches(self, tweet):
        """
        Called to determine if a tweet matches.
        """
        matches =  [p[0] for p in self.match_terms if p[1].match(tweet.text)]
        return matches

    def set_twitter_bot(self, bot):
        """
        Called to set the twiiter bot object which is needed in order to
        respond.
        """
        self.twitter_bot = bot
        return True

    def is_allowed(self, user):
        """
        Called to determine whether or not to respond to the owner of a matched
        tweet. Uses the bot's account friend list to authenticate.
        """
        if user.lower() in [
                    x.screen_name.lower() for x in (
                                    self.twitter_bot.api.friends(self.botname)
                                    )
                    ]:
            return True
        # This is here for testing!
        elif self.botname.lower() == user.lower():
            return True
        else:
            return False

    def respond(self, reply, reply_to_id=None):
        """
        Sends a response, passing the id of the tweet it is replying to if
        provided.

        Returns True if successful, False on error.
        """
        if not self.twitter_bot:
            print "ERROR: Twitter bot not set"
            return False
        try:
            self.twitter_bot.api.update_status(
                                reply,
                                reply_to_id
                                )
        except TweepError, e:
            print e
            return False

        print "Reply: %s" % reply
        return True
