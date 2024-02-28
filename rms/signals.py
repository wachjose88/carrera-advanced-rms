from PyQt5.QtCore import pyqtSignal, QObject


class RMSSignals(QObject):

    idle = pyqtSignal()

    home = pyqtSignal(str, int)

    start_sequence = pyqtSignal(int)

    competition_progress = pyqtSignal(dict, int)

    competition_finished = pyqtSignal(str)
