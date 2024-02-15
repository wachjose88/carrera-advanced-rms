from PyQt5.QtCore import pyqtSlot, QObject

class Console(QObject):

    def __init__(self, rms_signals):
        super().__init__()
        self.rms_signals = rms_signals

    @pyqtSlot(int)
    def start_sequence_slot(self, number):
        print(number)

    def connect_slots(self):
        self.rms_signals.start_sequence.connect(self.start_sequence_slot)
