"""Run the programme.

"""
from sys import argv, exit
from loocius.tools.qt import MainWindow
from loocius.tools.paths import icon_path
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication


def main():

    app = QApplication(argv)
    app.setWindowIcon(QIcon(icon_path))
    _ = MainWindow()
    exit(app.exec_())


if __name__ == '__main__':

    main()
