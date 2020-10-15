import locale
from PyQt5.QtWidgets import QWidget, QGridLayout, \
                            QLabel, QVBoxLayout, \
                            QListWidgetItem, QPushButton, \
                            QListWidget, \
                            QStackedWidget
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QFont
from babel.dates import format_datetime
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
        self.grid.addWidget(self.training, 1, 0)
        self.qualifying = QListWidget()
        self.grid.addWidget(self.qualifying, 1, 1)
        self.race = QListWidget()
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

    @pyqtSlot()
    def back_click(self):
        self.parent().parent().showHome()
