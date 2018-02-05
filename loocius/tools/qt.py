"""General Qt elements.

"""
from os.path import join as pj
from loocius.tools.data import Data
from loocius.tools.paths import *
from loocius.tools.argparser import get_parser
from PyQt5.QtCore import QTime
from PyQt5.QtWidgets import QMainWindow, QWidget, QTextEdit, QMessageBox


class MainWindow(QMainWindow):

    def __init__(self):
        """This is the very top-level instance for running an experiment or
        experiments in loocius.

        """

        super(MainWindow, self).__init__()

        # parse the command-line arguments and set default values

        self.args = get_parser().parse_args()
        self.subj_id = self.args.subj_id
        self.exp_name = None
        self.exp_names = self.args.exp_names.split()
        self.lang = self.args.lang
        self.proj_id = self.args.proj_id

        self.width = 768
        self.height = 512

        # set up the main window

        self.setFixedSize(self.width, self.height)
        # self.setStyleSheet("background-color:lightGray;")
        self.set_central_widget()

        # show on screen

        self.show()

    def set_central_widget(self):

        if self.exp_names:

            self.exp_name = self.exp_names.pop(0)
            widget = import_experiment(self.exp_name)
            self.setCentralWidget(widget(self))

        else:

            self.close()

    def closeEvent(self, event):

        reply = QMessageBox.question(
            self, 'Message', "Are you sure to quit?", QMessageBox.Yes |
            QMessageBox.No, QMessageBox.No
        )

        if reply == QMessageBox.Yes:

            event.accept()
        else:

            event.ignore()


class ExpWidget(QWidget):

    def __init__(self, parent=None):
        """Base class for experiment widgets.

        """

        super(ExpWidget, self).__init__(parent)

        # get some details from parent

        s_ = self.parent().subj_id
        e_ = self.parent().exp_name
        l_ = self.parent().lang

        # get instructions in html format

        self.instructions = get_instructions(e_, l_)

        # open a data object

        self.data_obj = Data(s_, e_)

        # set default values

        self.specific_vis_stim_path = pj(vis_stim_path, e_)
        self.specific_aud_stim_path = pj(aud_stim_path, e_)
        self.w = self.parent().width
        self.h = self.parent().height
        self.window_size = (self.w, self.h)
        self.iti = 2
        self.current_trial_details = None

        # set up a timer

        self.exp_time = QTime()

        # generate a control sequence, if not found in data object

        if not self.data_obj.control and not self.data_obj.exp_done:

            self.data_obj.control = self.gen_control()

        # run experiment-specific setup method

        self.setup()

        # show on screen

        self.setStyleSheet("background-color:lightGray;")
        self.setMinimumSize(*self.window_size)
        self.exp_time.start()
        self.show()

    def resize_window(self, resize_main_window=True):
        """Resize the current widget and optionally also the main window.

        """
        self.setFixedSize(*self.window_size)

        if resize_main_window is True:

            self.parent().setFixedSize(*self.window_size)

    def gen_control(self):
        """Override this method.

        """

        pass

    def setup(self):
        """Override this method.

        """

        pass

    def next_trial(self):
        """Override this method.

        """

        pass

    def save(self):

        self.data_obj.save()

    def display_message(self, content):
        """Displays a rich-text (HTML-formatted) message `content` in the
        widget with a continue button.

        """

        s = self.instructions[content].read()
        print(type(s), s)
        message_area = QTextEdit(self)
        message_area.setStyleSheet('font-size: 18pt')
        message_area.insertHtml(s)
        message_area.resize(self.w, self.h)
        message_area.setReadOnly(True)




