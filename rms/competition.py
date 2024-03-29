
from PyQt5.QtWidgets import QWidget, QGridLayout, \
                            QLabel, QVBoxLayout, QSizePolicy, QProgressBar, \
                            QPushButton, QHBoxLayout, \
                            QStackedWidget, QInputDialog
from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtGui import QFont, QColor, QPainter
from utils import formattime, HSep
from constants import COMP_MODE__TRAINING, COMP_MODE__QUALIFYING_LAPS, \
                      COMP_MODE__QUALIFYING_TIME, \
                      COMP_MODE__QUALIFYING_LAPS_SEQ, \
                      COMP_MODE__QUALIFYING_TIME_SEQ, \
                      COMP_MODE__RACE_LAPS, \
                      COMP_MODE__RACE_TIME, \
                      SORT_MODE__LAPS, SORT_MODE__LAPTIME, TTS_LAPS_MOD, \
                      TTS_TIME_MOD, TTS_LAPS_REMAINING, TTS_TIME_REMAINING


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

    def __init__(self, parent=None):
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


class RaceState(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.headFont = QFont()
        self.headFont.setPointSize(25)
        self.headFont.setBold(True)
        self.hbox = QVBoxLayout(self)
        self.starttext = QLabel(self.tr('Race'))
        self.starttext.setFont(self.headFont)
        self.hbox.addWidget(self.starttext)
        self.setLayout(self.hbox)
        self.duration = 0
        self.rlaps = 0
        self.rtime = 0

    def handleUpdateLaps(self, rtime, laps, cu_drivers, tts=None):
        mlaps = 0
        for driver in cu_drivers:
            if driver.laps > mlaps:
                mlaps = driver.laps
            if driver.laps >= laps:
                driver.racing = False
        rlaps = laps-mlaps
        self.starttext.setText(self.tr('Race: ')
                               + str(formattime(rtime))
                               + self.tr(', %n Lap(s) remaining',
                                         '', rlaps))
        if tts and rlaps != self.rlaps and rlaps > 0 and \
                (rlaps % TTS_LAPS_MOD == 0 or rlaps in TTS_LAPS_REMAINING):
            if rlaps == 1:
                tts.say(self.tr('One Lap remaining'))
            else:
                tts.say(self.tr('%n Lap(s) remaining', '', rlaps))
        self.rlaps = rlaps

    def handleUpdateTime(self, rtime, minutes, cu_drivers, tts=None):
        cd = (minutes * 60 * 1000) - rtime
        cds = int(cd/1000)
        if cd <= 0:
            for driver in cu_drivers:
                driver.stopnext = True
            self.starttext.setText(self.tr('Race finished'))
        else:
            self.starttext.setText(self.tr('Race: ')
                                   + str(formattime(cd)))
        if tts and cds != self.rtime and cds > 0 and \
                (cds % TTS_TIME_MOD == 0 or cds in TTS_TIME_REMAINING):
            tts.say(self.tr('%n Seconds(s) remaining', '', cds))
        self.rtime = cds


class QualifyingState(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.headFont = QFont()
        self.headFont.setPointSize(25)
        self.headFont.setBold(True)
        self.hbox = QVBoxLayout(self)
        self.starttext = QLabel(self.tr('Qualifying'))
        self.starttext.setFont(self.headFont)
        self.hbox.addWidget(self.starttext)
        self.setLayout(self.hbox)
        self.duration = 0
        self.current_addr = -1
        self.rlaps = 0
        self.rtime = 0

    def handleUpdateLapsSeq(self, rtime, laps, cu_drivers, tts=None):
        mlaps = 0
        for driver in cu_drivers:
            if driver.laps > mlaps:
                mlaps = driver.laps
            if driver.laps >= laps:
                driver.racing = False
        rlaps = laps-mlaps
        self.starttext.setText(self.tr('Qualifying: ')
                               + str(formattime(rtime))
                               + self.tr(', %n Lap(s) remaining',
                                         '', rlaps))
        if tts and rlaps != self.rlaps and rlaps > 0 and \
                (rlaps % TTS_LAPS_MOD == 0 or rlaps in TTS_LAPS_REMAINING):
            if rlaps == 1:
                tts.say(self.tr('One Lap remaining'))
            else:
                tts.say(self.tr('%n Lap(s) remaining', '', rlaps))
        self.rlaps = rlaps

    def handleUpdateLaps(self, rtime, laps, cu_drivers, tts=None):
        mlaps = 0
        for driver in cu_drivers:
            if driver.laps > mlaps:
                mlaps = driver.laps
            if driver.laps >= laps:
                driver.racing = False
        rlaps = laps-mlaps
        self.starttext.setText(self.tr('Qualifying: ')
                               + str(formattime(rtime))
                               + self.tr(', %n Lap(s) remaining',
                                         '', rlaps))
        if tts and rlaps != self.rlaps and rlaps > 0 and \
                (rlaps % TTS_LAPS_MOD == 0 or rlaps in TTS_LAPS_REMAINING):
            if rlaps == 1:
                tts.say(self.tr('One Lap remaining'))
            else:
                tts.say(self.tr('%n Lap(s) remaining', '', rlaps))
        self.rlaps = rlaps

    def handleUpdateTimeSeq(self, rtime, minutes, cu_drivers, tts=None):
        cd = (minutes * 60 * 1000) - rtime
        cds = int(cd/1000)
        if cd <= 0:
            for driver in cu_drivers:
                driver.stopnext = True
            self.starttext.setText(self.tr('Qualifying finished'))
        else:
            self.starttext.setText(self.tr('Qualifying: ')
                                   + str(formattime(cd)))
        if tts and cds != self.rtime and cds > 0 and \
                (cds % TTS_TIME_MOD == 0 or cds in TTS_TIME_REMAINING):
            tts.say(self.tr('%n Seconds(s) remaining', '', cds))
        self.rtime = cds

    def handleUpdateTime(self, rtime, minutes, cu_drivers, tts=None):
        cd = (minutes * 60 * 1000) - rtime
        cds = int(cd/1000)
        if cd <= 0:
            for driver in cu_drivers:
                driver.stopnext = True
            self.starttext.setText(self.tr('Qualifying finished'))
        else:
            self.starttext.setText(self.tr('Qualifying: ')
                                   + str(formattime(cd)))
        if tts and cds != self.rtime and cds > 0 and \
                (cds % TTS_TIME_MOD == 0 or cds in TTS_TIME_REMAINING):
            tts.say(self.tr('%n Seconds(s) remaining', '', cds))
        self.rtime = cds


class TrainingState(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.headFont = QFont()
        self.headFont.setPointSize(25)
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
        self.headFont.setPointSize(25)
        self.headFont.setBold(True)
        self.hbox = QVBoxLayout(self)
        self.starttext = QLabel(self.tr('False Start'))
        self.starttext.setFont(self.headFont)
        self.hbox.addWidget(self.starttext)
        self.stop_live = QPushButton()
        self.stop_live.setText(self.tr('Back'))
        self.stop_live.clicked.connect(self.stop_live_click)
        self.hbox.addWidget(self.stop_live)
        self.setLayout(self.hbox)

    @pyqtSlot()
    def stop_live_click(self):
        self.parent().parent().parent().parent().showHome()


class QualifyingSeq(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.headFont = QFont()
        self.headFont.setPointSize(35)
        self.headFont.setBold(True)
        self.posFont = QFont()
        self.posFont.setPointSize(25)
        self.posFont.setBold(True)
        self.hbox = QVBoxLayout(self)
        self.starttext = QLabel(self.tr('Qualifying Driver Change'))
        self.starttext.setFont(self.headFont)
        self.hbox.addWidget(self.starttext)
        self.hbox.addWidget(HSep())
        self.lasttext = QLabel(self.tr('Last: '))
        self.lasttext.setFont(self.posFont)
        self.hbox.addWidget(self.lasttext)
        self.hbox.addWidget(HSep())
        self.nexttext = QLabel(self.tr('Next: '))
        self.nexttext.setFont(self.posFont)
        self.hbox.addWidget(self.nexttext)
        self.hbox.addWidget(HSep())
        self.hbox.addStretch(1)
        self.start_next = QPushButton()
        self.start_next.setText(self.tr('Start Next Driver'))
        self.start_next.clicked.connect(self.start_next_click)
        self.hbox.addWidget(self.start_next)
        self.setLayout(self.hbox)

    def setDrivers(self, last, next):
        self.lasttext.setText(
            self.tr('Last Driver (best laptime): ')
            + '\n' + last['name'] + ': '
            + formattime(last['qualifying_cu_driver'].bestlap, longfmt=False))
        self.nexttext.setText(self.tr('Next Driver: ') + next['name'])

    @pyqtSlot()
    def start_next_click(self):
        self.parent().parent().startQualifying(
            self.parent().parent().comp_mode,
            self.parent().parent().comp_duration)


class ResultList(QWidget):

    def __init__(self, parent=None, database=None):
        super().__init__(parent)
        self.driver_ui = {}
        self.database = database
        self.initUI()

    def initUI(self):
        self.posFont = QFont()
        self.posFont.setPointSize(30)
        self.posFont.setBold(True)
        self.headline = QLabel(self.tr('Ranking'))
        self.headline.setFont(self.posFont)
        self.vbox = QVBoxLayout()
        self.vbox.addWidget(self.headline)
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
        self.nameFont = QFont()
        self.nameFont.setPointSize(20)
        self.nameFont.setBold(True)
        self.timeFont = QFont()
        self.timeFont.setPointSize(30)
        self.timeFont.setBold(True)
        self.timeFont.setStyleHint(QFont.TypeWriter)
        self.timeFont.setFamily('monospace')
        self.posCss = "QLabel{ border-radius: 10px; border-color: black; " \
            + "border: 3px solid black; background-color: white}"
        self.nameCss = "QLabel{ border-radius: 10px; border-color: black; " \
            + "border: 3px solid black; background-color: white; " \
            + "font-size: 20pt}"
        self.lcdCss = "QLCDNumber{ border-radius: 10px; " \
            + "background-color: black}"
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
        self.final_drivers = drivers
        self.final_cu_drivers = cu_drivers
        self.final_sort_mode = sort_mode
        rank = []
        dns = []
        for addr, driver in drivers.items():
            if cu_drivers[addr].time is None:
                dns.append(cu_drivers[addr])
            else:
                rank.append(cu_drivers[addr])
        if sort_mode == SORT_MODE__LAPS:
            rank.sort(
                key=lambda dr: (0, 0) if dr.bestlap is None else (-dr.laps,
                                                                  dr.time))
        if sort_mode == SORT_MODE__LAPTIME:
            rank.sort(key=lambda dr: 0 if dr.bestlap is None else dr.bestlap)
        last_drank = '0'
        last_bl = 0
        last_tm = 0
        last_lp = 0
        for crank in rank:
            addr = crank.num
            drank = rank.index(crank) + 1
            driverPos = QLabel(str(drank))
            driverPos.setStyleSheet(self.posCss)
            driverPos.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Expanding)
            driverPos.setFont(self.posFont)
            self.mainLayout.addWidget(driverPos, self.num_row, 0)
            name = QLabel(
                '<big><b>' + str(crank.name)
                + '</b></big><br><small>' + str(drivers[addr-1]['car'])
                + '</small>')
            name.setStyleSheet(self.nameCss)
            name.setTextFormat(Qt.RichText)
            self.mainLayout.addWidget(name, self.num_row, 1)
            laps = QLabel(str(crank.laps))
            laps.setStyleSheet(self.posCss)
            laps.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Expanding)
            laps.setFont(self.timeFont)
            self.mainLayout.addWidget(laps, self.num_row, 2)
            dtime = ''
            ftime = ''
            if sort_mode == SORT_MODE__LAPS:
                ftime = formattime(crank.time)
                if drank == 1:
                    dtime = ' '
                else:
                    if rank[0].time is not None:
                        if rank[0].laps <= crank.laps:
                            dtime = '+' + formattime(crank.time - rank[0].time,
                                                     longfmt=False)
                        else:
                            dtime = self.tr('+%n Lap(s)', '',
                                            rank[0].laps - crank.laps)
            if sort_mode == SORT_MODE__LAPTIME:
                ftime = formattime(crank.bestlap, longfmt=False)
                if drank == 1:
                    dtime = ' '
                else:
                    if rank[0].bestlap is not None:
                        dtime = '+' + formattime((int(crank.bestlap) -
                                                  float(rank[0].bestlap)),
                                                 longfmt=False)
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
            if sort_mode == SORT_MODE__LAPS:
                if int(crank.laps) == int(last_lp) and \
                        int(crank.time) == int(last_tm):
                    driverPos.setText(str(last_drank))
            if sort_mode == SORT_MODE__LAPTIME:
                if int(crank.bestlap) == int(last_bl):
                    driverPos.setText(str(last_drank))
            last_drank = driverPos.text()
            last_bl = int(crank.bestlap)
            last_lp = int(crank.laps)
            last_tm = int(crank.time)
            self.driver_ui[addr] = {
                'pos': driverPos,
                'name': name,
                'laps': laps,
                'fotime': fotime,
                'otime': otime
            }
            self.num_row += 1
        for crank in dns:
            addr = crank.num
            driverPos = QLabel(self.tr('DNS'))
            driverPos.setStyleSheet(self.posCss)
            driverPos.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Expanding)
            driverPos.setFont(self.posFont)
            self.mainLayout.addWidget(driverPos, self.num_row, 0)
            name = QLabel(
                '<big><b>' + str(crank.name)
                + '</b></big><br><small>' + str(drivers[addr-1]['car'])
                + '</small>')
            name.setStyleSheet(self.nameCss)
            name.setTextFormat(Qt.RichText)
            self.mainLayout.addWidget(name, self.num_row, 1)
            self.driver_ui[addr] = {
                'pos': driverPos,
                'name': name
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
        self.update()

    @pyqtSlot()
    def back_click(self):
        mode = self.parent().parent().comp_mode
        starttime = self.parent().parent().comp_starttime
        duration = self.parent().parent().comp_duration
        comp_mode_text = self.tr('unknown')
        if mode == COMP_MODE__TRAINING:
            comp_mode_text = self.tr('Save Training?')
        elif mode in [COMP_MODE__QUALIFYING_LAPS, COMP_MODE__QUALIFYING_TIME,
                      COMP_MODE__QUALIFYING_LAPS_SEQ,
                      COMP_MODE__QUALIFYING_TIME_SEQ]:
            comp_mode_text = self.tr('Save Qualifying?')
        elif mode in [COMP_MODE__RACE_LAPS, COMP_MODE__RACE_TIME]:
            comp_mode_text = self.tr('Save Race?')
        title, ok = QInputDialog.getText(self, comp_mode_text,
                                         self.tr('Title: '),
                                         text='')
        if ok:
            self.database.saveResult(title=title,
                                     time=starttime,
                                     mode=mode,
                                     sort_mode=self.final_sort_mode,
                                     duration=duration,
                                     drivers=self.final_drivers,
                                     cu_drivers=self.final_cu_drivers)
        self.parent().parent().showHome()


class Grid(QWidget):

    def __init__(self, parent=None, tts=None, threadtranslation=None):
        super().__init__(parent)
        self.sort_mode = SORT_MODE__LAPS
        self.tts = tts
        self.threadtranslation = threadtranslation
        self.driver_ui = {}
        self.initUI()
        self.initDriverUI()

    def initUI(self):
        self.mainLayout = QGridLayout()
        self.mainLayout.setSpacing(1)
        self.mainLayout.setHorizontalSpacing(5)
        self.headerFont = QFont()
        self.headerFont.setPointSize(10)
        self.headerFont.setBold(True)
        self.labelArr = [self.tr('Pos'), self.tr('Driver'), self.tr('Total'),
                         self.tr('Laps'),
                         self.tr('Laptime'), self.tr('Best Lap')]
        self.headerLabel = self.labelArr
        for index, label in enumerate(self.labelArr):
            self.headerLabel[index] = QLabel(label)
            self.headerLabel[index].setFont(self.headerFont)
            self.mainLayout.addWidget(self.headerLabel[index], 0,
                                      index, Qt.AlignHCenter)
        self.mainLayout.setColumnStretch(1, 1)
        self.mainLayout.setColumnStretch(2, 1)
        self.mainLayout.setColumnStretch(3, 2)
        self.mainLayout.setColumnStretch(4, 3)
        self.mainLayout.setColumnStretch(5, 3)
        self.stateStack = QStackedWidget()
        self.start_signal = StartLights()
        self.false_start = FalseStart()
        self.training_state = TrainingState()
        self.qualifying_state = QualifyingState()
        self.race_state = RaceState()
        self.stateStack.addWidget(self.false_start)
        self.stateStack.addWidget(self.start_signal)
        self.stateStack.addWidget(self.training_state)
        self.stateStack.addWidget(self.qualifying_state)
        self.stateStack.addWidget(self.race_state)
        self.vml = QVBoxLayout()
        self.vml.addLayout(self.mainLayout)
        self.vml.addStretch(1)
        self.vml.addWidget(self.stateStack)
        self.setLayout(self.vml)

    def initDriverUI(self):
        self.posFont = QFont()
        self.posFont.setPointSize(30)
        self.posFont.setBold(True)
        self.nameFont = QFont()
        self.nameFont.setPointSize(20)
        self.nameFont.setBold(True)
        self.timeFont = QFont()
        self.timeFont.setPointSize(30)
        self.timeFont.setBold(True)
        self.timeFont.setStyleHint(QFont.TypeWriter)
        self.timeFont.setFamily('monospace')
        self.pitFont = QFont()
        self.pitFont.setPointSize(10)
        self.pitFont.setBold(True)
        self.pitFont.setStyleHint(QFont.TypeWriter)
        self.pitFont.setFamily('monospace')
        self.posCss = "QLabel{ border-radius: 10px; border-color: black; " \
            + "border: 3px solid black; background-color: white}"
        self.pitCss = "QLabel{ border-radius: 10px; border-color: black; " \
            + "border: 3px solid black; background-color: white; padding: 0px}"
        self.nameCss = "QLabel{ border-radius: 10px; border-color: black; " \
            + "border: 3px solid black; background-color: white; " \
            + "font-size: 18pt}"
        self.lcdCss = "QLCDNumber{ border-radius: 10px; " \
            + "background-color: black}"
        self.lcdColor = QColor(255, 0, 0)
        self.num_row = 1

    def addDriver(self, addr, driver, show_fuel, show_pits):
        driverPos = QLabel(str(driver['pos']))
        driverPos.setStyleSheet(self.posCss)
        driverPos.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Expanding)
        driverPos.setFont(self.posFont)
        self.mainLayout.addWidget(driverPos, self.num_row, 0)
        name = QLabel(
            '<big><b>' + str(driver['name'])
            + '</b></big><br><small>' + str(driver['car'])
            + '</small>')
        name.setTextFormat(Qt.RichText)
        name.setStyleSheet(self.nameCss)
        self.mainLayout.addWidget(name, self.num_row, 1)
        total = QLabel(str(formattime(0)))
        total.setStyleSheet(self.posCss)
        total.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Expanding)
        total.setFont(self.timeFont)
        self.mainLayout.addWidget(total, self.num_row, 2)
        laps = QLabel('0')
        laps.setStyleSheet(self.posCss)
        laps.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Expanding)
        laps.setFont(self.timeFont)
        self.mainLayout.addWidget(laps, self.num_row, 3)
        laptime = QLabel(str(formattime(0, longfmt=False)))
        laptime.setStyleSheet(self.posCss)
        laptime.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Expanding)
        laptime.setFont(self.timeFont)
        self.mainLayout.addWidget(laptime, self.num_row, 4)
        bestlaptime = QLabel(str(formattime(0, longfmt=False)))
        bestlaptime.setStyleSheet(self.posCss)
        bestlaptime.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Expanding)
        bestlaptime.setFont(self.timeFont)
        self.mainLayout.addWidget(bestlaptime, self.num_row, 5)
        fuelbar = QProgressBar()
        fuelbar.setOrientation(Qt.Horizontal)
        fuelbar.setStyleSheet(
            "QProgressBar{ color: white; background-color: black; border: "
            + "3px solid black; border-radius: 10px; text-align: center} "
            + "QProgressBar::chunk { background: qlineargradient(x1: 1, "
            + "y1: 0.5, x2: 0, y2: 0.5, stop: 0 #00AA00, stop: "
            + str(0.92 - (1 / (15))) + " #22FF22, stop: "
            + str(0.921 - (1 / (15))) + " #22FF22, stop: "
            + str(1.001 - (1 / (15))) + " red, stop: 1 #550000); }")
        fuelbar.setMinimum(0)
        fuelbar.setMaximum(15)
        fuelbar.setValue(15)
        fuelbar.setFont(self.pitFont)
        fuelbar.setHidden(not show_fuel)
        self.mainLayout.addWidget(fuelbar, self.num_row+1, 1, 1, 3)
        pitslbl = QLabel(self.tr('Pits:'))
        pitslbl.setFont(self.headerFont)
        pitslbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        pitslbl.setHidden(not show_pits)
        self.mainLayout.addWidget(pitslbl, self.num_row+1, 4)
        pits = QLabel('0')
        pits.setStyleSheet(self.pitCss)
        pits.setFont(self.pitFont)
        pits.setHidden(not show_pits)
        self.mainLayout.addWidget(pits, self.num_row+1, 5)
        self.driver_ui[addr] = {
            'pos': driverPos,
            'name': name,
            'total': total,
            'laps': laps,
            'laptime': laptime,
            'bestlaptime': bestlaptime,
            'fuelbar': fuelbar,
            'pits': pits,
            'pitslbl': pitslbl
        }
        self.num_row += 2

    def resetDrivers(self, show_fuel, show_pits):
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
        if self.sort_mode == SORT_MODE__LAPS:
            rank.sort(
                key=lambda dr: (0, 0) if dr.bestlap is None else (-dr.laps,
                                                                  dr.time))
        if self.sort_mode == SORT_MODE__LAPTIME:
            rank.sort(key=lambda dr: 0 if dr.bestlap is None else dr.bestlap)
        posl = []
        for i in range(0, len(rank)):
            pos = i + 1
            dposm1 = i - 1
            if dposm1 >= 0:
                if self.sort_mode == SORT_MODE__LAPS:
                    if rank[i].laps is not None and \
                            rank[dposm1].laps is not None and \
                            rank[i].laps == rank[dposm1].laps and \
                            rank[i].time is not None and \
                            rank[dposm1].time is not None and \
                            rank[i].time == rank[dposm1].time:
                        pos = posl[dposm1]
                if self.sort_mode == SORT_MODE__LAPTIME:
                    if rank[i].bestlap is not None and \
                            rank[dposm1].bestlap is not None and \
                            rank[i].bestlap == rank[dposm1].bestlap:
                        pos = posl[dposm1]
            posl.append(pos)
        for addr, driver in self.driver_ui.items():
            try:
                di = cu_drivers[addr]
                p = str(di.pits)
                if di.pit:
                    p += self.tr(' (in)')
                dpos = posl[rank.index(di)]
                self.updateDriver(
                    addr=addr,
                    pos=dpos,
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
                r['bestlaptime'].setText(str(formattime(bestlaptime,
                                                        longfmt=False)))
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
            cm = self.parent().parent().comp_mode
            if cm == COMP_MODE__TRAINING:
                self.stateStack.setCurrentWidget(self.training_state)
            elif cm == COMP_MODE__RACE_LAPS:
                self.stateStack.setCurrentWidget(self.race_state)
            elif cm == COMP_MODE__RACE_TIME:
                self.stateStack.setCurrentWidget(self.race_state)
            elif cm == COMP_MODE__QUALIFYING_LAPS:
                self.stateStack.setCurrentWidget(self.qualifying_state)
            elif cm == COMP_MODE__QUALIFYING_TIME:
                self.stateStack.setCurrentWidget(self.qualifying_state)
            elif cm == COMP_MODE__QUALIFYING_LAPS_SEQ:
                self.stateStack.setCurrentWidget(self.qualifying_state)
            elif cm == COMP_MODE__QUALIFYING_TIME_SEQ:
                self.stateStack.setCurrentWidget(self.qualifying_state)
        elif number == 101:
            self.start_signal.lightOne.setOff()
            self.start_signal.lightTwo.setOff()
            self.start_signal.lightThree.setOff()
            self.start_signal.lightFour.setOff()
            self.start_signal.lightFive.setOff()
            # self.tts.say(self.threadtranslation.ready.text())
