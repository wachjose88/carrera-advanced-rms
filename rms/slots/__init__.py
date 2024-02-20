from PyQt5.QtCore import QObject, pyqtSlot


class Slots(QObject):

    def __init__(self, rms_signals):
        super().__init__()
        self.rms_signals = rms_signals

    @pyqtSlot(str, int)
    def home_slot(self, track_name, track_length):
        pass

    @pyqtSlot(int)
    def start_sequence_slot(self, number):
        pass

    def connect_slots(self):
        self.rms_signals.home.connect(self.home_slot)
        self.rms_signals.start_sequence.connect(self.start_sequence_slot)
