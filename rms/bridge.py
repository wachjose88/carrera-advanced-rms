
import time
import copy
from PyQt5.QtCore import QThread, pyqtSignal
from utils import formattime


class IdleMonitor(QThread):

    update_state = pyqtSignal(int)

    def __init__(self, cu, cu_instance):
        QThread.__init__(self)
        self.cu = cu
        self.cu_instance = cu_instance
        self.stop = False

    def run(self):
        last = None
        while not self.stop:
            try:
                time.sleep(0.01)
                data = self.cu.request()

                # print('IdleMonitor: ', data)
                if data == last:
                    continue
                elif isinstance(data, self.cu_instance.Status):
                    self.update_state.emit(data.mode)
                elif isinstance(data, self.cu_instance.Timer):
                    pass
                last = data
            except:
                pass


class StartSignal(QThread):

    ready_to_run = pyqtSignal()
    show_lights = pyqtSignal(int)

    def __init__(self, cu, cu_instance):
        QThread.__init__(self)
        self.cu = cu
        self.cu_instance = cu_instance
        self.stop = False

    def run(self):
        self.show_lights.emit(101)
        self.cu.start()
        status = self.cu.request()
        time.sleep(2.0)
        self.cu.start()
        finished = False
        last = None
        while not self.stop:
            time.sleep(0.01)
            status = self.cu.request()
            if status == last:
                continue
            # print('StartSignal: ', status)
            if isinstance(status, self.cu_instance.Status):
                if status.start > 1 and status.start < 7:
                    self.show_lights.emit(status.start)
                if status.start == 7:
                    self.show_lights.emit(100)
                    self.ready_to_run.emit()
                    break
                if status.start > 7:
                    self.show_lights.emit(0)
                if status.start == 0 and finished is True:
                    break


class CUBridge(QThread):

    update_grid = pyqtSignal(list)

    comp_finished = pyqtSignal(int, list)

    comp_state = pyqtSignal(int, list)

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
            self.name = ''
            self.racing = False

        def newlap(self, timer):
            if self.racing:
                if self.time is not None:
                    self.laptime = timer.timestamp - self.time
                    if self.bestlap is None or self.laptime < self.bestlap:
                        self.bestlap = self.laptime
                    self.laps += 1
                self.time = timer.timestamp

        def dump(self):
            print('num: ' + str(self.num) + ' time: ' + str(self.time))

    def __init__(self, cu, cu_instance, selected_drivers, tts, threadtranslation):
        QThread.__init__(self)
        self.cu = cu
        self.cu_instance = cu_instance
        self.tts = tts
        self.threadtranslation = threadtranslation
        self.running = False
        self.stop = False
        self.reset(selected_drivers)

    def reset(self, selected_drivers):
        self.drivers = [self.Driver(num) for num in range(1, 9)]
        for addr, driver in selected_drivers.items():
            self.drivers[addr].name = driver['name']
            self.drivers[addr].racing = True
        self.maxlaps = 0
        self.starttime = None
        # discard remaining timer messages
        status = self.cu.request()
        while not isinstance(status, self.cu_instance.Status):
            time.sleep(0.01)
            status = self.cu.request()
        self.status = status
        # reset cu timer
        self.cu.reset()
        # reset position tower
        self.cu.clrpos()

    def run(self):
        last = None
        race_start = time.time()
        self.tts.say(self.threadtranslation.letsgo.text())
        while not self.stop:
            rt = time.time() - race_start
            self.comp_state.emit(int(rt*1000), self.drivers)
            racing = False
            for driver in self.drivers:
                if driver.racing is True:
                    racing = True
            if racing is False:
                self.comp_finished.emit(int(rt*1000), copy.deepcopy(self.drivers))
                while not self.stop:
                    time.sleep(0.01)
                continue
            try:
                time.sleep(0.01)
                data = self.cu.request()
                # prevent counting duplicate laps
                # print('CUBridge: ', data)
                if data == last:
                    continue
                elif isinstance(data, self.cu_instance.Status):
                    self.handle_status(data)
                elif isinstance(data, self.cu_instance.Timer):
                    self.handle_timer(data)
                last = data
                self.update_grid.emit(self.drivers)
            except:
                pass

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
        old = copy.deepcopy(self.drivers)
        driver.newlap(timer)
        if self.maxlaps < driver.laps:
            self.maxlaps = driver.laps
            # position tower only handles 250 laps
            self.cu.setlap(self.maxlaps % 250)
        if self.starttime is None:
            self.starttime = timer.timestamp
        self.tts.say_on_timer(old, copy.deepcopy(self.drivers), timer.address)
