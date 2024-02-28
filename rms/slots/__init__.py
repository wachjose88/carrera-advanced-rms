from PyQt5.QtCore import QObject, pyqtSlot


class Slots(QObject):

    def __init__(self, rms_signals, database):
        super().__init__()
        self.rms_signals = rms_signals
        self.database = database

    @pyqtSlot(str, int)
    def home_slot(self, track_name, track_length):
        pass

    @pyqtSlot(int)
    def start_sequence_slot(self, number):
        pass

    @pyqtSlot(dict, int)
    def competition_progress_slot(self, results, mode):
        pass

    @pyqtSlot(str)
    def competition_finished_slot(self, mode):
        pass

    @pyqtSlot()
    def idle_slot(self):
        pass

    def connect_slots(self):
        self.rms_signals.home.connect(self.home_slot)
        self.rms_signals.start_sequence.connect(self.start_sequence_slot)
        self.rms_signals.competition_progress.connect(
            self.competition_progress_slot)
        self.rms_signals.competition_finished.connect(
            self.competition_finished_slot)
        self.rms_signals.idle.connect(self.idle_slot)
