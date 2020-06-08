
import contextlib
import sys
import argparse

from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QMainWindow, QApplication, QMessageBox, \
    QStackedWidget

from bridge import CUBridge, StartSignal, IdleMonitor
from gui import Grid, Home


class RMS(QMainWindow):

    def __init__(self, cu):
        super().__init__()
        self.cuv = cu.version()
        self.main_stack = QStackedWidget(self)
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
        self.main_stack.addWidget(self.home)
        self.main_stack.addWidget(self.grid)
        self.bridge.update_grid.connect(self.grid.driver_change)
        self.start_signal.ready_to_run.connect(self.startAfterSignal)
        self.start_signal.show_lights.connect(self.grid.start_signal.showLight)
        self.idle.update_state.connect(self.show_state)
        self.setCentralWidget(self.main_stack)
        self.initUI()

    def initUI(self):

        self.statusBar().showMessage('Ready')

        #self.showMaximized()
        self.setWindowTitle('RMS')
        self.showHome()
        self.show()

    def startBridgeThread(self):
        if not self.bridge.isRunning():
            self.bridge.stop = False
            self.bridge.start()

    def startIdleThread(self):
        if not self.idle.isRunning():
            self.idle.stop = False
            self.idle.start()

    def startStartSignalThread(self):
        if not self.start_signal.isRunning():
            self.start_signal.stop = False
            self.start_signal.start()

    def stopAllThreads(self):
        if self.bridge.isRunning():
            self.bridge.stop = True
            self.bridge.wait()
        if self.idle.isRunning():
            self.idle.stop = True
            self.idle.wait()
        if self.start_signal.isRunning():
            self.start_signal.stop = True
            self.start_signal.wait()

    def showHome(self):
        for i in range(0, 6):
            try:
                n = self.drivers[i]['name']
                self.home.setOk(i, True)
                self.home.setName(i, n)
            except KeyError:
                self.home.setOk(i, False)
                self.home.setName(i, '')

        self.main_stack.setCurrentWidget(self.home)
        self.stopAllThreads()
        self.startIdleThread()

    def showGrid(self):
        self.grid.resetDrivers()
        for addr, driver in self.drivers.items():
            self.grid.addDriver(addr, driver)

        self.main_stack.setCurrentWidget(self.grid)
        self.stopAllThreads()

    def startTraining(self):
        self.showGrid()
        self.bridge.reset()
        self.startStartSignalThread()

    @pyqtSlot()
    def startAfterSignal(self):
        self.startBridgeThread()

    @pyqtSlot(int)
    def show_state(self, mode):
        self.statusBar().showMessage(
            'CU version: ' + str(self.cuv) + ', mode: ' + str(mode))

    def closeEvent(self, event):
        result = QMessageBox.question(self,
                                      "Confirm Exit...",
                                      "Are you sure you want to exit ?",
                                      QMessageBox.Yes | QMessageBox.No)
        event.ignore()

        if result == QMessageBox.Yes:
            event.accept()
            self.stopAllThreads()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    parser = argparse.ArgumentParser(
        description='Advanced Race Management for Carrera Digital')
    parser.add_argument('-cu', '--controlunit',
                        help='cu address or dummy', required=True)
    args = parser.parse_args()
    if args.controlunit in ['d', 'dummy']:
        from dummy import ControlUnit
    else:
        from carreralib import ControlUnit
    with contextlib.closing(ControlUnit(args.controlunit, timeout=1.0)) as cu:
        print('CU version %s' % cu.version())
        ex = RMS(cu)
        sys.exit(app.exec_())
