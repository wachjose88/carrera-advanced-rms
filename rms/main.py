#from bridge import CUBridge
from dummy import CUBridge
from bridge import GUIBridge
import contextlib
from carreralib import ControlUnit
import threading
import time
import sys
from PyQt5.QtWidgets import QMainWindow, QApplication, QMessageBox, \
                            QVBoxLayout, QWidget
from gui import Grid, Home


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
        self.gui_bridge = GUIBridge(mainwindow=self, lock=self.lock)
        self.gui_bridge_thread = threading.Thread(target=self.gui_bridge.run, args=())
        self.gui_bridge_thread.start()
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

    def initUI(self):

        self.statusBar().showMessage('Ready')

        self.showMaximized()
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

    def startTraining(self):
        print(self.drivers)
        self.showGrid()
        self.gui_bridge.running = True

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
            self.gui_bridge.stop = True
            self.gui_bridge_thread.join()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = RMS()
    sys.exit(app.exec_())
