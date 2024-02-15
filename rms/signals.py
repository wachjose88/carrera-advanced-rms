from PyQt5.QtCore import pyqtSignal, QObject


class RMSSignals(QObject):

    start_sequence = pyqtSignal(int)