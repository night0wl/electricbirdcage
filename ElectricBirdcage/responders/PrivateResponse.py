import logging
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
            logging.error("Invalid DM: %s" % reply)
            return False

        try:
            self.respond(reply, reply_to_id)
            logging.info("Sent DM: %s" % reply)
            return True
        except TweepError:
            logging.error("Failed to send DM: %s" % reply)
            return False
