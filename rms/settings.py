import json
from PyQt5.QtWidgets import QWidget, QGridLayout, \
                            QLabel, QVBoxLayout, QSizePolicy, \
                            QListWidgetItem, QLineEdit, QPushButton, \
                            QInputDialog, QTabWidget, QMessageBox, QListWidget
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QFont

from home import ControllerSet
from utils import HSep


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
        self.addcar = QPushButton()
        self.addcar.setText(self.tr('Add'))
        self.addcar.clicked.connect(self.carname_finished)
        self.addcar.setSizePolicy(QSizePolicy.Maximum,
                                  QSizePolicy.Maximum)
        self.mgrid.addWidget(self.addcar, 0, 2)
        self.carlist = QListWidget()
        self.carlist.itemDoubleClicked.connect(self.carlist_itemDoubleClicked)
        i = 0
        for car in self.database.getAllCars():
            self.carlist.insertItem(i, car.name)
            i = i + 1
        self.mgrid.addWidget(self.carlist, 1, 0, 1, 3)
        self.setLayout(self.mgrid)

    @pyqtSlot(QListWidgetItem)
    def carlist_itemDoubleClicked(self, item):
        c = self.database.getCarByName(item.text())
        name, ok = QInputDialog.getText(self, self.tr('Edit Car'),
                                        self.tr('Carname: '),
                                        text=c.name)

        if ok:
            cn = str(name).strip()
            if len(cn) <= 0:
                return
            self.database.setCar(cn)
            self.parent().parent().parent().coreset.controller.buildCarList()
            self.carlist.clear()
            i = 0
            for car in self.database.getAllCars():
                self.carlist.insertItem(i, car.name)
                i = i + 1

    @pyqtSlot()
    def carname_finished(self):
        cn = str(self.carname.text()).strip()
        if len(cn) <= 0:
            return
        self.database.setCar(cn)
        self.carname.setText('')
        self.parent().parent().parent().coreset.controller.buildCarList()
        self.carlist.clear()
        i = 0
        for car in self.database.getAllCars():
            self.carlist.insertItem(i, car.name)
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
        self.error = False

    @pyqtSlot()
    def trackname_finished(self):
        tn = str(self.trackname.text()).strip()
        if len(tn) > 0:
            self.database.setConfig('TRACKNAME', tn)
            self.error = False
        else:
            self.error = True
            QMessageBox.information(
                self,
                self.tr("Missing Trackname"),
                self.tr("Please enter a trackname."),
                QMessageBox.Ok)


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
        if self.coreset.error is True:
            return
        dc = {}
        for i in range(0, 6):
            try:
                if self.coreset.controller.getOk(i) is True:
                    dc[i] = {
                        'pos': 1,
                        'name': self.coreset.controller.getName(i),
                        'car': self.coreset.controller.getCar(i)
                    }
            except KeyError:
                pass
        self.database.setConfig('DEFAULT_DRIVERS', str(json.dumps(dc)))
        self.parent().parent().setDefaultDrivers()
        self.parent().parent().showHome()
