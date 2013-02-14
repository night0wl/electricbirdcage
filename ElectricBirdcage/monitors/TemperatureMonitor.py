# A monitor for a TEMPer USB device
# Keeps a record of any changes in temperature, listens for a signal and
# responds if required. Has a method to calculate the velocity of change in
# temperature.
#
# Author: matt Revell

import logging
import temper

from multiprocessing import Process, Pipe
from time import sleep, time

MIN = 60
HOUR = 60*60

class TemperatureMonitor(object):
    """
    A monitor for a TEMPer USB device.

    Keeps a record of any changes in temperature, listens for a signal and
    responds if required. Has a method to calculate the velocity of change in
    temperature.
    """
    def __init__(self):
        """
        Initialise parameters
        """
        devs = temper.TemperHandler().get_devices()
        self.dev = (len(devs) > 0 and devs[0]) or None
        self.events = [
                (time(), self.dev.get_temperature())
                ]

    def get_diffs(self, current_temperature):
        """
        Calculates and returns the difference in temperature over a minute and
        an hour interval.

        Returns a tuple (min, hour)
        """
        get_events = lambda x : [
                    y for y in self.events if y[0] >= time() - x
                    ]

        get_diff = lambda x : -min(x)[1]--current_temperature

        #print get_events(MIN), get_events(HOUR)

        min_events = get_events(MIN)
        hour_events = get_events(HOUR)

        min_diff = min_events and get_diff(min_events) or 0.0
        hour_diff = hour_events and get_diff(hour_events) or 0.0

        return current_temperature, min_diff, hour_diff


    def run(self, pipe):
        """
        Start monitoring temperature and record changes.

        Runs forever, checking for signal. Terminates when it recieves 'halt'
        """
        try:
            while True:
                current_temperature = self.dev.get_temperature()
                if pipe.poll():
                    msg = pipe.recv()
                    if msg == "get_diffs":
                        pipe.send(self.get_diffs(current_temperature))
                    elif msg == "halt":
                        logging.info("Temperature monitor received 'halt'")
                        break

                if self.events[0][1] != current_temperature:
                    try:
                        self.events.insert(0, (time(), current_temperature))
                    except usb.USBError:
                        print "USB Error"
                        continue
                sleep(1)

            pipe.send("quitting")
        except KeyboardInterrupt:
            pass
