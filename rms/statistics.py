import locale
from PyQt5.QtWidgets import QWidget, QGridLayout, \
                            QLabel, QVBoxLayout, \
                            QListWidgetItem, QPushButton, \
                            QListWidget, \
                            QStackedWidget, QSizePolicy
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


class CompetitionItem(QListWidgetItem):

    def __init__(self, competition=None):
        super().__init__(str(
            format_datetime(competition.time,
                            locale=locale.getdefaultlocale()[0])
            + ': ' + competition.title))
        self.competition = competition


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
        for p in competition.get_result(self):
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
            self.driver_ui.append({
                'pos': driverPos,
                'name': name,
                'laps': laps,
                'fotime': fotime,
                'otime': otime
            })
            self.num_row += 1


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

    @pyqtSlot()
    def back_click(self):
        if self.stack.currentWidget() == self.showdetails:
            self.showLists()
        else:
            self.parent().parent().showHome()
