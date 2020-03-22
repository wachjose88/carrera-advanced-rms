from bridge import CUBridge, StartSignal, IdleMonitor
import contextlib
from carreralib import ControlUnit
import sys
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QMainWindow, QApplication, QMessageBox
from gui import Grid, Home


class RMS(QMainWindow):

    def __init__(self, cu):
        super().__init__()
        self.cuv = cu.version()
        self.idle = IdleMonitor(cu=cu)
        self.bridge = CUBridge(cu=cu)
        self.start_signal = StartSignal(cu=cu)
        self.grid = Grid(parent=self)
        self.home = Home(parent=self)
        self.drivers = {
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
        self.bridge.update_grid.connect(self.grid.driver_change)
        self.start_signal.ready_to_run.connect(self.startAfterSignal)
        self.start_signal.show_lights.connect(self.grid.start_signal.showLight)
        self.idle.update_state.connect(self.show_state)
        self.idle.start()

    def initUI(self):

        self.statusBar().showMessage('Ready')

        #self.showMaximized()
        self.setWindowTitle('RMS')
        self.showHome()
        self.show()

    def showHome(self):
        for i in range(0, 6):
            try:
                n = self.drivers[i]['name']
                self.home.setOk(i, True)
                self.home.setName(i, n)
            except KeyError:
                self.home.setOk(i, False)
                self.home.setName(i, '')

        self.setCentralWidget(self.home)

    def showGrid(self):
        self.grid.resetDrivers()
        for addr, driver in self.drivers.items():
            self.grid.addDriver(addr, driver)

        self.setCentralWidget(self.grid)
        print(5)

    def startTraining(self):
        self.idle.stop = True
        self.idle.wait()
        print(self.drivers)
        self.showGrid()
        self.bridge.reset()
        self.start_signal.start()

    @pyqtSlot()
    def startAfterSignal(self):
        self.bridge.start()

    @pyqtSlot(int)
    def show_state(self, mode):
        self.statusBar().showMessage('CU version: ' + str(self.cuv) + ', mode: ' + str(mode))

    def closeEvent(self, event):
        result = QMessageBox.question(self,
                                      "Confirm Exit...",
                                      "Are you sure you want to exit ?",
                                      QMessageBox.Yes | QMessageBox.No)
        event.ignore()

        if result == QMessageBox.Yes:
            event.accept()
            self.bridge.stop = True
            self.bridge.wait()
            self.idle.stop = True
            self.idle.wait()
            self.start_signal.stop = True
            self.start_signal.wait()


if __name__ == '__main__':
    app = QApplication(sys.argv)

    with contextlib.closing(ControlUnit('/dev/ttyUSB0', timeout=1.0)) as cu:
        print('CU version %s' % cu.version())
        ex = RMS(cu)
        sys.exit(app.exec_())
