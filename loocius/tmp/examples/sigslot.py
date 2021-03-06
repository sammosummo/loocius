import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QWidget, QLCDNumber, QSlider,
                             QVBoxLayout, QApplication, QDial)


class Example(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        lcd = QLCDNumber(self)
        sld = QSlider(Qt.Horizontal, self)
        dlr = QDial(self, wrapping=True, maximum=360)

        vbox = QVBoxLayout()
        vbox.addWidget(lcd)
        vbox.addWidget(sld)
        vbox.addWidget(dlr)

        self.setLayout(vbox)
        # sld.valueChanged.connect(lcd.display)
        dlr.valueChanged.connect(lcd.display)

        self.setGeometry(1000, 1000, 250, 150)
        self.setWindowTitle('Signal and slot')
        self.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())