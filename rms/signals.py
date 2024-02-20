from PyQt5.QtCore import pyqtSignal, QObject


class RMSSignals(QObject):

    home = pyqtSignal(str, int)

    start_sequence = pyqtSignal(int)
