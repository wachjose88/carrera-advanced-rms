
import time
import copy
import locale
import pyttsx3
from PyQt5.QtCore import QThread
from utils import formattime


class TTSHandler():

    def __init__(self):
        self.to_say = []

    def say_on_timer(self, old, new, addr):
        n = new[addr].name
        bl = old[addr].bestlap
        nbl = new[addr].bestlap

        if bl is None and nbl is not None:
            self.say(n + ': ' + str(formattime(nbl, longfmt=False)))
        if bl is not None and nbl is not None and nbl < bl:
            self.say(n + ': ' + str(formattime(nbl, longfmt=False)))

    def say(self, text):
        self.to_say.append(text)

    def getSays(self):
        t = copy.deepcopy(self.to_say)
        self.to_say = []
        return t


class TTSThread(QThread):

    def __init__(self, handler):
        QThread.__init__(self)
        lang = locale.getlocale()[0][0:2]
        self.handler = handler
        self.engine = pyttsx3.init()
        voices = self.engine.getProperty('voices')
        usev = 'english'
        for voice in voices:
            if lang in voice.languages[0].decode("utf-8"):
                usev = voice.id
        self.engine.setProperty('voice', usev)
        rate = self.engine.getProperty('rate')
        self.engine.setProperty('rate', rate-30)
        self.stop = False

    def run(self):
        while not self.stop:
            try:
                time.sleep(0.3)
                for text in self.handler.getSays():
                    self.engine.say(text)
                self.engine.runAndWait()
            except:
                pass
