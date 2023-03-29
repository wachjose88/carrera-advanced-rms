import locale
from PyQt5.QtWidgets import QWidget, QGridLayout, \
                            QLabel, QVBoxLayout, \
                            QListWidgetItem, QPushButton, \
                            QListWidget, \
                            QStackedWidget, QSizePolicy, QScrollArea
from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtGui import QFont, QColor
from babel.dates import format_datetime
from constants import SORT_MODE__LAPS, SORT_MODE__LAPTIME
from constants import COMP_MODE__TRAINING, COMP_MODE__QUALIFYING_LAPS, \
                      COMP_MODE__QUALIFYING_TIME, \
                      COMP_MODE__QUALIFYING_LAPS_SEQ, \
                      COMP_MODE__QUALIFYING_TIME_SEQ, \
                      COMP_MODE__RACE_LAPS, \
                      COMP_MODE__RACE_TIME
from database import Competition, RacingPlayer
from utils import formattime


class CompetitionItem(QListWidgetItem):

    def __init__(self, competition=None):
        super().__init__(str(
            format_datetime(competition.time,
                            locale=locale.getdefaultlocale()[0])
            + ': ' + competition.title))
        self.competition = competition


class PlayerDetails(QWidget):

    def __init__(self, parent=None, database=None):
        super().__init__(parent)
        self.driver_ui = []
        self.database = database
        self.initUI()
        self.competition = None
        self.racingplayer = None
        self.num_row = 0

    def initUI(self):
        self.posFont = QFont()
        self.posFont.setPointSize(30)
        self.posFont.setBold(True)
        self.nameFont = QFont()
        self.nameFont.setPointSize(20)
        self.nameFont.setBold(True)
        self.headline = QLabel(self.tr('Ranking'))
        self.headline.setFont(self.nameFont)
        self.vbox = QVBoxLayout()
        self.vbox.addWidget(self.headline)
        self.scrollarea = QScrollArea(self)
        self.scrollarea.setWidgetResizable(True)
        self.scrollwidget = QWidget()
        self.scrollvbox = QVBoxLayout(self.scrollwidget)
        self.mainLayout = QGridLayout()
        self.scrollvbox.addLayout(self.mainLayout)
        self.scrollvbox.addStretch(1)
        self.scrollarea.setWidget(self.scrollwidget)
        self.mainLayout.setSpacing(10)
        self.mainLayout.setHorizontalSpacing(10)
        self.headerFont = QFont()
        self.headerFont.setPointSize(14)
        self.headerFont.setBold(True)
        self.labelArr = [self.tr('Lap'), self.tr('Time'),
                         self.tr('Laptime'), self.tr('Avg speed'),
                         self.tr('Fuel')]
        for index, label in enumerate(self.labelArr):
            self.headerLabel = QLabel(label)
            self.headerLabel.setFont(self.headerFont)
            self.mainLayout.addWidget(self.headerLabel, 0,
                                      index, Qt.AlignHCenter)
        self.mainLayout.setColumnStretch(1, 2)
        self.mainLayout.setColumnStretch(2, 1)
        self.mainLayout.setColumnStretch(3, 1)
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
        self.vbox.addWidget(self.scrollarea)
        #self.vbox.addStretch(1)
        self.setLayout(self.vbox)


    def buildDetails(self, competition, racingplayer):
        self.competition = competition
        self.racingplayer = racingplayer
        modet = ''
        if competition.mode == COMP_MODE__TRAINING:
            modet = self.tr('Training')
        elif competition.mode in (COMP_MODE__QUALIFYING_LAPS,
                                  COMP_MODE__QUALIFYING_TIME,
                                  COMP_MODE__QUALIFYING_LAPS_SEQ,
                                  COMP_MODE__QUALIFYING_TIME_SEQ):
            modet = self.tr('Qualifying')
        elif competition.mode in (COMP_MODE__RACE_LAPS,
                                  COMP_MODE__RACE_TIME):
            modet = self.tr('Race')
        self.headline.setText(str(
            modet + ' ' +
            format_datetime(competition.time,
                            locale=locale.getdefaultlocale()[0])
            + ': ' + competition.title + ' ' + racingplayer.player.name))
        for row in self.driver_ui:
            for name, widget in row.items():
                self.mainLayout.removeWidget(widget)
                widget.deleteLater()
                del widget
        self.driver_ui = []
        self.num_row = 1
        self.update()
        last_time = 0
        for lap in racingplayer.lap:
            lapnum = QLabel(str(self.num_row - 1))
            lapnum.setStyleSheet(self.posCss)
            lapnum.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Expanding)
            lapnum.setFont(self.posFont)
            self.mainLayout.addWidget(lapnum, self.num_row, 0)
            time = QLabel(str(formattime(lap.timestamp)))
            time.setStyleSheet(self.posCss)
            time.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Expanding)
            time.setFont(self.timeFont)
            self.mainLayout.addWidget(time, self.num_row, 1)
            laptimev = lap.timestamp - last_time
            laptime = QLabel(str(formattime(laptimev, False)))
            last_time = lap.timestamp
            laptime.setStyleSheet(self.posCss)
            laptime.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Expanding)
            laptime.setFont(self.timeFont)
            self.mainLayout.addWidget(laptime, self.num_row, 2)
            avgreal = self.database.calcAvgSpeed(laptimev)
            avgspeedtext = '<small>' + self.tr('real: ') \
                           + str(round(avgreal, 2)) + ' km/h</small>'
            if racingplayer.car.scale is not None:
                avgscaled = self.database.calcAvgSpeed(laptimev, 1.0,
                                                       racingplayer.car.scale)
                avgspeedtext += '<br><small>' + self.tr('scaled: ') \
                                + str(round(avgscaled, 2)) + ' km/h</small>'
            avgspeed = QLabel(avgspeedtext)
            avgspeed.setStyleSheet(self.nameCss)
            avgspeed.setTextFormat(Qt.RichText)
            avgspeed.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Expanding)
            self.mainLayout.addWidget(avgspeed, self.num_row, 3)
            pit = ' X'
            if lap.pit is False:
                pit = ''
            fuel = QLabel(str(round(100.0 / 15.0 * float(lap.fuel), 2)) + '%' + pit)
            fuel.setStyleSheet(self.posCss)
            fuel.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Expanding)
            fuel.setFont(self.posFont)
            self.mainLayout.addWidget(fuel, self.num_row, 4)
            self.driver_ui.append({
                'lapnum': lapnum,
                'time': time,
                'laptime': laptime,
                'fuel': fuel,
                'avgspeed': avgspeed
            })
            self.num_row += 1
        scrollmin = self.scrollarea.verticalScrollBar().minimum()
        self.scrollarea.verticalScrollBar().setValue(scrollmin)


class ShowDetails(QWidget):

    def __init__(self, parent=None, database=None):
        super().__init__(parent)
        self.driver_ui = []
        self.database = database
        self.initUI()

    def initUI(self):
        self.posFont = QFont()
        self.posFont.setPointSize(30)
        self.posFont.setBold(True)
        self.nameFont = QFont()
        self.nameFont.setPointSize(20)
        self.nameFont.setBold(True)
        self.headline = QLabel(self.tr('Ranking'))
        self.headline.setFont(self.nameFont)
        self.vbox = QVBoxLayout()
        self.vbox.addWidget(self.headline)
        self.scrollarea = QScrollArea(self)
        self.scrollarea.setWidgetResizable(True)
        self.scrollwidget = QWidget()
        self.scrollvbox = QVBoxLayout(self.scrollwidget)
        self.mainLayout = QGridLayout()
        self.scrollvbox.addLayout(self.mainLayout)
        self.scrollvbox.addStretch(1)
        self.scrollarea.setWidget(self.scrollwidget)
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
        self.vbox.addWidget(self.scrollarea)
        # self.vbox.addStretch(1)
        self.setLayout(self.vbox)

    def buildDetails(self, competition):
        modet = ''
        if competition.mode == COMP_MODE__TRAINING:
            modet = self.tr('Training')
        elif competition.mode in (COMP_MODE__QUALIFYING_LAPS,
                                  COMP_MODE__QUALIFYING_TIME,
                                  COMP_MODE__QUALIFYING_LAPS_SEQ,
                                  COMP_MODE__QUALIFYING_TIME_SEQ):
            modet = self.tr('Qualifying')
        elif competition.mode in (COMP_MODE__RACE_LAPS,
                                  COMP_MODE__RACE_TIME):
            modet = self.tr('Race')
        self.headline.setText(str(
            modet + ' ' +
            format_datetime(competition.time,
                            locale=locale.getdefaultlocale()[0])
            + ': ' + competition.title))
        for row in self.driver_ui:
            for name, widget in row.items():
                self.mainLayout.removeWidget(widget)
                widget.deleteLater()
                del widget
        self.driver_ui = []
        self.num_row = 1
        self.update()
        for p in competition.get_result():
            driverPos = QLabel(str(p['rank']))
            driverPos.setStyleSheet(self.posCss)
            driverPos.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Expanding)
            driverPos.setFont(self.posFont)
            self.mainLayout.addWidget(driverPos, self.num_row, 0)
            name = QLabel(
                '<big><b>' + str(p['player'].player.name)
                + '</b></big> <small>(' + str(p['player'].player.username)
                + ')</small><br><small>' + str(p['player'].car.name)
                + '</small>')
            name.setStyleSheet(self.nameCss)
            name.setTextFormat(Qt.RichText)
            self.mainLayout.addWidget(name, self.num_row, 1)
            laps = QLabel(str(p['laps']))
            laps.setStyleSheet(self.posCss)
            laps.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Expanding)
            laps.setFont(self.timeFont)
            self.mainLayout.addWidget(laps, self.num_row, 2)
            if competition.sortmode == SORT_MODE__LAPS:
                ftime = p['time']
            if competition.sortmode == SORT_MODE__LAPTIME:
                ftime = p['bestlap']
            fotime = QLabel(str(ftime))
            fotime.setStyleSheet(self.posCss)
            fotime.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Expanding)
            fotime.setFont(self.timeFont)
            self.mainLayout.addWidget(fotime, self.num_row, 3)
            otime = QLabel(str(p['diff']))
            otime.setStyleSheet(self.posCss)
            otime.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Expanding)
            otime.setFont(self.timeFont)
            self.mainLayout.addWidget(otime, self.num_row, 4)
            showmore = QPushButton(self.tr('>>'))
            showmore.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
            showmore.clicked.connect(
                lambda state, comp = competition, rp = p['player']: self.showMore(comp, rp))
            self.mainLayout.addWidget(showmore, self.num_row, 5)
            avgreallbl = QLabel(self.tr('average speed (real):'))
            avgreallbl.setFont(self.headerFont)
            self.mainLayout.addWidget(avgreallbl, self.num_row + 1, 1, Qt.AlignRight)
            avgrealv = 0.0
            if competition.sortmode == SORT_MODE__LAPS:
                avgrealv = self.database.calcAvgSpeed(
                    p['rawtime'],
                    len(p['player'].lap) - 1)
            if competition.sortmode == SORT_MODE__LAPTIME:
                avgrealv = self.database.calcAvgSpeed(p['rawbestlap'])
            avgreal = QLabel(str(round(avgrealv, 2)) + ' km/h')
            avgreal.setFont(self.headerFont)
            self.mainLayout.addWidget(avgreal, self.num_row + 1, 3,
                                      Qt.AlignRight)
            steps = 2
            uis = {
                'pos': driverPos,
                'name': name,
                'laps': laps,
                'fotime': fotime,
                'otime': otime,
                'showmore': showmore,
                'avgreallbl': avgreallbl,
                'avgreal': avgreal
            }
            if p['player'].car.scale is not None:
                avgscalelbl = QLabel(self.tr('average speed (scaled):'))
                avgscalelbl.setFont(self.headerFont)
                self.mainLayout.addWidget(avgscalelbl, self.num_row + 2, 1, Qt.AlignRight)
                uis['avgscalelbl'] = avgscalelbl
                avgscalev = 0.0
                if competition.sortmode == SORT_MODE__LAPS:
                    avgscalev = self.database.calcAvgSpeed(
                        p['rawtime'],
                        len(p['player'].lap) - 1,
                        p['player'].car.scale)
                if competition.sortmode == SORT_MODE__LAPTIME:
                    avgscalev = self.database.calcAvgSpeed(
                        p['rawbestlap'],
                        1.0,
                        p['player'].car.scale)
                avgscale = QLabel(str(round(avgscalev, 2)) + ' km/h')
                avgscale.setFont(self.headerFont)
                self.mainLayout.addWidget(avgscale, self.num_row + 2, 3,
                                          Qt.AlignRight)
                uis['avgscale'] = avgscale
                steps += 1
            self.driver_ui.append(uis)
            self.num_row += steps
        scrollmin = self.scrollarea.verticalScrollBar().minimum()
        self.scrollarea.verticalScrollBar().setValue(scrollmin)

    @pyqtSlot(Competition, RacingPlayer)
    def showMore(self, competition, racingplayer):
        self.parent().parent().showPlayerDetails(competition, racingplayer)


class ListAll(QWidget):

    def __init__(self, parent=None, database=None):
        super().__init__(parent)
        self.database = database
        self.grid = QGridLayout()
        self.traininglbl = QLabel(self.tr('Training'))
        self.grid.addWidget(self.traininglbl, 0, 0)
        self.qualifyinglbl = QLabel(self.tr('Qualifying'))
        self.grid.addWidget(self.qualifyinglbl, 0, 1)
        self.racelbl = QLabel(self.tr('Race'))
        self.grid.addWidget(self.racelbl, 0, 2)
        self.training = QListWidget()
        self.training.itemDoubleClicked.connect(
            self.showdetails_itemDoubleClicked)
        self.grid.addWidget(self.training, 1, 0)
        self.qualifying = QListWidget()
        self.qualifying.itemDoubleClicked.connect(
            self.showdetails_itemDoubleClicked)
        self.grid.addWidget(self.qualifying, 1, 1)
        self.race = QListWidget()
        self.race.itemDoubleClicked.connect(
            self.showdetails_itemDoubleClicked)
        self.grid.addWidget(self.race, 1, 2)
        self.setLayout(self.grid)

    def buildLists(self):
        self.training.clear()
        self.qualifying.clear()
        self.race.clear()
        i = 0
        for competition in self.database.getCompetitions(
                mode=(COMP_MODE__TRAINING, )):
            self.training.insertItem(i, CompetitionItem(competition))
            i = i + 1
        i = 0
        for competition in self.database.getCompetitions(
                mode=(COMP_MODE__QUALIFYING_LAPS,
                      COMP_MODE__QUALIFYING_TIME,
                      COMP_MODE__QUALIFYING_LAPS_SEQ,
                      COMP_MODE__QUALIFYING_TIME_SEQ)):
            self.qualifying.insertItem(i, CompetitionItem(competition))
            i = i + 1
        i = 0
        for competition in self.database.getCompetitions(
                mode=(COMP_MODE__RACE_LAPS, COMP_MODE__RACE_TIME)):
            self.race.insertItem(i, CompetitionItem(competition))
            i = i + 1

    @pyqtSlot(QListWidgetItem)
    def showdetails_itemDoubleClicked(self, item):
        self.parent().parent().showDetails(item.competition)


class Statistics(QWidget):

    def __init__(self, parent=None, database=None):
        super().__init__(parent)
        self.database = database
        self.vbox = QVBoxLayout(self)
        self.headFont = QFont()
        self.headFont.setPointSize(33)
        self.headFont.setBold(True)
        self.headline = QLabel(self.tr('Statistics'))
        self.headline.setFont(self.headFont)
        self.vbox.addWidget(self.headline)
        self.stack = QStackedWidget()
        self.listall = ListAll(parent=self, database=self.database)
        self.stack.addWidget(self.listall)
        self.showdetails = ShowDetails(parent=self, database=self.database)
        self.stack.addWidget(self.showdetails)
        self.playerdetails = PlayerDetails(parent=self, database=self.database)
        self.stack.addWidget(self.playerdetails)
        self.stack.setCurrentWidget(self.listall)
        self.vbox.addWidget(self.stack)
        self.back = QPushButton()
        self.back.setText(self.tr('Back'))
        self.back.clicked.connect(self.back_click)
        self.vbox.addWidget(self.back)
        self.setLayout(self.vbox)

    def showLists(self):
        self.listall.buildLists()
        self.stack.setCurrentWidget(self.listall)

    def showDetails(self, competition):
        self.showdetails.buildDetails(competition)
        self.stack.setCurrentWidget(self.showdetails)

    def showPlayerDetails(self, competition, racingplayer):
        self.playerdetails.buildDetails(competition, racingplayer)
        self.stack.setCurrentWidget(self.playerdetails)

    @pyqtSlot()
    def back_click(self):
        if self.stack.currentWidget() == self.showdetails:
            self.showLists()
        elif self.stack.currentWidget() == self.playerdetails:
            self.showDetails(self.playerdetails.competition)
        else:
            self.parent().parent().showHome()
