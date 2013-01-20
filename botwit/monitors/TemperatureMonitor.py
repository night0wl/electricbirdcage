import temper
from time import sleep, time

MIN = 60
HOUR = 60*60
DAY = 60*60*24

class TemperatureMonitor(object):
    def __init__(self):
        devs = temper.TemperHandler().get_devices()
        self.dev = (len(devs) > 0 and devs[0]) or None
        self.events = [
                (time(), self.dev.get_temperature())
                ]
#        self.pipe = pipe

    def get_diffs(self, current_temperature):
        get_events = lambda x : [
                    y for y in self.events if y[0] >= time() - x
                    ]

        get_diff = lambda x : -min(x)[1]--current_temperature

        print get_events(MIN), get_events(HOUR), get_events(DAY)

        min_events = get_events(MIN)
        hour_events = get_events(HOUR)
        day_events = get_events(DAY)

        min_diff = min_events and get_diff(min_events) or 0.0
        hour_diff = hour_events and get_diff(hour_events) or 0.0
        day_diff = day_events and get_diff(day_events) or 0.0

        return min_diff, hour_diff, day_diff


    def run(self):
        while True:
            current_temperature = self.dev.get_temperature()
            if self.events[0][1] != current_temperature:
                try:
                    self.events.insert(0, (time(), current_temperature))
                except usb.USBError:
                    print "USB Error"
                    continue
            print self.get_diffs(current_temperature)
            sleep(1)

if __name__ == "__main__":
    mon = TemperatureMonitor()
    mon.run()
