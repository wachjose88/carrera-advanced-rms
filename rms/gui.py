
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QGridLayout, \
                            QLabel, QVBoxLayout, QSizePolicy, QProgressBar, \
                            QCheckBox, QLineEdit, QPushButton, QHBoxLayout
from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtGui import QFont, QColor, QPainter
from utils import formattime


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
        self.headFont = QFont()
        self.headFont.setPointSize(50)
        self.headFont.setBold(True)
        hbox = QHBoxLayout(self)
        self.lightOne = StartLight()
        self.lightTwo = StartLight()
        self.lightThree = StartLight()
        self.lightFour = StartLight()
        self.lightFive = StartLight()
        self.starttext = QLabel('Starting... ')
        self.starttext.setFont(self.headFont)
        hbox.addWidget(self.starttext)
        hbox.addWidget(self.lightOne)
        hbox.addWidget(self.lightTwo)
        hbox.addWidget(self.lightThree)
        hbox.addWidget(self.lightFour)
        hbox.addWidget(self.lightFive)

    @pyqtSlot(int)
    def showLight(self, number):
        if number == 2:
            self.lightOne.setOn()
        elif number == 3:
            self.lightTwo.setOn()
        elif number == 4:
            self.lightThree.setOn()
        elif number == 5:
            self.lightFour.setOn()
        elif number == 6:
            self.lightFive.setOn()
        elif number == 0:
            self.starttext.setText('False Start')
        elif number == 100:
            self.starttext.setText('Racing')
            self.lightOne.setGreen()
            self.lightTwo.setGreen()
            self.lightThree.setGreen()
            self.lightFour.setGreen()
            self.lightFive.setGreen()

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
            ok.setText('Controller ' + str(i+1))
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
        self.headline = QLabel('Carrera RMS')
        self.headline.setFont(self.headFont)
        self.vml.addWidget(self.headline)
        self.vml.addLayout(self.controller)
        self.starts = QHBoxLayout()
        self.vml.addLayout(self.starts)
        self.start_training = QPushButton()
        self.start_training.setText('Training')
        self.start_training.clicked.connect(self.startTraining_click)
        self.start_training.setSizePolicy(QSizePolicy.Expanding,
                                          QSizePolicy.Expanding)
        self.starts.addWidget(self.start_training)
        self.start_qualifying = QPushButton()
        self.start_qualifying.setText('Qualifying')
        self.start_qualifying.setSizePolicy(QSizePolicy.Expanding,
                                            QSizePolicy.Expanding)
        self.starts.addWidget(self.start_qualifying)
        self.start_race = QPushButton()
        self.start_race.setText('Race')
        self.start_race.setSizePolicy(QSizePolicy.Expanding,
                                      QSizePolicy.Expanding)
        self.starts.addWidget(self.start_race)
        self.statistics = QPushButton()
        self.statistics.setText('Statistics')
        self.vml.addWidget(self.statistics)
        self.settings = QPushButton()
        self.settings.setText('Settings')
        self.vml.addWidget(self.settings)
        self.setLayout(self.vml)

    @pyqtSlot()
    def startTraining_click(self):
        d = {}
        for i in range(0, 5):
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


class Grid(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
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
        self.labelArr = ['Pos', 'Driver', 'Total', 'Laps',
                         'Laptime', 'Best Lap', 'Fuel', 'Pits']
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
        self.start_signal = StartLights()
        self.vml = QVBoxLayout()
        self.vml.addLayout(self.mainLayout)
        self.vml.addStretch(1)
        self.vml.addWidget(self.start_signal)
        self.stop_live = QPushButton()
        self.stop_live.setText('Stop')
        self.stop_live.clicked.connect(self.stop_live_click)
        self.vml.addWidget(self.stop_live)
        self.setLayout(self.vml)

    def initDriverUI(self):
        self.posFont = QFont()
        self.posFont.setPointSize(35)
        self.posFont.setBold(True)
        self.nameFont = QFont()
        self.nameFont.setPointSize(20)
        self.nameFont.setBold(True)
        self.timeFont = QFont()
        self.timeFont.setPointSize(25)
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
        rank.sort(key=lambda dr: 0 if dr.bestlap is None else dr.bestlap)
        for addr, driver in self.driver_ui.items():
            try:
                di = cu_drivers[addr]
                p = str(di.pits)
                if di.pit:
                    p += ' (in)'
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


    @pyqtSlot()
    def stop_live_click(self):
        if self.parent().parent().bridge.stop is False:
            self.parent().parent().bridge.stop = True
            self.parent().parent().bridge.wait()
            self.parent().parent().start_signal.stop = True
            self.parent().parent().start_signal.wait()
        else:
            self.parent().parent().idle.stop = False
            self.parent().parent().idle.start()
            self.parent().setCurrentWidget(self.parent().parent().home)

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
                r['laptime'].setText(str(formattime(laptime)))
            if bestlaptime is not None:
                r['bestlaptime'].setText(str(formattime(bestlaptime)))
            if fuelbar is not None:
                r['fuelbar'].setValue(fuelbar)
            if pits is not None:
                r['pits'].setText(str(pits))
        except KeyError:
            print('wrong addr', addr)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Home()
    ex.show()
    sys.exit(app.exec_())
