import sys
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QPushButton, QWidget, QApplication


class Example(QWidget):

    def __init__(self):

        super().__init__()

        self.times_called = 0

        def delayed_f():

            self.times_called += 1
            print('function called %i times' % self.times_called)

        self.button = QPushButton('push me', self)
        self.button.clicked.connect(lambda: QTimer.singleShot(500, delayed_f))
        # self.move(0, 0)
        self.show()




if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())
