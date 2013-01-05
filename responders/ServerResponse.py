import redis
import socket
from BaseResponse import BaseResponse

class ServerResponse(BaseResponse):
    def __init__(self, botname):
        replies = {
            "@%s SERVER STATUS.*$" % botname: self.server_check,
            "@%s SERVER WAKEUP.*$" % botname: self.server_wake
            }

        BaseResponse.__init__(self, replies)

        self.server_status_replies = {
            "status_down": "Server \"%s\" is down",
            "status_up": "Server \"%s\" is up"
            }
        self.redis = redis.StrictRedis()

    def check_ssh(self):
        pass

    def server_check(self, tweet):
        """ Hello """

    def server_wake(self, tweet):
        server_name = tweet.text.lower().split()[3]
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 2)
        mac = self.redis.get(
                '%s:server:%s:mac' % (
                        self.twitter_bot.botname.lower(),
                        server_name
                        )
                    )
        s.sendto(
            '\xff' * 6 + mac.replace(':','').decode('hex') * 16,
            ('255.255.255.255', 9)
            )

        self.respond(
                "@%s Acknowledged. Wakeup packet sent to %s" % (
                                                        tweet.author.screen_name,
                                                        server_name
                                                        ),
                tweet.id
                )

    def react(self, *args):
        tweet, match = args
        self.replies[match](tweet)
