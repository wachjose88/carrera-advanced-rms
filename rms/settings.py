import json
from urllib import request, error, parse
from PyQt5.QtWidgets import QWidget, QGridLayout, QSpinBox, \
                            QLabel, QVBoxLayout, QSizePolicy, \
                            QListWidgetItem, QLineEdit, QPushButton, \
                            QInputDialog, QTabWidget, QListWidget, \
                            QProgressBar
from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtGui import QFont

from home import ControllerSet
from statistics import ShowDetails
from utils import HSep


class PlayerItem(QListWidgetItem):

    def __init__(self, username=None, name=None):
        super().__init__(str(username + ': ' + name))
        self.username = username
        self.name = name


class PlayerSet(QWidget):

    def __init__(self, parent=None, database=None):
        super().__init__(parent)
        self.database = database
        self.mgrid = QGridLayout()
        self.usernamelbl = QLabel(self.tr('Username: '))
        self.usernamelbl.setSizePolicy(QSizePolicy.Maximum,
                                       QSizePolicy.Maximum)
        self.mgrid.addWidget(self.usernamelbl, 0, 0)
        self.username = QLineEdit()
        self.username.setSizePolicy(QSizePolicy.Expanding,
                                    QSizePolicy.Maximum)
        self.mgrid.addWidget(self.username, 0, 1)
        self.playernamelbl = QLabel(self.tr('Name: '))
        self.playernamelbl.setSizePolicy(QSizePolicy.Maximum,
                                         QSizePolicy.Maximum)
        self.mgrid.addWidget(self.playernamelbl, 1, 0)
        self.playername = QLineEdit()
        self.playername.setSizePolicy(QSizePolicy.Expanding,
                                      QSizePolicy.Maximum)
        self.mgrid.addWidget(self.playername, 1, 1)
        self.addplayer = QPushButton()
        self.addplayer.setText(self.tr('Add'))
        self.addplayer.clicked.connect(self.playername_finished)
        self.addplayer.setSizePolicy(QSizePolicy.Maximum,
                                     QSizePolicy.Expanding)
        self.mgrid.addWidget(self.addplayer, 0, 2, 2, 1)
        self.playerlist = QListWidget()
        self.playerlist.itemDoubleClicked.connect(
            self.playerlist_itemDoubleClicked)
        i = 0
        for player in self.database.getAllPlayers():
            self.playerlist.insertItem(i, PlayerItem(player.username,
                                                     player.name))
            i = i + 1
        self.mgrid.addWidget(self.playerlist, 2, 0, 1, 3)
        self.setLayout(self.mgrid)

    @pyqtSlot()
    def playername_finished(self):
        pn = str(self.playername.text()).strip()
        if len(pn) <= 0:
            return
        pun = str(self.username.text()).strip()
        if len(pun) <= 0:
            return
        self.database.setPlayer(pun, pun, pn)
        self.username.setText('')
        self.playername.setText('')
        self.parent().parent().parent().coreset.controller.buildPlayerList()
        self.playerlist.clear()
        i = 0
        for player in self.database.getAllPlayers():
            self.playerlist.insertItem(i, PlayerItem(player.username,
                                                     player.name))
            i = i + 1

    @pyqtSlot(QListWidgetItem)
    def playerlist_itemDoubleClicked(self, item):
        p = self.database.getPlayer(item.username)
        username, ok = QInputDialog.getText(self, self.tr('Edit Player'),
                                            self.tr('Username: '),
                                            text=p.username)
        name, okn = QInputDialog.getText(self, self.tr('Edit Player'),
                                         self.tr('Name: '),
                                         text=p.name)

        if ok and okn:
            pu = str(username).strip()
            if len(pu) <= 0:
                return
            pn = str(name).strip()
            if len(pn) <= 0:
                return
            self.database.setPlayer(p.username, pu, pn)
            self.parent().parent().parent().coreset.controller.buildPlayerList()
            self.playerlist.clear()
            i = 0
            for player in self.database.getAllPlayers():
                self.playerlist.insertItem(i, PlayerItem(player.username,
                                                         player.name))
                i = i + 1


class CarItem(QListWidgetItem):

    def __init__(self, name=None, number=None):
        super().__init__(str(name + ' (' + number + ')'))
        self.name = name
        self.number = number


class CarSet(QWidget):

    def __init__(self, parent=None, database=None):
        super().__init__(parent)
        self.database = database
        self.mgrid = QGridLayout()
        self.carnamelbl = QLabel(self.tr('Carname: '))
        self.carnamelbl.setSizePolicy(QSizePolicy.Maximum,
                                      QSizePolicy.Maximum)
        self.mgrid.addWidget(self.carnamelbl, 0, 0)
        self.carname = QLineEdit()
        self.carname.setSizePolicy(QSizePolicy.Expanding,
                                   QSizePolicy.Maximum)
        self.mgrid.addWidget(self.carname, 0, 1)
        self.carnumberlbl = QLabel(self.tr('Carnumber: '))
        self.carnumberlbl.setSizePolicy(QSizePolicy.Maximum,
                                        QSizePolicy.Maximum)
        self.mgrid.addWidget(self.carnumberlbl, 1, 0)
        self.carnumber = QLineEdit()
        self.carnumber.setSizePolicy(QSizePolicy.Expanding,
                                     QSizePolicy.Maximum)
        self.mgrid.addWidget(self.carnumber, 1, 1)
        self.addcar = QPushButton()
        self.addcar.setText(self.tr('Add'))
        self.addcar.clicked.connect(self.carname_finished)
        self.addcar.setSizePolicy(QSizePolicy.Maximum,
                                  QSizePolicy.Expanding)
        self.mgrid.addWidget(self.addcar, 0, 2, 2, 1)
        self.carlist = QListWidget()
        self.carlist.itemDoubleClicked.connect(self.carlist_itemDoubleClicked)
        i = 0
        for car in self.database.getAllCars():
            self.carlist.insertItem(i, CarItem(car.name, car.number))
            i = i + 1
        self.mgrid.addWidget(self.carlist, 2, 0, 1, 3)
        self.setLayout(self.mgrid)

    @pyqtSlot(QListWidgetItem)
    def carlist_itemDoubleClicked(self, item):
        c = self.database.getCarByName(item.name)
        name, ok = QInputDialog.getText(self, self.tr('Edit Car'),
                                        self.tr('Carname: '),
                                        text=c.name)
        number, okn = QInputDialog.getText(self, self.tr('Edit Car'),
                                           self.tr('Carnumber: '),
                                           text=c.number)

        if ok and okn:
            cn = str(name).strip()
            if len(cn) <= 0:
                return
            cnr = str(number).strip()
            if len(cnr) <= 0:
                return
            self.database.setCar(c.name, cn, cnr)
            self.parent().parent().parent().coreset.controller.buildCarList()
            self.carlist.clear()
            i = 0
            for car in self.database.getAllCars():
                self.carlist.insertItem(i, CarItem(car.name, car.number))
                i = i + 1

    @pyqtSlot()
    def carname_finished(self):
        cn = str(self.carname.text()).strip()
        if len(cn) <= 0:
            return
        cnr = str(self.carnumber.text()).strip()
        if len(cnr) <= 0:
            return
        self.database.setCar(cn, cn, cnr)
        self.carname.setText('')
        self.carnumber.setText('')
        self.parent().parent().parent().coreset.controller.buildCarList()
        self.carlist.clear()
        i = 0
        for car in self.database.getAllCars():
            self.carlist.insertItem(i, CarItem(car.name, car.number))
            i = i + 1


class CoreSet(QWidget):

    def __init__(self, parent=None, database=None):
        super().__init__(parent)
        self.database = database
        self.vml = QVBoxLayout()
        self.mgrid = QGridLayout()
        self.tracknamelbl = QLabel(self.tr('Trackname: '))
        self.tracknamelbl.setSizePolicy(QSizePolicy.Maximum,
                                        QSizePolicy.Maximum)
        self.mgrid.addWidget(self.tracknamelbl, 0, 0)
        self.trackname = QLineEdit()
        tn = self.database.getConfigStr('TRACKNAME')
        if tn is not None:
            self.trackname.setText(tn)
        self.trackname.editingFinished.connect(self.trackname_finished)
        self.trackname.setSizePolicy(QSizePolicy.Expanding,
                                     QSizePolicy.Maximum)
        self.mgrid.addWidget(self.trackname, 0, 1)
        self.tracklengthlbl = QLabel(self.tr('Tracklength: '))
        self.tracklengthlbl.setSizePolicy(QSizePolicy.Maximum,
                                          QSizePolicy.Maximum)
        self.mgrid.addWidget(self.tracklengthlbl, 1, 0)
        self.tracklength = QSpinBox()
        self.tracklength.setMinimum(1)
        self.tracklength.setMaximum(2147483647)
        self.tracklength.setSuffix(self.tr(' mm'))
        self.tracklength.setValue(20000)
        tl = self.database.getConfigStr('TRACKLENGTH')
        if tl is not None:
            self.tracklength.setValue(int(tl))
        self.tracklength.editingFinished.connect(self.tracklength_finished)
        self.tracklength.setSizePolicy(QSizePolicy.Expanding,
                                       QSizePolicy.Maximum)
        self.mgrid.addWidget(self.tracklength, 1, 1)
        self.vml.addLayout(self.mgrid)
        self.vml.addWidget(HSep())
        self.dcs = QLabel(self.tr('Default Controller Settings:'))
        self.vml.addWidget(self.dcs)
        self.controller = ControllerSet(self, self.database)
        driversjson = self.database.getConfigStr('DEFAULT_DRIVERS')
        if driversjson is not None:
            driversdb = json.loads(driversjson)
            for addr, driver in driversdb.items():
                addrt = int(addr)
                self.controller.setOk(addrt, True)
                self.controller.setName(addrt, driver['name'])
                self.controller.setCar(addrt, driver['car'])
        self.vml.addWidget(self.controller)
        self.vml.addWidget(HSep())
        self.vml.addStretch(1)
        self.setLayout(self.vml)

    @pyqtSlot()
    def tracklength_finished(self):
        tl = str(self.tracklength.value()).strip()
        self.database.setConfig('TRACKLENGTH', tl)

    @pyqtSlot()
    def trackname_finished(self):
        tn = str(self.trackname.text()).strip()
        self.database.setConfig('TRACKNAME', tn)


class SyncSet(QWidget):

    def __init__(self, parent=None, database=None):
        super().__init__(parent)
        self.database = database
        self.vml = QVBoxLayout()
        self.mgrid = QGridLayout()
        self.apiurllbl = QLabel(self.tr('URL: '))
        self.apiurllbl.setSizePolicy(QSizePolicy.Maximum,
                                     QSizePolicy.Maximum)
        self.mgrid.addWidget(self.apiurllbl, 0, 0)
        self.apiurl = QLineEdit()
        apiurl = self.database.getConfigStr('APIURL')
        if apiurl is not None:
            self.apiurl.setText(apiurl)
        self.apiurl.editingFinished.connect(self.apiurl_finished)
        self.apiurl.setSizePolicy(QSizePolicy.Expanding,
                                  QSizePolicy.Maximum)
        self.mgrid.addWidget(self.apiurl, 0, 1)
        self.apiuserlbl = QLabel(self.tr('Username: '))
        self.apiuserlbl.setSizePolicy(QSizePolicy.Maximum,
                                      QSizePolicy.Maximum)
        self.mgrid.addWidget(self.apiuserlbl, 1, 0)
        self.apiuser = QLineEdit()
        apiuser = self.database.getConfigStr('APIUSER')
        if apiuser is not None:
            self.apiuser.setText(apiuser)
        self.apiuser.editingFinished.connect(self.apiuser_finished)
        self.apiuser.setSizePolicy(QSizePolicy.Expanding,
                                   QSizePolicy.Maximum)
        self.mgrid.addWidget(self.apiuser, 1, 1)
        self.apipwlbl = QLabel(self.tr('Password: '))
        self.apipwlbl.setSizePolicy(QSizePolicy.Maximum,
                                    QSizePolicy.Maximum)
        self.mgrid.addWidget(self.apipwlbl, 2, 0)
        self.apipw = QLineEdit()
        apipw = self.database.getConfigStr('APIPW')
        if apiurl is not None:
            self.apipw.setText(apipw)
        self.apipw.editingFinished.connect(self.apipw_finished)
        self.apipw.setSizePolicy(QSizePolicy.Expanding,
                                 QSizePolicy.Maximum)
        self.mgrid.addWidget(self.apipw, 2, 1)
        self.vml.addLayout(self.mgrid)
        self.vml.addWidget(HSep())
        self.syncprogress = QProgressBar()
        self.syncprogress.setOrientation(Qt.Horizontal)
        self.syncprogress.setMinimum(0)
        self.syncprogress.setMaximum(100)
        self.syncprogress.setValue(0)
        self.vml.addWidget(self.syncprogress)
        self.sync = QPushButton()
        self.sync.setText(self.tr('Synchronize'))
        self.sync.clicked.connect(self.sync_click)
        self.vml.addWidget(self.sync)
        self.vml.addStretch(1)
        self.setLayout(self.vml)

    @pyqtSlot()
    def sync_click(self):
        self.syncprogress.setValue(0)
        apiurl = self.database.getConfigStr('APIURL')
        if apiurl is None:
            return
        apiuser = self.database.getConfigStr('APIUSER')
        if apiuser is None:
            return
        apipw = self.database.getConfigStr('APIPW')
        if apipw is None:
            return
        try:
            auth_handler = request.HTTPBasicAuthHandler()
            auth_handler.add_password(realm='Carrera RMS Statistics',
                                      uri=apiurl + 'upload',
                                      user=apiuser,
                                      passwd=apipw)
            opener = request.build_opener(auth_handler)
            cars = self.database.getCarsForSync()
            self.syncprogress.setValue(10)
            if cars is not None and len(cars) > 0:
                params = {
                    'cars': str(json.dumps(cars))
                }
                data = parse.urlencode(params)
                data = data.encode('ascii')
                response = opener.open(apiurl + 'upload', data)
                response_data = response.read().decode('utf-8')
                print(response_data)
                carsr = json.loads(response_data)
                self.database.setCarsSync(carsr['cars'])
                self.syncprogress.setValue(15)
            players = self.database.getPlayersForSync()
            # print(players)
            self.syncprogress.setValue(20)
            if players is not None and len(players) > 0:
                params = {
                    'players': str(json.dumps(players))
                }
                data = parse.urlencode(params)
                data = data.encode('ascii')
                response = opener.open(apiurl + 'upload', data)
                response_data = response.read().decode('utf-8')
                playersr = json.loads(response_data)
                self.database.setPlayersSync(playersr['players'])
                self.syncprogress.setValue(25)
            racingplayers = self.database.getRacingPlayersForSync()
            # print(racingplayers)
            if racingplayers is not None and len(racingplayers) > 0:
                params = {
                    'racingplayers': str(json.dumps(racingplayers))
                }
                data = parse.urlencode(params)
                data = data.encode('ascii')
                response = opener.open(apiurl + 'upload', data)
                response_data = response.read().decode('utf-8')
                racingplayersr = json.loads(response_data)
                self.database.setRacingPlayersSync(racingplayersr['racingplayers'])
                self.syncprogress.setValue(30)
            laps = self.database.getLapsForSync()
            # print(laps)
            if laps is not None and len(laps) > 0:
                params = {
                    'laps': str(json.dumps(laps))
                }
                data = parse.urlencode(params)
                data = data.encode('ascii')
                response = opener.open(apiurl + 'upload', data)
                response_data = response.read().decode('utf-8')
                lapsr = json.loads(response_data)
                self.database.setLapsSync(lapsr['laps'])
                self.syncprogress.setValue(35)
            competitions = self.database.getCompetitionsForSync(ShowDetails())
            print(competitions)
            if competitions is not None and len(competitions) > 0:
                params = {
                    'competitions': str(json.dumps(competitions))
                }
                data = parse.urlencode(params)
                data = data.encode('ascii')
                response = opener.open(apiurl + 'upload', data)
                response_data = response.read().decode('utf-8')
                competitionsr = json.loads(response_data)
                self.database.setCompetitionsSync(competitionsr['competitions'])
                self.syncprogress.setValue(95)
        except error.HTTPError as e:
            print(e)
        self.syncprogress.setValue(100)

    @pyqtSlot()
    def apiurl_finished(self):
        apiurl = str(self.apiurl.text()).strip()
        self.database.setConfig('APIURL', apiurl)

    @pyqtSlot()
    def apiuser_finished(self):
        apiuser = str(self.apiuser.text()).strip()
        self.database.setConfig('APIUSER', apiuser)

    @pyqtSlot()
    def apipw_finished(self):
        apipw = str(self.apipw.text()).strip()
        self.database.setConfig('APIPW', apipw)


class Settings(QWidget):

    def __init__(self, parent=None, database=None):
        super().__init__(parent)
        self.database = database
        self.vbox = QVBoxLayout(self)
        self.headFont = QFont()
        self.headFont.setPointSize(33)
        self.headFont.setBold(True)
        self.headline = QLabel(self.tr('Settings'))
        self.headline.setFont(self.headFont)
        self.vbox.addWidget(self.headline)
        self.settab = QTabWidget()
        self.vbox.addWidget(self.settab)
        self.coreset = CoreSet(database=self.database)
        self.settab.addTab(self.coreset, self.tr('Core'))
        self.carset = CarSet(database=self.database)
        self.settab.addTab(self.carset, self.tr('Cars'))
        self.playerset = PlayerSet(database=self.database)
        self.settab.addTab(self.playerset, self.tr('Drivers'))
        self.syncset = SyncSet(database=self.database)
        self.settab.addTab(self.syncset, self.tr('Sync'))
        self.back = QPushButton()
        self.back.setText(self.tr('Back'))
        self.back.clicked.connect(self.back_click)
        self.vbox.addWidget(self.back)
        self.setLayout(self.vbox)

    @pyqtSlot()
    def back_click(self):
        dc = {}
        try:
            for i in range(0, 6):
                if self.coreset.controller.getOk(i) is True:
                    dc[i] = {
                        'pos': 1,
                        'name': self.coreset.controller.getName(i),
                        'car': self.coreset.controller.getCar(i)
                    }
            self.database.setConfig('DEFAULT_DRIVERS', str(json.dumps(dc)))
            self.parent().parent().setDefaultDrivers()
            self.parent().parent().showHome()
        except KeyError:
            pass
