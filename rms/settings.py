import json
from PyQt5.QtWidgets import QWidget, QGridLayout, \
                            QLabel, QVBoxLayout, QSizePolicy, \
                            QCheckBox, QLineEdit, QPushButton, QHBoxLayout, \
                            QSpinBox, QTabWidget, QMessageBox, QListWidget
from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtGui import QFont

from home import ControllerSet


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
        self.carname.editingFinished.connect(self.carname_finished)
        self.carname.setSizePolicy(QSizePolicy.Expanding,
                                   QSizePolicy.Maximum)
        self.mgrid.addWidget(self.carname, 0, 1)
        self.carlist = QListWidget()
        self.carlist.currentRowChanged.connect(self.carlist_rowchanged)
        self.item2car = {}
        i = 0
        for car in self.database.getAllCars():
            self.carlist.insertItem(i, car.name)
            self.item2car[i] = car.id
            i = i + 1
        self.mgrid.addWidget(self.carlist, 1, 0, 1, 2)
        self.setLayout(self.mgrid)

    @pyqtSlot(int)
    def carlist_rowchanged(self, id):
        self.carname.setText(self.database.getCar(self.item2car[id]).name)

    @pyqtSlot()
    def carname_finished(self):
        cn = str(self.carname.text()).strip()
        self.database.setCar(cn)
        self.carlist.clear()
        self.item2car = {}
        i = 0
        for car in self.database.getAllCars():
            self.carlist.insertItem(i, car.name)
            self.item2car[i] = car.id
            i = i + 1


class CoreSet(QWidget):

    def __init__(self, parent=None, database=None):
        super().__init__(parent)
        self.database = database
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
        self.controller = ControllerSet()
        driversjson = self.database.getConfigStr('DEFAULT_DRIVERS')
        if driversjson is not None:
            driversdb = json.loads(driversjson)
            for addr, driver in driversdb.items():
                addrt = int(addr)
                self.controller.setOk(addrt, True)
                self.controller.setName(addrt, driver['name'])
        self.mgrid.addWidget(self.controller, 1, 0, 1, 2)
        self.setLayout(self.mgrid)
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
                        'name': self.coreset.controller.getName(i)
                    }
            except KeyError:
                pass
        self.database.setConfig('DEFAULT_DRIVERS', str(json.dumps(dc)))
        self.parent().parent().setDefaultDrivers()
        self.parent().parent().showHome()
