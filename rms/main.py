
import contextlib
import sys
import argparse
import locale

from PyQt5.QtCore import pyqtSlot, QTranslator, QLibraryInfo
from PyQt5.QtWidgets import QMainWindow, QApplication, QMessageBox, \
    QStackedWidget

from bridge import CUBridge, StartSignal, IdleMonitor
from gui import Grid, Home, ThreadTranslation, ResultList
from tts import TTSHandler
from constants import *


class RMS(QMainWindow):

    def __init__(self, cu, cu_instance):
        super().__init__()
        self.cuv = cu.version()
        self.drivers = {
            0: {
                'pos': 4,
                'name': 'Josef'
            },
            1: {
                'pos': 2,
                'name': 'Papa'
            }
        }
        self.comp_mode = COMP_MODE__TRAINING
        self.comp_duration = 0
        self.tts = TTSHandler()
        self.tts.start()
        self.main_stack = QStackedWidget(self)
        self.threadtranslation = ThreadTranslation()
        self.main_stack.addWidget(self.threadtranslation)
        self.idle = IdleMonitor(cu=cu, cu_instance=cu_instance)
        self.bridge = CUBridge(cu=cu, cu_instance=cu_instance,
                               selected_drivers=self.drivers, tts=self.tts,
                               threadtranslation=self.threadtranslation)
        self.start_signal = StartSignal(cu=cu, cu_instance=cu_instance)
        self.grid = Grid(parent=self)
        self.home = Home(parent=self)
        self.resultlist = ResultList(parent=self)
        self.main_stack.addWidget(self.home)
        self.main_stack.addWidget(self.grid)
        self.main_stack.addWidget(self.resultlist)
        self.bridge.update_grid.connect(self.grid.driver_change)
        self.bridge.comp_state.connect(self.comp_state_update)
        self.bridge.comp_finished.connect(self.comp_finished_all)
        self.start_signal.ready_to_run.connect(self.startAfterSignal)
        self.start_signal.show_lights.connect(self.grid.showLight)
        self.idle.update_state.connect(self.show_state)
        self.setCentralWidget(self.main_stack)
        self.initUI()

    def initUI(self):

        self.statusBar().showMessage('Ready')

        if self.cuv not in ['d', 'dummy']:
            self.showMaximized()
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

    def showResultList(self, cu_drivers):
        self.stopAllThreads()
        self.resultlist.resetDrivers()
        self.resultlist.addDrivers(self.drivers, cu_drivers, self.grid.sort_mode)
        self.main_stack.setCurrentWidget(self.resultlist)

    def showGrid(self):
        self.grid.resetDrivers()
        for addr, driver in self.drivers.items():
            self.grid.addDriver(addr, driver)

        self.main_stack.setCurrentWidget(self.grid)
        self.stopAllThreads()

    def startRace(self, mode, duration):
        self.comp_mode = mode
        self.comp_duration = duration
        self.grid.sort_mode = SORT_MODE__LAPS
        self.showGrid()
        self.bridge.reset(self.drivers)
        self.startStartSignalThread()

    def startTraining(self):
        self.comp_mode = COMP_MODE__TRAINING
        self.grid.sort_mode = SORT_MODE__LAPTIME
        self.showGrid()
        self.bridge.reset(self.drivers)
        self.startStartSignalThread()

    @pyqtSlot()
    def startAfterSignal(self):
        self.startBridgeThread()

    @pyqtSlot(int, list)
    def comp_finished_all(self, rtime, drivers):
        self.stopAllThreads()
        self.showResultList(drivers)

    @pyqtSlot(int, list)
    def comp_state_update(self, rtime, cu_drivers):
        if self.comp_mode == COMP_MODE__TRAINING:
            self.grid.training_state.showTime(rtime=rtime)
        elif self.comp_mode == COMP_MODE__RACE_LAPS:
            self.grid.race_state.handleUpdateLaps(rtime=rtime,
                                                  laps=self.comp_duration,
                                                  cu_drivers=cu_drivers)
        elif self.comp_mode == COMP_MODE__RACE_TIME:
            self.grid.race_state.handleUpdateTime(rtime=rtime,
                                                  minutes=self.comp_duration,
                                                  cu_drivers=cu_drivers)

    @pyqtSlot(int)
    def show_state(self, mode):
        self.statusBar().showMessage(
            self.tr('CU version: ') + str(self.cuv) + self.tr(', mode: ') + str(mode))

    def closeEvent(self, event):
        result = QMessageBox.question(self,
                                      self.tr("Confirm Exit..."),
                                      self.tr("Are you sure you want to exit ?"),
                                      QMessageBox.Yes | QMessageBox.No)
        event.ignore()

        if result == QMessageBox.Yes:
            event.accept()
            self.stopAllThreads()
            self.tts.stop = True
            self.tts.wait()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    qtbase_translator = QTranslator()
    qtbase_translator.load("qtbase_" + locale.getlocale()[0][0:2],
        QLibraryInfo.location(QLibraryInfo.TranslationsPath))
    app.installTranslator(qtbase_translator)
    qt_translator = QTranslator()
    qt_translator.load("qt_" + locale.getlocale()[0][0:2],
        QLibraryInfo.location(QLibraryInfo.TranslationsPath))
    app.installTranslator(qt_translator)
    translator = QTranslator()
    translator.load("locales/carrera_" + locale.getlocale()[0][0:2])
    app.installTranslator(translator)
    parser = argparse.ArgumentParser(
        description='Advanced Race Management for Carrera Digital')
    parser.add_argument('-cu', '--controlunit',
                        help='cu address or dummy', required=True)
    args = parser.parse_args()
    if args.controlunit in ['d', 'dummy']:
        from dummy import ControlUnit
    else:
        from carreralib import ControlUnit
        print(args.controlunit)
    with contextlib.closing(ControlUnit(str(args.controlunit), timeout=3.0)) as cu:
        print('CU version %s' % cu.version())
        ex = RMS(cu, ControlUnit)
        sys.exit(app.exec_())
