import re


class ResponseHandler(object):
    def __init__(self, match_terms=[]):
        self.match_terms = [(x, re.compile(x, re.IGNORECASE)) for x in match_terms]

    def matches(self, tweet):
        """ Called to determine if a tweet matches """
        matches =  [p[0] for p in self.match_terms if p[1].match(tweet.text)]
        return matches

    def set_twitter_bot(self, bot):
        self.twitter_bot = bot
        return True


class ReplyResponse(ResponseHandler):
    def __init__(self, replies):
        self.twitter_bot = None
        self.replies = replies
        ResponseHandler.__init__(self, self.replies.keys())

    def respond(self, tweet, match_str):
        if not self.twitter_bot:
            print "ERROR: Twitter bot not set"
            return False

        self. twitter_bot.api.update_status(
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
        return True
