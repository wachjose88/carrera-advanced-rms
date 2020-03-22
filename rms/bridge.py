from carreralib import ControlUnit
from PyQt5.QtCore import QThread, pyqtSignal
import time


class IdleMonitor(QThread):

    update_state = pyqtSignal(int)

    def __init__(self, cu):
        QThread.__init__(self)
        self.cu = cu
        self.stop = False

    def run(self):
        last = None
        while not self.stop:
            try:
                data = self.cu.request()
                # prevent counting duplicate laps
                #print(data)
                if data == last:
                    continue
                elif isinstance(data, ControlUnit.Status):
                    self.update_state.emit(data.mode)
                elif isinstance(data, ControlUnit.Timer):
                    pass
                last = data
            except:
                pass


class StartSignal(QThread):

    ready_to_run = pyqtSignal()
    show_lights = pyqtSignal(int)

    def __init__(self, cu):
        QThread.__init__(self)
        self.cu = cu

    def run(self):
        self.cu.start()
        status = self.cu.request()
        time.sleep(2.0)
        self.cu.start()
        finished = False
        last = None
        while True:
            status = self.cu.request()
            if status == last:
                continue
            print(status)
            if isinstance(status, ControlUnit.Status):
                if status.start > 1 and status.start < 7:
                    self.show_lights.emit(status.start)
                if status.start == 7:
                    finished = True
                if status.start > 7:
                    self.show_lights.emit(0)
                if status.start == 0 and finished is True:
                    self.show_lights.emit(100)
                    self.ready_to_run.emit()
                    break


class CUBridge(QThread):

    update_grid = pyqtSignal(list)

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

    def __init__(self, cu):
        QThread.__init__(self)
        self.cu = cu
        self.running = False
        self.stop = False
        self.reset()

    def reset(self):
        self.drivers = [self.Driver(num) for num in range(1, 9)]
        self.maxlaps = 0
        self.starttime = None
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
            #self.lock.acquire()
            try:
                data = self.cu.request()
                # prevent counting duplicate laps
                print(data)
                if data == last:
                    continue
                elif isinstance(data, ControlUnit.Status):
                    self.handle_status(data)
                elif isinstance(data, ControlUnit.Timer):
                    self.handle_timer(data)
                last = data
                self.update_grid.emit(self.drivers)
            except:
                pass
            #self.lock.release()

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
        if self.starttime is None:
            self.starttime = timer.timestamp
