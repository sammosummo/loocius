import sys
from os.path import join as pj

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QWidget

from loocius.tmp.tools import vis_stim_path


class Example(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.setGeometry(300, 300, 300, 220)
        self.setWindowTitle('Icon')
        icon_path = pj(vis_stim_path, 'logo', 'favicon.png')
        self.setWindowIcon(QIcon(icon_path))

        self.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())