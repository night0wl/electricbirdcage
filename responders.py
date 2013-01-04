import re


class ResponseHandler(object):
    def __init__(self, match_terms=[]):
        self.match_terms = [(x, re.compile(x, re.IGNORECASE)) for x in match_terms]

    def matches(self, tweet):
        """ Called to determine if a tweet matches """
        matches =  [p[0] for p in self.match_terms if p[1].match(tweet.text)]
        return matches


class ReplyResponse(ResponseHandler):
    def __init__(self, stream_bot):
        self.stream_bot = stream_bot
        self.replies = {
                "^.*achoo.*$":
                "Bless You"
                }
        ResponseHandler.__init__(self, self.replies.keys())

    def respond(self, tweet, match_str):
        self. stream_bot.api.update_status(
                    "@%s %s" % (
                        tweet.author.screen_name,
                        self.replies[match_str]
                        ),
                    tweet.id
                    )
        print "Replied to: %s\t\t%s" % (
                tweet.author.screen_name,
                self.replies[match_str]
                )
