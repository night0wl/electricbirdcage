from tweepy.error import TweepError
from BaseResponse import BaseResponse

class PrivateResponse(BaseResponse):
    def react(self, *args):
        tweet, match = args
        reply = "DM @%s %s" % (
                tweet.author.screen_name,
                self.replies[match]
                )
        self.respond_private(reply, tweet.id)

    def respond_private(self, reply, reply_to_id=None):
        if reply[:2].lower() != "dm":
            print "That reply isn't a direct message"
            print reply
            return False

        try:
            self.respond(reply, reply_to_id)
            print "Reply: %s" % reply
            return True
        except TweepError:
            print "Cannot send DM to %s" % tweet.author.screen_name
            return False
