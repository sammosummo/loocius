"""General Qt elements.

"""
from os.path import join as pj
from loocius.tools.data import Data
from loocius.tools.paths import *
from loocius.tools.argparser import get_parser
from loocius.tools.instructions import read_instructions
from PyQt5.QtCore import QTime
from PyQt5.QtWidgets import *


class MainWindow(QMainWindow):

    def __init__(self):
        """This is the very top-level instance for running an experiment or
        experiments in loocius. Command-line arguments are read here.

        """

        super(MainWindow, self).__init__()

        # parse the command-line arguments

        self.args = get_parser().parse_args()
        self.subj_id = self.args.subj_id
        self.exp_names = self.args.exp_names.split()
        self.lang = self.args.lang
        self.proj_id = self.args.proj_id

        # set default values, to be overwritten by specific experiments

        self.exp_name = None
        self.width = 768
        self.height = 512

        # set up the main window

        self.setFixedSize(self.width, self.height)
        self.set_central_widget()

        # show on screen

        self.show()

    def set_central_widget(self):
        """Sets the central widget (i.e., the experiment).

        """

        if self.exp_names:

            # take an experiment from the experiment list

            self.exp_name = self.exp_names.pop(0)
            widget = import_experiment(self.exp_name)
            self.setCentralWidget(widget(self))

        else:

            # no more experiments

            self.close()

    def closeEvent(self, event):
        """Overridden method to confirm closing loocius.

        """

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

        This class does lots of heavy lifting, including:

            1. Loading experiment- and language-specific instructions
            2. Loading or creating a new Data object.
            3. Numerous generic widgets are created (e.g., message display).
            4. Numerous convenience methods are defined (e.g., clear message).

        """

        # declare parent (always MainWindow)

        super(ExpWidget, self).__init__(parent)

        # get some details from MainWindow

        s_ = self.parent().subj_id
        e_ = self.parent().exp_name
        l_ = self.parent().lang

        # get a dictionary of written instructions

        self.instructions_dic = read_instructions(e_, l_)

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

        # create an empty message screen

        self.message_area = QTextEdit(self)

        # create a generic continue button in the selected language

        m = self.instructions_dic['__continue__']
        self.cont_button = QPushButton(m, self)

        # run experiment-specific setup method

        self.setup()

        # show on screen

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

        raise Exception('Control method not overridden.')

    def setup(self):
        """Override this method.

        """

        raise Exception('Setup method not overridden.')

    def trial(self):
        """Override this method.

        """

        raise Exception('Trial method not overridden.')

    def save(self):

        self.data_obj.save()

    def display_message(self, content, func, button_message=None):
        """Displays a rich-text (HTML-formatted) message.

        Args:
            content (str): Message to display. Supports HTML text formatting.
            func (function): Method from `Experiment` to connect to the button,
                e.g., `self.trial`.
            button_message (Optional[str]): Message to display inside the
                button. Defaults to "Continue" in the selected language.

        """

        if button_message:

            self.cont_button.setText(button_message)

        self.message_area.clear()
        self.message_area.insertHtml(content)
        self.message_area.setReadOnly(True)
        self.message_area.resize(self.w, self.h)

        self.cont_button.resize(self.cont_button.sizeHint())
        x = self.w // 2 - self.cont_button.size().width() // 2
        y = self.h - self.cont_button.size().height()
        self.cont_button.move(x, y)
        self.cont_button.clicked.connect(func)
        self.cont_button.setFocus()

    def hide_message(self):
        """Hide the message and continue-button widgets.

        """
        self.message_area.hide()
        self.cont_button.hide()





