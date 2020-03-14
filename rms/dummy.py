from carreralib import ControlUnit
import time

class CUBridge(object):

    class Driver(object):
        def __init__(self, num):
            self.num = num
            self.time = None
            self.laptime = None
            self.bestlap = None
            self.laps = 0
            self.pits = 0
            self.fuel = 0
            self.pit = False

        def newlap(self, timer):
            if self.time is not None:
                self.laptime = timer - self.time
                if self.bestlap is None or self.laptime < self.bestlap:
                    self.bestlap = self.laptime
                self.laps += 1
            self.time = timer

        def dump(self):
            print('num: ' + str(self.num) + ' time: ' + str(self.time))

    def __init__(self, cu, lock):
        self.cu = cu
        self.lock = lock
        self.running = True
        self.stop = False
        self.reset()

    def reset(self):
        self.drivers = [self.Driver(num) for num in range(1, 9)]
        self.maxlaps = 0
        self.start = None

    def run(self):
        last = 0
        while not self.stop:
            while not self.running:
                if self.stop:
                    break
            self.lock.acquire()
            self.handle_timer(last+1500, 3)
            self.handle_timer(last+900, 1)
            self.lock.release()
            time.sleep(2.4)
            last += 2400

    def handle_status(self, status):
        for driver, fuel in zip(self.drivers, status.fuel):
            driver.fuel = fuel
        for driver, pit in zip(self.drivers, status.pit):
            if pit and not driver.pit:
                driver.pits += 1
            driver.pit = pit
        self.status = status

    def handle_timer(self, timer, address):
        driver = self.drivers[address]
        driver.newlap(timer)
        if self.maxlaps < driver.laps:
            self.maxlaps = driver.laps
        if self.start is None:
            self.start = timer
