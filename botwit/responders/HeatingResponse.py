import temper
from x10.controllers.bus import USBScanner
from time import sleep

from PrivateResponse import PrivateResponse

class HeatingResponse(PrivateResponse):
    def __init__(self, botname, pipe):
        self.pipe = pipe
        temper_devs = temper.TemperHandler().get_devices()
        self.temper_dev = (len(temper_devs) > 0 and temper_devs[0]) or None

        heater_devs = list(USBScanner().findDevices())
        if len(heater_devs) > 0:
            heater_devs[0].open()
            self.heater_dev = heater_devs[0].actuator("A1")
        else:
            self.heater_dev = None

        replies = {
            "@%s HEATING STATUS.*$" % botname: self.heating_status,
            "@%s HEATING ON.*$" % botname: self.heating_on,
            "@%s HEATING OFF.*$" % botname: self.heating_off
            }

        PrivateResponse.__init__(self, botname, replies)

        self.heating_replies = {
            "heating_status": ''.join([
                            "@%s Current temperature is %0.2fC. ",
                            "Change (min/hour) %0.2f / %0.2f"
                            ]),
            "heating_on": "@%s The heating is now on",
            "heating_off": "@%s The heating is now off",
            "no_temper_dev": "DM @%s Did not detect a TEMPer device",
            "no_x10_dev": "DM @%s Did not detect an x10 controller device",
            "fail": "DM @%s Oh Noes! That failed"
            }

    def heating_status(self, tweet):
        if self.temper_dev:
            self.pipe.send("get_diffs")
            #out_args = (tweet.author.screen_name,) + self.pipe.recv()
            #print out_args
            self.respond(
                    self.heating_replies["heating_status"] % (
                                            (tweet.author.screen_name,) +
                                            self.pipe.recv()
                                            ),
                    tweet.id
                    )
        else:
            self.respond_private(
                    self.heating_replies["no_temper_dev"]  % (
                                            tweet.author.screen_name
                                            ),
                    tweet.id
                    )

    def heating_on(self, tweet):
        if self.heater_dev:
            self.heater_dev.on()
            self.respond(
                    self.heating_replies["heating_on"] % (
                                            tweet.author.screen_name
                                            ),
                    tweet.id
                    )
        else:
            self.respond_private(
                    self.heating_replies["no_x10_dev"]  % (
                                            tweet.author.screen_name
                                            ),
                    tweet.id
                    )

    def heating_off(self, tweet):
        pass
        if self.heater_dev:
            self.heater_dev.off()
            self.respond(
                    self.heating_replies["heating_off"] % (
                                            tweet.author.screen_name
                                            ),
                    tweet.id
                    )
        else:
            self.respond_private(
                    self.heating_replies["no_x10_dev"]  % (
                                            tweet.author.screen_name
                                            ),
                    tweet.id
                    )

    def react(self, *args):
        tweet, match = args
        if self.is_allowed(tweet.author.screen_name):
            self.replies[match](tweet)
