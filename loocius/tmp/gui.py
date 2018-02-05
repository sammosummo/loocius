from PyQt5.QtWidgets import QMainWindow, QDesktopWidget

from loocius.tmp.tools import icon_path, window_size


class MainWindow(QMainWindow):

    def __init__(self):

        super().__init__()
        self.resize(*window_size)
        self.center()
        self.init()
        self.show()

    def init(self):


        self.setWindowTitle('Color Wheel')

        dial = QDial(self, wrapping=True, maximum=360)
        vbox = QVBoxLayout()
        vbox.addWidget(dial)
        self.setStyleSheet("background-image: url(%s);" % icon_path)
        self.setLayout(vbox)

        self.show()

    def center(self):

        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())