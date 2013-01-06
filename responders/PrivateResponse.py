from tweepy.error import TweepError
from BaseResponse import BaseResponse

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
            self.respond(reply)
            print "Reply: %s" % reply
            return True
        except TweepError:
            print "Cannot send DM to %s" % tweet.author.screen_name
            return False
