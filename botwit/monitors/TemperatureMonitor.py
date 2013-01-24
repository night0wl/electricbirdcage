import temper
from multiprocessing import Process, Pipe
from time import sleep, time

MIN = 60
HOUR = 60*60

class TemperatureMonitor(object):
    def __init__(self):
        devs = temper.TemperHandler().get_devices()
        self.dev = (len(devs) > 0 and devs[0]) or None
        self.events = [
                (time(), self.dev.get_temperature())
                ]

    def get_diffs(self, current_temperature):
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
        try:
            while True:
                current_temperature = self.dev.get_temperature()
                if pipe.poll():
                    msg = pipe.recv()
                    if msg == "get_diffs":
                        pipe.send(self.get_diffs(current_temperature))
                    elif msg == "halt":
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

if __name__ == "__main__":
    mon = TemperatureMonitor()
    parent, child = Pipe()
    p = Process(target=mon.run, args=(child,))
    p.start()
    parent.send("get_diffs")
    print parent.recv()
    parent.send("halt")
    print parent.recv()
    p.join()
