from carreralib import ControlUnit


class GUIBridge(object):

    def __init__(self, mainwindow, lock):
        self.mainwindow = mainwindow
        self.lock = lock
        self.running = False
        self.stop = False

    def run(self):
        while not self.stop:
            while not self.running:
                if self.stop:
                    break
            self.lock.acquire()
            for addr, driver in self.mainwindow.drivers.items():
                self.mainwindow.grid.updateDriver(addr=addr,
                    pos=1,
                    total=self.mainwindow.bridge.drivers[addr].time,
                    laps=self.mainwindow.bridge.drivers[addr].laps,
                    laptime=self.mainwindow.bridge.drivers[addr].laptime,
                    bestlaptime=self.mainwindow.bridge.drivers[addr].bestlap,
                    fuelbar=self.mainwindow.bridge.drivers[addr].fuel,
                    pits=self.mainwindow.bridge.drivers[addr].pit)
            self.lock.release()


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
                self.laptime = timer.timestamp - self.time
                if self.bestlap is None or self.laptime < self.bestlap:
                    self.bestlap = self.laptime
                self.laps += 1
            self.time = timer.timestamp

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
        # discard remaining timer messages
        status = self.cu.request()
        while not isinstance(status, ControlUnit.Status):
            status = self.cu.request()
        self.status = status
        # reset cu timer
        self.cu.reset()
        # reset position tower
        self.cu.clrpos()

    def run(self):
        last = None
        while not self.stop:
            while not self.running:
                if self.stop:
                    break
            self.lock.acquire()
            try:
                data = self.cu.request()
                # prevent counting duplicate laps
                if data == last:
                    continue
                elif isinstance(data, ControlUnit.Status):
                    self.handle_status(data)
                elif isinstance(data, ControlUnit.Timer):
                    self.handle_timer(data)
                last = data
            except:
                pass
            self.lock.release()

    def handle_status(self, status):
        for driver, fuel in zip(self.drivers, status.fuel):
            driver.fuel = fuel
        for driver, pit in zip(self.drivers, status.pit):
            if pit and not driver.pit:
                driver.pits += 1
            driver.pit = pit
        self.status = status

    def handle_timer(self, timer):
        driver = self.drivers[timer.address]
        driver.newlap(timer)
        if self.maxlaps < driver.laps:
            self.maxlaps = driver.laps
            # position tower only handles 250 laps
            self.cu.setlap(self.maxlaps % 250)
        if self.start is None:
            self.start = timer.timestamp
