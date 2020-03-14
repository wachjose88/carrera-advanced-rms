#from bridge import CUBridge
from dummy import CUBridge
import contextlib
from carreralib import ControlUnit
import threading
import time
import sys
from PyQt5.QtWidgets import QMainWindow, QApplication, QMessageBox, \
                            QVBoxLayout, QWidget
from gui import Grid


class RMS(QMainWindow):

    def __init__(self):
        super().__init__()
    #with contextlib.closing(ControlUnit('/dev/ttyUSB0', timeout=1.0)) as cu:
        #print('CU version %s' % cu.version())
        cu = 5
        self.lock = threading.Lock()
        self.bridge = CUBridge(cu=cu, lock=self.lock)
        self.cub_thread = threading.Thread(target=self.bridge.run, args=())
        self.cub_thread.start()
        self.grid = Grid(parent=self)
        self.drivers = {
            2: {
                'pos': 1,
                'name': 'Josef'
            },
            3: {
                'pos': 4,
                'name': 'Josef'
            },
            1: {
                'pos': 2,
                'name': 'Mario'
            }
        }
        self.initUI()
        self.grid.addDriver(2, self.drivers[2])
        self.grid.addDriver(1, self.drivers[1])
        self.grid.reset()
        self.grid.addDriver(2, self.drivers[2])
        self.grid.driver_ui[2]['pits'].setText('1')

    def initUI(self):

        self.statusBar().showMessage('Ready')

        self.showMaximized()
        self.setWindowTitle('RMS')
        self.setCentralWidget(self.grid)
        self.show()

    def closeEvent(self, event):
        result = QMessageBox.question(self,
                                      "Confirm Exit...",
                                      "Are you sure you want to exit ?",
                                      QMessageBox.Yes | QMessageBox.No)
        event.ignore()

        if result == QMessageBox.Yes:
            event.accept()
            self.bridge.stop = True
            self.cub_thread.join()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = RMS()
    sys.exit(app.exec_())
