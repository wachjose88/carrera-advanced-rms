from PyQt5.QtCore import pyqtSlot
from . import Slots

class Console(Slots):

    LINE_LENGTH = 42

    def _build_text(self, text):
        length = self.LINE_LENGTH - 4
        end = ' ' * (length - len(text))
        print(f'# {text[:length]}{end} #')

    @pyqtSlot(str, int)
    def home_slot(self, track_name, track_length):
        print('#' * self.LINE_LENGTH)
        self._build_text(track_name)
        self._build_text(str(track_length) + ' mm')
        print('#' * self.LINE_LENGTH)

    @pyqtSlot(int)
    def start_sequence_slot(self, number):
        if number not in [0, 2, 3, 4, 5, 6, 100]:
            return
        print('#' * self.LINE_LENGTH)
        start_in = self.tr('Start in')
        if number == 2:
            self._build_text(f'{start_in}: 5')
        elif number == 3:
            self._build_text(f'{start_in}: 4')
        elif number == 4:
            self._build_text(f'{start_in}: 3')
        elif number == 5:
            self._build_text(f'{start_in}: 2')
        elif number == 6:
            self._build_text(f'{start_in}: 1')
        elif number == 0:
            self._build_text(self.tr('False start'))
        elif number == 100:
            self._build_text(self.tr('GO GO GO!'))
        print('#' * self.LINE_LENGTH)
