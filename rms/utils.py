import locale

from PyQt5.QtWidgets import QWidget,  QHBoxLayout, QFrame, QLabel


class ThreadTranslation(QWidget):
    def __init__(self):
        super().__init__()
        self.hbox = QHBoxLayout()
        self.letsgo = QLabel(self.tr("let's go!"))
        self.hbox.addWidget(self.letsgo)
        self.box = QLabel(self.tr("box box box!"))
        self.hbox.addWidget(self.box)
        self.finished = QLabel(self.tr("finished!"))
        self.hbox.addWidget(self.finished)
        self.setLayout(self.hbox)


class HSep(QFrame):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.HLine)
        self.setLineWidth(1)


class VSep(QFrame):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.VLine)
        self.setLineWidth(1)


def formattime(time, longfmt=True):
    if time is None:
        return 'n/a'
    s = int(time // 1000)
    ms = int(time % 1000)

    if not longfmt:
        sms = float(str(s)+'.'+str('%03d' % (ms)))
        return locale.format_string('%.3f', sms)
    elif s < 3600:
        sms = float(str(s % 60) + '.' + str('%03d' % (ms)))
        t = '%d:' % (s // 60)
        return t + locale.format_string('%06.3f', sms)
    else:
        sms = float(str(s % 60) + '.' + str('%03d' % (ms)))
        t = '%d:%02d:' % (s // 3600, (s // 60) % 60)
        return t + locale.format_string('%06.3f', sms)
