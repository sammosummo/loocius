"""This is an example of a rudimentary test which implements all of the basic
functionality of loocius.

"""
from PyQt5.QtWidgets import QLabel
from loocius.tools.gui import ExpWidget


test_name = 'basic-test'
conditions = ('one', 'two', 'three')


class BasicTest(ExpWidget):

    def trial(self, trial_details):

        s = 'This is condition %s!' % trial_details['condition']
        label = QLabel

