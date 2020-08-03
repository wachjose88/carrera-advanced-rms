
from PyQt5.QtWidgets import QWidget, QGridLayout, \
                            QLabel, QVBoxLayout, QSizePolicy, \
                            QCheckBox, QLineEdit, QPushButton, QHBoxLayout, \
                            QSpinBox, QTabWidget
from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtGui import QFont
from utils import HSep, VSep
from constants import COMP_MODE__QUALIFYING_LAPS, \
                      COMP_MODE__QUALIFYING_TIME, \
                      COMP_MODE__QUALIFYING_LAPS_SEQ, \
                      COMP_MODE__QUALIFYING_TIME_SEQ, \
                      COMP_MODE__RACE_LAPS, \
                      COMP_MODE__RACE_TIME, \
                      DUMMY_IDS


class CompTime(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.vbox = QVBoxLayout(self)
        self.dtext = QLabel(self.tr('Duration in minutes:'))
        self.vbox.addWidget(self.dtext)
        self.duration = QSpinBox()
        self.duration.setMinimum(1)
        self.duration.setSuffix(self.tr(' Minutes'))
        self.duration.setValue(10)
        self.vbox.addWidget(self.duration)
        self.setLayout(self.vbox)


class CompLaps(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.vbox = QVBoxLayout(self)
        self.dtext = QLabel(self.tr('Duration in laps'))
        self.vbox.addWidget(self.dtext)
        self.duration = QSpinBox()
        self.duration.setMinimum(1)
        self.duration.setSuffix(self.tr(' Laps'))
        self.duration.setValue(20)
        self.vbox.addWidget(self.duration)
        self.setLayout(self.vbox)


class RaceParams(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.vbox = QVBoxLayout(self)
        self.modetab = QTabWidget()
        self.vbox.addWidget(self.modetab)
        self.complaps = CompLaps()
        self.modetab.addTab(self.complaps, self.tr('Laps'))
        self.comptime = CompTime()
        self.modetab.addTab(self.comptime, self.tr('Time'))
        self.setLayout(self.vbox)

    def getCompMode(self):
        if self.modetab.currentWidget() == self.complaps:
            return COMP_MODE__RACE_LAPS
        if self.modetab.currentWidget() == self.comptime:
            return COMP_MODE__RACE_TIME

    def getDuration(self):
        if self.modetab.currentWidget() == self.complaps:
            return self.complaps.duration.value()
        if self.modetab.currentWidget() == self.comptime:
            return self.comptime.duration.value()


class QualifyingParams(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.vbox = QVBoxLayout(self)
        self.modetab = QTabWidget()
        self.vbox.addWidget(self.modetab)
        self.complaps = CompLaps()
        self.modetab.addTab(self.complaps, self.tr('Laps'))
        self.comptime = CompTime()
        self.modetab.addTab(self.comptime, self.tr('Time'))
        self.sequential = QCheckBox()
        self.sequential.setText(self.tr('Sequential'))
        self.vbox.addWidget(self.sequential)
        self.setLayout(self.vbox)

    def getCompMode(self):
        if self.modetab.currentWidget() == self.complaps:
            if self.sequential.isChecked():
                return COMP_MODE__QUALIFYING_LAPS_SEQ
            return COMP_MODE__QUALIFYING_LAPS
        if self.modetab.currentWidget() == self.comptime:
            if self.sequential.isChecked():
                return COMP_MODE__QUALIFYING_TIME_SEQ
            return COMP_MODE__QUALIFYING_TIME

    def getDuration(self):
        if self.modetab.currentWidget() == self.complaps:
            return self.complaps.duration.value()
        if self.modetab.currentWidget() == self.comptime:
            return self.comptime.duration.value()


class Home(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        self.controller = QGridLayout()
        self.controller_ok = []
        self.controller_name = []
        for i in range(0, 6):
            ok = QCheckBox()
            ok.setText(self.tr('Controller ') + str(i+1))
            self.controller.addWidget(ok, 0, i)
            self.controller_ok.append(ok)
            name = QLineEdit()
            self.controller.addWidget(name, 1, i)
            self.controller_name.append(name)
        self.vml = QVBoxLayout()
        self.vml.setSpacing(10)
        self.headFont = QFont()
        self.headFont.setPointSize(45)
        self.headFont.setBold(True)
        self.headline = QLabel(self.tr('Carrera RMS'))
        self.headline.setFont(self.headFont)
        self.vml.addWidget(self.headline)
        self.vml.addWidget(HSep())
        self.vml.addLayout(self.controller)
        self.vml.addWidget(HSep())
        self.starts = QHBoxLayout()
        self.vml.addLayout(self.starts)
        self.vml.addWidget(HSep())
        self.start_training = QPushButton()
        self.start_training.setText(self.tr('Training'))
        self.start_training.clicked.connect(self.startTraining_click)
        self.start_training.setSizePolicy(QSizePolicy.Expanding,
                                          QSizePolicy.Expanding)
        self.starts.addWidget(self.start_training)
        self.starts.addWidget(VSep())
        self.qualifyingparams = QualifyingParams()
        self.qualifyingparams.setSizePolicy(QSizePolicy.Expanding,
                                            QSizePolicy.Maximum)
        self.qhbox = QVBoxLayout()
        self.qhbox.addWidget(self.qualifyingparams)
        self.start_qualifying = QPushButton()
        self.start_qualifying.setText(self.tr('Qualifying'))
        self.start_qualifying.clicked.connect(self.startQualifying_click)
        self.start_qualifying.setSizePolicy(QSizePolicy.Expanding,
                                            QSizePolicy.Expanding)
        self.qhbox.addWidget(self.start_qualifying)
        self.starts.addLayout(self.qhbox)
        self.starts.addWidget(VSep())
        self.raceparams = RaceParams()
        self.raceparams.setSizePolicy(QSizePolicy.Expanding,
                                      QSizePolicy.Maximum)
        self.rhbox = QVBoxLayout()
        self.rhbox.addWidget(self.raceparams)
        self.start_race = QPushButton()
        self.start_race.setText(self.tr('Race'))
        self.start_race.clicked.connect(self.startRace_click)
        self.start_race.setSizePolicy(QSizePolicy.Expanding,
                                      QSizePolicy.Expanding)
        self.rhbox.addWidget(self.start_race)
        self.starts.addLayout(self.rhbox)
        self.fullscreen = QPushButton()
        self.fullscreen.setText(self.tr('Fullscreen'))
        self.fullscreen.clicked.connect(self.fullscreen_click)
        self.vml.addWidget(self.fullscreen)
        self.statistics = QPushButton()
        self.statistics.setText(self.tr('Statistics'))
        self.vml.addWidget(self.statistics)
        self.settings = QPushButton()
        self.settings.setText(self.tr('Settings'))
        self.vml.addWidget(self.settings)
        self.exitrms = QPushButton()
        self.exitrms.setText(self.tr('Exit'))
        self.exitrms.clicked.connect(self.exitrms_click)
        self.vml.addWidget(self.exitrms)
        self.setLayout(self.vml)

    @pyqtSlot()
    def exitrms_click(self):
        self.parent().parent().close()

    @pyqtSlot()
    def fullscreen_click(self):
        if self.parent().parent().windowState() & Qt.WindowFullScreen:

            if self.parent().parent().cuv not in DUMMY_IDS:
                self.parent().parent().showMaximized()
            else:
                self.parent().parent().showNormal()
            self.fullscreen.setText(self.tr('Fullscreen'))
        else:
            self.parent().parent().showFullScreen()
            self.fullscreen.setText(self.tr('Exit Fullscreen'))

    def getDrivers(self):
        d = {}
        for i in range(0, 6):
            if self.getOk(i):
                p = {'pos': 0, 'name': self.getName(i)}
                if self.qualifyingparams.getCompMode() in [
                        COMP_MODE__QUALIFYING_LAPS_SEQ,
                        COMP_MODE__QUALIFYING_TIME_SEQ]:
                    p['qualifying_cu_driver'] = None
                d[i] = p
        return d

    @pyqtSlot()
    def startRace_click(self):
        self.parent().parent().drivers = self.getDrivers()
        self.parent().parent().startRace(self.raceparams.getCompMode(),
                                         self.raceparams.getDuration())

    @pyqtSlot()
    def startQualifying_click(self):
        self.parent().parent().drivers = self.getDrivers()
        self.parent().parent().startQualifying(
            self.qualifyingparams.getCompMode(),
            self.qualifyingparams.getDuration())

    @pyqtSlot()
    def startTraining_click(self):
        self.parent().parent().drivers = self.getDrivers()
        self.parent().parent().startTraining()

    def getOk(self, addr):
        return self.controller_ok[addr].isChecked()

    def getName(self, addr):
        return self.controller_name[addr].text()

    def setOk(self, addr, checked):
        self.controller_ok[addr].setChecked(checked)

    def setName(self, addr, name):
        self.controller_name[addr].setText(name)
