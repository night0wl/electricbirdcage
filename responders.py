import re

from tweepy.error import TweepError


class BaseResponse(object):
    def __init__(self, replies):
        self.replies = replies
        self.twitter_bot = None
        self.match_terms = [
            (x, re.compile(x, re.IGNORECASE)) for x in replies.keys()
            ]

    def react(self, *args):
        """
        This is the method called by the bot to
        process, respond to or otherwise act upon
        the tweet it receives
        """

    def matches(self, tweet):
        """ Called to determine if a tweet matches """
        matches =  [p[0] for p in self.match_terms if p[1].match(tweet.text)]
        return matches

    def set_twitter_bot(self, bot):
        self.twitter_bot = bot
        return True

    def respond(self, tweet, reply):
        if not self.twitter_bot:
            print "ERROR: Twitter bot not set"
            return False
        #  Thou shall not spam!
        #self.twitter_bot.api.update_status(reply)
        #            "@%s %s" % (
        #                tweet.author.screen_name,
        #                self.replies[match_str]
        #                ),
        #            tweet.id
        #            )
        print "Reply: %s" % reply
        return True


class PrivateResponse(BaseResponse):
    def react(self, *args):
        tweet, match = args
        reply = "DM @%s %s" % (
                tweet.author.screen_name,
                self.replies[match]
                )
        self.respond_private(tweet, reply)

    def respond_private(self, tweet, reply):
        if reply[:2].lower() != "dm":
            print "That reply isn't a direct message"
            print reply
            return False

        try:
            self.twitter_bot.api.update_status(reply)
            print "Reply: %s" % reply
            return True
        except TweepError:
            print "Cannot send DM to %s" % tweet.author.screen_name
            return False



class SimpleResponse(BaseResponse):
    def react(self, *args):
        self.respond(*args)


class AbuseCounterResponse(PrivateResponse):
    pass


class ABReplyResponse(BaseResponse):
    pass
