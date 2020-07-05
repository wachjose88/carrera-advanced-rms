
import time
import pyttsx3
from PyQt5.QtCore import QThread
from utils import formattime


class TTSHandler(QThread):

    def __init__(self):
        QThread.__init__(self)
        self.engine = pyttsx3.init()
        self.stop = False

    def say(self, text):
        self.engine.say(text)

    def run(self):
        while not self.stop:
            try:
                time.sleep(0.3)
                self.engine.runAndWait()
            except:
                pass
