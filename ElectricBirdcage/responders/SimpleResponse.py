# A simple response object
# Sends a static response to a matching tweet
#
# Author: Matt Revell

from BaseResponse import BaseResponse

class SimpleResponse(BaseResponse):
    """
    A simple response object.
    """
    def react(self, *args):
        """
        Called when a match is found. Sends a tweet with reply id.
        """
        tweet, match = args
        self.respond(
                "@%s %s" % (
                        tweet.author.screen_name,
                        self.replies[match]
                        ),
                tweet.id
                )
