import re

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

    def respond(self, reply, reply_to_id=None):
        if not self.twitter_bot:
            print "ERROR: Twitter bot not set"
            return False
        self.twitter_bot.api.update_status(
                                reply,
                                reply_to_id
                                )
        print "Reply: %s" % reply
        return True
