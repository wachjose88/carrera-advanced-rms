
from collections import namedtuple
import time
import random


class ControlUnit(object):

    class Status(namedtuple('Status', 'fuel start mode pit display')):
        __slots__ = ()

        FUEL_MODE = 0x1
        REAL_MODE = 0x2
        PIT_LANE_MODE = 0x4
        LAP_COUNTER_MODE = 0x8

    class Timer(namedtuple('Timer', 'address timestamp sector')):
        pass

    PACE_CAR_KEY = b'T1'
    START_KEY = b'T2'
    SPEED_KEY = b'T5'
    BRAKE_KEY = b'T6'
    FUEL_KEY = b'T7'
    CODE_KEY = b'T8'

    def __init__(self, device, **kwargs):
        self.device = device
        self.time = time.time()
        self.start_press = 0
        self.started = None
        n = time.time()
        self.drivers = [n, n, n, n, n, n]
        self._status()

    def _status(self,
                fuel=(15, 15, 15, 15, 15, 15, 0, 0),
                start=0,
                mode=6,
                pit=(False, False, False, False, False, False, False, False),
                display=8):
        self.start_press = start if start < 8 else 0
        if self.started is None and start == 8:
            self.started = time.time()
        self.last = ControlUnit.Status(fuel, self.start_press, mode, pit, display)
        return self.last

    def _timer(self, address, timestamp, sector=1):
        self.last = ControlUnit.Timer(address, timestamp, sector)
        return self.last

    def close(self):
        pass

    def clrpos(self):
        pass

    def ignore(self, mask):
        pass

    def request(self, buf=b'?', maxlength=None):
        n = time.time()
        d = n - self.time
        if isinstance(self.last, ControlUnit.Timer):
            return self._status()
        if self.start_press == 0 and buf == self.START_KEY:
            self.time = n
            return self._status(start=1)
        if self.start_press == 1 and buf == self.START_KEY:
            self.time = n
            return self._status(start=2)
        if self.start_press in range(2, 8) and d > 1.0:
            self.time = n
            return self._status(start=self.start_press+1)
        r = random.uniform(2.1, 3.2)
        if self.started is not None:
            for i, dn in enumerate(self.drivers):
                dnd = n - dn
                if dnd > r:
                    dnn = dn + r
                    self.drivers[i] = dnn
                    return self._timer(i, int((dnn-self.started)*1000))
        return self.last

    def reset(self):
        self.time = time.time()
        self.start_press = 0
        self.started = None
        n = time.time()
        self.drivers = [n, n, n, n, n, n]
        self._status()

    def setbrake(self, address, value):
        pass

    def setfuel(self, address, value):
        pass

    def setlap(self, value):
        pass

    def setlap_hi(self, value):
        pass

    def setlap_lo(self, value):
        pass

    def setpos(self, address, position):
        pass

    def setspeed(self, address, value):
        pass

    def setword(self, word, address, value, repeat=1):
        pass

    def start(self):
        self.request(self.START_KEY)

    def version(self):
        return self.device
