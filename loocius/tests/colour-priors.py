"""Pilot experiment which aims to measure subjects' 'priors' on the colours of
real-world objects. On each trial in the experiment, the subject sees two
images, which are identical apart from their colour, and a dial. The task is to
use the dial to adjust the colour of the image on the right (the test image) so
that it matches the colour of the image on the left (the sample image). There
are no correct or incorrect responses to a given trial.

The experiment estimates the subject's prior using a technique reminiscent of
the children's game 'Chinese whispers' (or 'Telephone'). On the first trial,
the colour of the sample image is chosen randomly from the colour wheel. On
the second trial, the colour of the sample image is set to the colour of the
test image that the subject chose on the first trial. On the next trial, the
colour of the sample image is set to that of the test image on the previous
trial, and so on. Using this technique, the colours of the sample images form
a Markov chain, which can be shown to converge asymptotically on the prior
distribution.

Notes:
    Currently this version defines colours using the HSL model. Note that this
    isn't the best choice because it is not perceptually relevant. This should
    be changed in a later version.

Requirements:
    colour-science: 0.3.9-py36_0: `conda install -c conda-forge colour-science`

"""
import numpy as np
from loocius.tools.paths import colourwheel_path, vis_stim_path
from loocius.tools.control import rand_control_sequence
from loocius.tools.visual import load_colourised_pixmap, colour_mask
from os import listdir
from os.path import join as pj
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import *


test_name = 'color-priors'
stim_path = pj(vis_stim_path, test_name)
exp_window_size = (256 * 3, 256)
mask_duration = 0.2
intertrial_interval = 0.2
modes = ('random', 'telephone')
stimuli = (s for s in listdir(stim_path) if '.png' in s)
durations = (0.1, 0.2, 0.3)
trials_per_condition = 100


# the experiment

class ExpWidget(QWidget):

    def __init__(self, parent=None):

        super(ExpWidget, self).__init__(parent)

        # control = self.parent().control
        #
        # if control:
        #
        #     self.control = control
        #
        # else:
        #
        #     self.control = rand_control_sequence(
        #         stimulus=stimuli, mode=modes, duration=durations,
        #         _t=range(trials_per_condition)
        #     )
        #
        # self.results = self.parent().results
        self.setup()
        self.show()

    def setup(self):

        # set up window

        self.resize(*exp_window_size)
        self.setStyleSheet("background-color:lightGray;")

        # draw colour wheel and dial

        wheel = QLabel(self)
        wheel.setPixmap(QPixmap(colourwheel_path))
        wheel.move(256 + 64, 64)
        dial = QDial(self, wrapping=True, minimum=-1, maximum=359)
        dial.setStyleSheet("color:rgba(255, 0, 0, 50%);")
        dial.setGeometry(256 + 64 + 6, 64 + 6, 128 - 13, 128 - 13)
        dial.valueChanged.connect(self.response)

        # set up areas for left and right images

        self.left = QLabel(self)
        self.right = QLabel(self)
        self.right.move(512, 0)

    def show_image(self, stimulus, position, hue):


        if position == 'left':

            image = self.left

        else:

            image = self.right

        pixmap = load_colourised_pixmap(pj(stim_path, stimulus), hue)
        image.clear()
        image.setPixmap(pixmap)
        image.update()
        image.show()

    def show_mask(self):

        pixmap = colour_mask()
        image = QLabel(self)
        image.setPixmap(pixmap)
        image.update()
        image.show()

    # def show_sample(self, stimulus, duration, hue):
    #
    #     timings = np.array([
    #         intertrial_interval, mask_duration, duration, mask_duration
    #     ]).cumsum() * 1000
    #     events = [
    #         self.show_mask, lambda: self.show_image(stimulus, 'left', hue),
    #         self.show_mask
    #     QTimer.singleShot(intertrial_interval * 1000, self.show_mask)
    #     QTimer.singleShot(intertrial_interval * 1000, self.show_mask)



    def response(self):

        value = self.sender().value()
        self.show_image('banana.png', 'right', value)


    #
    #     # dial.move(332, 78)
    #
    #
    #
    #
    #
    #
    #
    #     # self.resize(*exp_window_size)
    #     # self.setStyleSheet("background-color:lightGray;")
    #     # self.center()
    #     # self.trial(trial_details)
    #     # self.show()
    #
    # def trial(self):
    #
    #
    #
    #     hue = 200
    #     sat = 80
    #
    #     # left_pixmap = colour_mask()
    #     # left_image_label = QLabel(self)
    #     # left_image_label.setPixmap(left_pixmap)
    #
    #     wheel = QLabel(self)
    #     wheel.setPixmap(QPixmap(colourwheel_path))
    #     wheel.move(256, 64)
    #     #
    #     # rpixmap = QPixmap(stim_details['tree']['path'])
    #     # rimg = QLabel(self)
    #     # rimg.setPixmap(rpixmap)
    #     # rimg.move(256 * 2, 0)
    #
    #     # dial = QDial(self, wrapping=True, maximum=360)
    #     # dial.move(332, 78)
    #
    #
    #
    # def center(self):
    #
    #     qr = self.frameGeometry()
    #     cp = QDesktopWidget().availableGeometry().center()
    #     qr.moveCenter(cp)
    #     self.move(qr.topLeft())


def main():
    """Run the experiment.

    """
    import sys

    app = QApplication(sys.argv)
    ex = ExpWidget()
    sys.exit(app.exec_())


if __name__ == '__main__':

    main()
