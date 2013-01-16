from BaseResponse import BaseResponse

class SimpleResponse(BaseResponse):
    def react(self, *args):
        tweet, match = args
        self.respond(
                "@%s %s" % (
                        tweet.author.screen_name,
                        self.replies[match]
                        ),
                tweet.id
                )
