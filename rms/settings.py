import json
from PyQt5.QtWidgets import QWidget, QGridLayout, QSpinBox, \
                            QLabel, QVBoxLayout, QSizePolicy, \
                            QListWidgetItem, QLineEdit, QPushButton, \
                            QInputDialog, QTabWidget, QListWidget, \
                            QListWidgetItem
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QFont

from home import ControllerSet
from utils import HSep


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
