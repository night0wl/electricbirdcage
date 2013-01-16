import temper
import x10

from time import sleep

from PrivateResponse import PrivateResponse

class HeatingResponse(PrivateResponse):
    def __init__(self, botname):
        self.temper_dev = temper.TemperHandler().get_devices()[0]
        replies = {
            "@%s HEATING STATUS.*$" % botname: self.heating_status,
            "@%s HEATING ON.*$" % botname: self.heating_on,
            "@%s HEATING OFF.*$" % botname: self.heating_off
            }

        PrivateResponse.__init__(self, botname, replies)

        self.heating_replies = {
            "heating_status": "@%s Current temperature is %0.2fC",
            "fail": "DM @%s Oh Noes! That failed"
            }

    def heating_status(self, tweet):
        self.respond(
                self.heating_replies["heating_status"] % (
                                        tweet.author.screen_name,
                                        self.temper_dev.get_temperature()
                                        ),
                tweet.id
                )

    def heating_on(self, tweet):
        pass

    def heating_off(self, tweet):
        pass

    def react(self, *args):
        tweet, match = args
        if self.is_allowed(tweet.author.screen_name):
            self.replies[match](tweet)
