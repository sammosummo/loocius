from PyQt5.QtWidgets import QMainWindow, QDesktopWidget


default_app_size = (768, 576)


class MainWindow(QMainWindow):

    def __init__(self, data, exp_or_exps):

        super(MainWindow, self).__init__()

        self.data = data

        if isinstance(exp_or_exps, list):

            self.exps = exp_or_exps

        else:

            self.exps = [exp_or_exps]

        self.resize(*default_app_size)
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        self.frameGeometry().moveCenter(cp)
        self.move(qr.topLeft())
        self.set_central_widget()
        self.show()

    def set_central_widget(self):

        if self.exps:

            self.exp = self.exps.pop(0)
            self.setCentralWidget(self.exp)

        else:

            self.close()
