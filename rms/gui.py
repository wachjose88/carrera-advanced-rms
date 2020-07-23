
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QGridLayout, \
                            QLabel, QVBoxLayout, QSizePolicy, QProgressBar, \
                            QCheckBox, QLineEdit, QPushButton, QHBoxLayout, \
                            QStackedWidget
from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtGui import QFont, QColor, QPainter
from utils import formattime


class ThreadTranslation(QWidget):
    def __init__(self):
        super().__init__()
        self.hbox = QHBoxLayout()
        self.letsgo = QLabel(self.tr("let's go!"))
        self.hbox.addWidget(self.letsgo)
        self.setLayout(self.hbox)


class StartLight(QWidget):
    def __init__(self):
        super().__init__()
        self.onVal = QColor(40, 40, 40)
        self.update()

    def setOn(self):
        self.onVal = Qt.red
        self.update()

    def setGreen(self):
        self.onVal = Qt.green
        self.update()

    def setOff(self):
        self.onVal = QColor(40, 40, 40)
        self.update()

    def paintEvent(self, e):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(self.onVal)
        painter.drawEllipse(0, 0, 50, 50)


class StartLights(QWidget):

    def __init__(self, parent = None):
        super().__init__(parent)
        hbox = QHBoxLayout(self)
        self.lightOne = StartLight()
        self.lightTwo = StartLight()
        self.lightThree = StartLight()
        self.lightFour = StartLight()
        self.lightFive = StartLight()
        hbox.addWidget(self.lightOne)
        hbox.addWidget(self.lightTwo)
        hbox.addWidget(self.lightThree)
        hbox.addWidget(self.lightFour)
        hbox.addWidget(self.lightFive)


class TrainingState(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.headFont = QFont()
        self.headFont.setPointSize(50)
        self.headFont.setBold(True)
        self.hbox = QVBoxLayout(self)
        self.starttext = QLabel(self.tr('Training'))
        self.starttext.setFont(self.headFont)
        self.hbox.addWidget(self.starttext)
        self.stop_live = QPushButton()
        self.stop_live.setText(self.tr('Stop'))
        self.stop_live.clicked.connect(self.stop_live_click)
        self.hbox.addWidget(self.stop_live)
        self.setLayout(self.hbox)

    def showTime(self, rtime):
        self.starttext.setText('Training: ' + str(formattime(rtime)))

    @pyqtSlot()
    def stop_live_click(self):
        for driver in self.parent().parent().parent().parent().bridge.drivers:
            driver.racing = False


class FalseStart(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.headFont = QFont()
        self.headFont.setPointSize(50)
        self.headFont.setBold(True)
        hbox = QHBoxLayout(self)
        self.starttext = QLabel('False Start')
        self.starttext.setFont(self.headFont)
        hbox.addWidget(self.starttext)
        self.setLayout(hbox)


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
        self.vml.addLayout(self.controller)
        self.starts = QHBoxLayout()
        self.vml.addLayout(self.starts)
        self.start_training = QPushButton()
        self.start_training.setText(self.tr('Training'))
        self.start_training.clicked.connect(self.startTraining_click)
        self.start_training.setSizePolicy(QSizePolicy.Expanding,
                                          QSizePolicy.Expanding)
        self.starts.addWidget(self.start_training)
        self.start_qualifying = QPushButton()
        self.start_qualifying.setText(self.tr('Qualifying'))
        self.start_qualifying.setSizePolicy(QSizePolicy.Expanding,
                                            QSizePolicy.Expanding)
        self.starts.addWidget(self.start_qualifying)
        self.start_race = QPushButton()
        self.start_race.setText(self.tr('Race'))
        self.start_race.setSizePolicy(QSizePolicy.Expanding,
                                      QSizePolicy.Expanding)
        self.starts.addWidget(self.start_race)
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
        self.setLayout(self.vml)

    @pyqtSlot()
    def fullscreen_click(self):
        if self.parent().parent().windowState() & Qt.WindowFullScreen:
            self.parent().parent().showNormal()
            self.fullscreen.setText(self.tr('Fullscreen'))
        else:
            self.parent().parent().showFullScreen()
            self.fullscreen.setText(self.tr('Exit Fullscreen'))

    @pyqtSlot()
    def startTraining_click(self):
        d = {}
        for i in range(0, 6):
            if self.getOk(i):
                p = {'pos': 0, 'name': self.getName(i)}
                d[i] = p
        self.parent().parent().drivers = d
        self.parent().parent().startTraining()

    def getOk(self, addr):
        return self.controller_ok[addr].isChecked()

    def getName(self, addr):
        return self.controller_name[addr].text()

    def setOk(self, addr, checked):
        self.controller_ok[addr].setChecked(checked)

    def setName(self, addr, name):
        self.controller_name[addr].setText(name)


class ResultList(QWidget):

    SORT_MODE__LAPS = 0
    SORT_MODE__LAPTIME = 1

    def __init__(self, parent=None):
        super().__init__(parent)
        self.driver_ui = {}
        self.initUI()

    def initUI(self):
        self.vbox = QVBoxLayout()
        self.mainLayout = QGridLayout()
        self.mainLayout.setSpacing(10)
        self.mainLayout.setHorizontalSpacing(10)
        self.headerFont = QFont()
        self.headerFont.setPointSize(14)
        self.headerFont.setBold(True)
        self.labelArr = [self.tr('Pos'), self.tr('Driver'),
                         self.tr('Laps'),
                         self.tr('Time'), self.tr('Difference')]
        for index, label in enumerate(self.labelArr):
            self.headerLabel = QLabel(label)
            self.headerLabel.setFont(self.headerFont)
            self.mainLayout.addWidget(self.headerLabel, 0,
                                      index, Qt.AlignHCenter)
        self.mainLayout.setColumnStretch(1, 1)
        self.mainLayout.setColumnStretch(2, 1)
        self.mainLayout.setColumnStretch(3, 2)
        self.posFont = QFont()
        self.posFont.setPointSize(35)
        self.posFont.setBold(True)
        self.nameFont = QFont()
        self.nameFont.setPointSize(20)
        self.nameFont.setBold(True)
        self.timeFont = QFont()
        self.timeFont.setPointSize(36)
        self.timeFont.setBold(True)
        self.timeFont.setStyleHint(QFont.TypeWriter)
        self.timeFont.setFamily('monospace')
        self.posCss = "QLabel{ border-radius: 10px; border-color: black; border: 5px solid black; background-color: white}"
        self.lcdCss = "QLCDNumber{ border-radius: 10px; background-color: black}"
        self.lcdColor = QColor(255, 0, 0)
        self.num_row = 1
        self.vbox.addLayout(self.mainLayout)
        self.vbox.addStretch(1)
        self.back = QPushButton()
        self.back.setText(self.tr('Back'))
        self.back.clicked.connect(self.back_click)
        self.vbox.addWidget(self.back)
        self.setLayout(self.vbox)

    def addDrivers(self, drivers, cu_drivers, sort_mode):
        rank = []
        for addr, driver in drivers.items():
            rank.append(cu_drivers[addr])
        if sort_mode == self.SORT_MODE__LAPS:
            rank.sort(key=lambda dr: 0 if dr.bestlap is None else (-dr.laps,
                                                                   dr.time))
        if sort_mode == self.SORT_MODE__LAPTIME:
            rank.sort(key=lambda dr: 0 if dr.bestlap is None else dr.bestlap)

        for crank in rank:
            addr = crank.num
            drank = rank.index(crank) + 1
            driverPos = QLabel(str(drank))
            driverPos.setStyleSheet(self.posCss)
            driverPos.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Expanding)
            driverPos.setFont(self.posFont)
            self.mainLayout.addWidget(driverPos, self.num_row, 0)
            name = QLabel(str(crank.name))
            name.setStyleSheet(self.posCss)
            name.setFont(self.nameFont)
            self.mainLayout.addWidget(name, self.num_row, 1)
            laps = QLabel(str(crank.laps))
            laps.setStyleSheet(self.posCss)
            laps.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Expanding)
            laps.setFont(self.timeFont)
            self.mainLayout.addWidget(laps, self.num_row, 2)
            dtime = 0
            ftime = ''
            if sort_mode == self.SORT_MODE__LAPS:
                ftime = formattime(crank.time, longfmt=False)
                if drank == 1:
                    dtime = ' '
                else:
                    dtime = '+' + formattime(crank.time - rank[0].time, longfmt=False)
            if sort_mode == self.SORT_MODE__LAPTIME:
                ftime = formattime(crank.bestlap, longfmt=False)
                if drank == 1:
                    dtime = ' '
                else:
                    dtime = '+' + formattime(crank.bestlap - rank[0].bestlap, longfmt=False)
            fotime = QLabel(str(ftime))
            fotime.setStyleSheet(self.posCss)
            fotime.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Expanding)
            fotime.setFont(self.timeFont)
            self.mainLayout.addWidget(fotime, self.num_row, 3)
            otime = QLabel(str(dtime))
            otime.setStyleSheet(self.posCss)
            otime.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Expanding)
            otime.setFont(self.timeFont)
            self.mainLayout.addWidget(otime, self.num_row, 4)
            self.driver_ui[addr] = {
                'pos': driverPos,
                'name': name,
                'laps': laps,
                'otime': otime
            }
            self.num_row += 1

    def resetDrivers(self):
        for addr, row in self.driver_ui.items():
            for name, widget in row.items():
                self.mainLayout.removeWidget(widget)
                widget.deleteLater()
                del widget
        self.driver_ui = {}
        self.num_row = 1

    @pyqtSlot()
    def back_click(self):
        self.parent().parent().showHome()


class Grid(QWidget):

    SORT_MODE__LAPS = 0
    SORT_MODE__LAPTIME = 1

    def __init__(self, parent=None):
        super().__init__(parent)
        self.sort_mode = self.SORT_MODE__LAPS
        self.driver_ui = {}
        self.initUI()
        self.initDriverUI()

    def initUI(self):
        self.mainLayout = QGridLayout()
        self.mainLayout.setSpacing(10)
        self.mainLayout.setHorizontalSpacing(10)
        self.headerFont = QFont()
        self.headerFont.setPointSize(14)
        self.headerFont.setBold(True)
        self.labelArr = [self.tr('Pos'), self.tr('Driver'), self.tr('Total'),
                         self.tr('Laps'),
                         self.tr('Laptime'), self.tr('Best Lap'),
                         self.tr('Fuel'), self.tr('Pits')]
        for index, label in enumerate(self.labelArr):
            self.headerLabel = QLabel(label)
            self.headerLabel.setFont(self.headerFont)
            self.mainLayout.addWidget(self.headerLabel, 0,
                                    index, Qt.AlignHCenter)
        self.mainLayout.setColumnStretch(1, 1)
        self.mainLayout.setColumnStretch(2, 1)
        self.mainLayout.setColumnStretch(3, 2)
        self.mainLayout.setColumnStretch(4, 3)
        self.mainLayout.setColumnStretch(5, 3)
        self.mainLayout.setColumnStretch(6, 2)
        self.mainLayout.setColumnStretch(7, 1)
        self.stateStack = QStackedWidget()
        self.start_signal = StartLights()
        self.false_start = FalseStart()
        self.training_state = TrainingState()
        self.stateStack.addWidget(self.false_start)
        self.stateStack.addWidget(self.start_signal)
        self.stateStack.addWidget(self.training_state)
        self.vml = QVBoxLayout()
        self.vml.addLayout(self.mainLayout)
        self.vml.addStretch(1)
        self.vml.addWidget(self.stateStack)
        self.setLayout(self.vml)

    def initDriverUI(self):
        self.posFont = QFont()
        self.posFont.setPointSize(35)
        self.posFont.setBold(True)
        self.nameFont = QFont()
        self.nameFont.setPointSize(20)
        self.nameFont.setBold(True)
        self.timeFont = QFont()
        self.timeFont.setPointSize(36)
        self.timeFont.setBold(True)
        self.timeFont.setStyleHint(QFont.TypeWriter)
        self.timeFont.setFamily('monospace')
        self.posCss = "QLabel{ border-radius: 10px; border-color: black; border: 5px solid black; background-color: white}"
        self.lcdCss = "QLCDNumber{ border-radius: 10px; background-color: black}"
        self.lcdColor = QColor(255, 0, 0)
        self.num_row = 1

    def addDriver(self, addr, driver):
        driverPos = QLabel(str(driver['pos']))
        driverPos.setStyleSheet(self.posCss)
        driverPos.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Expanding)
        driverPos.setFont(self.posFont)
        self.mainLayout.addWidget(driverPos, self.num_row, 0)
        name = QLabel(str(driver['name']))
        name.setStyleSheet(self.posCss)
        name.setFont(self.nameFont)
        self.mainLayout.addWidget(name, self.num_row, 1)
        total = QLabel('00:00')
        total.setStyleSheet(self.posCss)
        total.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Expanding)
        total.setFont(self.timeFont)
        self.mainLayout.addWidget(total, self.num_row, 2)
        laps = QLabel('0')
        laps.setStyleSheet(self.posCss)
        laps.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Expanding)
        laps.setFont(self.timeFont)
        self.mainLayout.addWidget(laps, self.num_row, 3)
        laptime = QLabel('00:00')
        laptime.setStyleSheet(self.posCss)
        laptime.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Expanding)
        laptime.setFont(self.timeFont)
        self.mainLayout.addWidget(laptime, self.num_row, 4)
        bestlaptime = QLabel('00:00')
        bestlaptime.setStyleSheet(self.posCss)
        bestlaptime.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Expanding)
        bestlaptime.setFont(self.timeFont)
        self.mainLayout.addWidget(bestlaptime, self.num_row, 5)
        fuelbar = QProgressBar()
        fuelbar.setOrientation(Qt.Horizontal)
        fuelbar.setStyleSheet("QProgressBar{ color: white; background-color: black; border: 5px solid black; border-radius: 10px; text-align: center}\
                                    QProgressBar::chunk { background: qlineargradient(x1: 1, y1: 0.5, x2: 0, y2: 0.5, stop: 0 #00AA00, stop: " + str(0.92 - (1 / (15))) + " #22FF22, stop: " + str(0.921 - (1 / (15))) + " #22FF22, stop: " + str(1.001 - (1 / (15))) + " red, stop: 1 #550000); }")
        fuelbar.setMinimum(0)
        fuelbar.setMaximum(15)
        fuelbar.setValue(15)
        fuelbar.setFont(self.timeFont)
        fuelbar.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Expanding)
        self.mainLayout.addWidget(fuelbar, self.num_row, 6)
        pits = QLabel('00')
        pits.setStyleSheet(self.posCss)
        pits.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Expanding)
        pits.setFont(self.timeFont)
        pits.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Expanding)
        self.mainLayout.addWidget(pits, self.num_row, 7)
        self.driver_ui[addr] = {
            'pos': driverPos,
            'name': name,
            'total': total,
            'laps': laps,
            'laptime': laptime,
            'bestlaptime': bestlaptime,
            'fuelbar': fuelbar,
            'pits': pits
        }
        self.num_row += 1

    def resetDrivers(self):
        for addr, row in self.driver_ui.items():
            for name, widget in row.items():
                self.mainLayout.removeWidget(widget)
                widget.deleteLater()
                del widget
        self.driver_ui = {}
        self.num_row = 1

    @pyqtSlot(list)
    def driver_change(self, cu_drivers):
        rank = []
        for addr, driver in self.driver_ui.items():
            rank.append(cu_drivers[addr])
        if self.sort_mode == self.SORT_MODE__LAPS:
            rank.sort(key=lambda dr: 0 if dr.bestlap is None else (-dr.laps,
                                                                   dr.time))
        if self.sort_mode == self.SORT_MODE__LAPTIME:
            rank.sort(key=lambda dr: 0 if dr.bestlap is None else dr.bestlap)
        for addr, driver in self.driver_ui.items():
            try:
                di = cu_drivers[addr]
                p = str(di.pits)
                if di.pit:
                    p += self.tr(' (in)')
                self.updateDriver(
                    addr=addr,
                    pos=rank.index(di)+1,
                    total=di.time,
                    laps=di.laps,
                    laptime=di.laptime,
                    bestlaptime=di.bestlap,
                    fuelbar=di.fuel,
                    pits=p)
            except KeyError:
                pass
            except ValueError:
                pass



    def updateDriver(self, addr, pos=None, name=None, total=None,
                     laps=None, laptime=None, bestlaptime=None,
                     fuelbar=None, pits=None):
        try:
            r = self.driver_ui[addr]
            if pos is not None:
                r['pos'].setText(str(pos))
            if name is not None:
                r['name'].setText(str(name))
            if total is not None:
                r['total'].setText(str(formattime(total)))
            if laps is not None:
                r['laps'].setText(str(laps))
            if laptime is not None:
                r['laptime'].setText(str(formattime(laptime, longfmt=False)))
            if bestlaptime is not None:
                r['bestlaptime'].setText(str(formattime(bestlaptime, longfmt=False)))
            if fuelbar is not None:
                r['fuelbar'].setValue(fuelbar)
            if pits is not None:
                r['pits'].setText(str(pits))
        except KeyError:
            print('wrong addr', addr)

    @pyqtSlot(int)
    def showLight(self, number):
        self.stateStack.setCurrentWidget(self.start_signal)
        if number == 2:
            self.start_signal.lightOne.setOn()
        elif number == 3:
            self.start_signal.lightTwo.setOn()
        elif number == 4:
            self.start_signal.lightThree.setOn()
        elif number == 5:
            self.start_signal.lightFour.setOn()
        elif number == 6:
            self.start_signal.lightFive.setOn()
        elif number == 0:
            self.stateStack.setCurrentWidget(self.false_start)
        elif number == 100:
            self.start_signal.lightOne.setGreen()
            self.start_signal.lightTwo.setGreen()
            self.start_signal.lightThree.setGreen()
            self.start_signal.lightFour.setGreen()
            self.start_signal.lightFive.setGreen()
            self.stateStack.setCurrentWidget(self.training_state)
        elif number == 101:
            self.start_signal.lightOne.setOff()
            self.start_signal.lightTwo.setOff()
            self.start_signal.lightThree.setOff()
            self.start_signal.lightFour.setOff()
            self.start_signal.lightFive.setOff()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ResultList()
    ex.show()
    sys.exit(app.exec_())
