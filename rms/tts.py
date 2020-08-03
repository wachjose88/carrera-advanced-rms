
import time
import locale
import pyttsx3
from PyQt5.QtCore import QThread
from utils import formattime


class TTSHandler(QThread):

    def __init__(self):
        QThread.__init__(self)
        lang = locale.getlocale()[0][0:2]
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

    def say_on_timer(self, old, new, addr):
        bl = old[addr].bestlap
        nbl = new[addr].bestlap
        if bl is None and nbl is not None:
            self.say(new[addr].name + ': '
                     + str(formattime(nbl, longfmt=False)))
        if bl is not None and nbl is not None and nbl < bl:
            self.say(new[addr].name + ': '
                     + str(formattime(nbl, longfmt=False)))

    def say(self, text):
        self.engine.say(text)

    def run(self):
        while not self.stop:
            try:
                time.sleep(0.3)
                self.engine.runAndWait()
            except:
                pass
