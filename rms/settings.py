
from PyQt5.QtWidgets import QWidget, QGridLayout, \
                            QLabel, QVBoxLayout, QSizePolicy, \
                            QCheckBox, QLineEdit, QPushButton, QHBoxLayout, \
                            QSpinBox, QTabWidget, QMessageBox
from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtGui import QFont


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
        self.back = QPushButton()
        self.back.setText(self.tr('Back'))
        self.back.clicked.connect(self.back_click)
        self.vbox.addWidget(self.back)
        self.setLayout(self.vbox)

    @pyqtSlot()
    def back_click(self):
        if self.coreset.error is True:
            return
        self.parent().parent().showHome()
