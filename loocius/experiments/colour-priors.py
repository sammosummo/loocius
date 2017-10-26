"""Color priors.

Pilot experiment which aims to measure subjects' 'priors' on the colours of
real-world objects. On each trial in the experiment, the subject sees two
images, which are identical apart from their colour, and a dial. The task is to
use the dial to adjust the colour of the image on the right (the test image) so
that it matches the colour of the image on the left (the sample image). There
are no correct or incorrect responses to a given trial.

The experiment estimates the subject's prior using a technique reminiscent of
the children's game 'Chinese whispers' (or 'Telephone'). On the first trial,
the colour of the sample image is chosen randomly from the colour wheel. On
the second trial, the colour of the sample image is set to the colour of the
test image chosen by the subject on the first trial. Trials continue in this
fashion until the prior is effectively sampled.

Priors are estimated for several different stimuli, some of which should have
strong unimodal priors (e.g., a banana) and some which shouldn't (e.g. a
balloon). The experiment also contains an additional condition per stimulus in
which the colour of the sample image is randomly selected and not updated
according to the subject's responses.

Notes:
    Currently this version defines colours using the HSL model. Note that this
    isn't the best choice because it is not perceptually relevant. This should
    be changed in a later version.

Requirements:
    colour-science: 0.3.9-py36_0: `conda install -c conda-forge colour-science`

"""
import argparse
import loocius
import os
import pickle
import sys
import pandas as pd
import numpy as np
from colour.models.rgb.deprecated import RGB_to_HSV, HSV_to_RGB
from datetime import datetime
from getpass import getuser
from itertools import product
from random import shuffle, randint
from pkgutil import iter_modules
from PIL import Image, ImageQt
from PyQt5.QtCore import pyqtSignal, QTimer, QObject
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QApplication, QDial, QLabel, QMainWindow, QStatusBar, QWidget


loocius_path = os.path.dirname(loocius.__file__)
data_path = os.path.join(loocius_path, 'data')
stim_path = os.path.join(loocius_path, 'stimuli')
vis_stim_path = os.path.join(stim_path, 'visual')


def get_parser():
    """Parse command-line arguments.

    """
    parser = argparse.ArgumentParser(
        description='Loocius: A lightweight skeleton for running '
                    'psychophysical experiments in Python.'
    )
    parser.add_argument(
        '-s', '--subj_id', default='TEST',
        help='Subject ID (if omitted, no data will be saved).'
    )
    parser.add_argument(
        '-e', '--exp_names', default='',
        help='Path of a batch file, name of an experiment, or names of '
             'multiple experiments separated by spaces.'
    )

    return parser


def is_experiment(s):
    """Checks if `s` is an existing experiment.

    """
    explist = [name for _, name, _ in iter_modules(['loocius.experiments'])]
    return s in explist


def find_experiments(s):
    """Parses `s` and returns a list of experiments to run.

    """

    if os.path.exists(s) is True:

        exp_names = [i.rstrip() for i in open(s).readlines()]

    else:

        exp_names = s.split()

    assert all(is_experiment(s) for s in
               exp_names), 'one or more invalid experiment names'

    return exp_names


def rand_control_sequence(reps, **kwargs):
    """Generate a random control sequence.

    A control sequence is a list of dictionaries where each dictionary contains
    the details required to execute a new trial.

    Args:
        reps (int): Number of repetitions per level of each condition.

    Kwargs:
        Takes any keyword arguments where the keyword is the name of the
            factor and the argument is an iterable containing all levels of the
            factor. (e.g., `condition=('one', 'two', 'three')`).

    Returns:
        list: Control sequence. Each item is a dictionary of trial details.

    """
    factors = kwargs.keys()
    levels = [[l for l in kwargs[f]] for f in factors]
    control = [{f: l for f, l in zip(factors, t)} for t in product(*levels)]
    control *= reps
    shuffle(control)

    return control


def square_mask(shape, tile):
    """Create a randomly-coloured square mask.

    Args:
        shape (int): Width/height of the mask in pxels.
        tile (int): Width/height of square tiles of solid colour.

    Returns:
        QPixmap: A QPixmap widget.

    Notes:
        Creating images takes non-zero time. To ensure accurate timing, make
            sure to send an event once successfully blitted to the screen.

    """

    assert shape % tile == 0, '%i not a divisor of %i' % (tile, shape)

    reps = int(shape / tile)
    rgb = np.random.random_integers(0, 255 + 1, (reps, reps, 3))
    rgb = np.repeat(rgb, tile, axis=0)
    rgb = np.repeat(rgb, tile, axis=1)
    new = Image.fromarray((rgb * 255).astype('uint8'), 'RGB')

    return QPixmap.fromImage(QImage(ImageQt.ImageQt(new)))


def colourise_hsv(src, hue):
    """Colourise a source image using the HSV model.

    Args:
        src (str): Path to a stimulus. Stimuli should all be PNGs.
        hue (int): Colour of the image (0-359).

    Returns:
        QPixmap: A QPixmap widget.

    Notes:
        Creating images takes non-zero time. To ensure accurate timing, make
            sure to send an event once successfully blitted to the screen.
        `PIL` documentation is misleading; it can't convert to/from HSV. We
            therefore use the third-party package  `colour-science`. This
            package seems to have some very nice features that we might use in
            the future, so it is a requirement.
        HSV is not a suitable model for psychophysical experiments. CIELAB is a
            better choice, but the function for CIELAB-based colourisation is
            likely to me much more complex and is currently not implemented.

    """
    # load the image using PIL

    orig = Image.open(src)
    data = np.array(orig)

    # is there an alpha channel?

    if data.shape[-1] == 4:

        isalpha = True
        rgb = data[..., : -1] / 255.
        alpha = orig.split()[-1]  # save this for later

    else:
        isalpha = False
        rgb = data / 255.

    # convert to HSV

    hsv = RGB_to_HSV(rgb)
    hue = hue / 360.  # colour-science normalises all values

    # change hue

    hsv[..., [0]] = hue
    rgb = HSV_to_RGB(hsv)
    new = Image.fromarray((rgb * 255).astype('uint8'), 'RGB')

    if isalpha is True:

        new.putalpha(alpha)  # reinstate transparency

    return QPixmap.fromImage(QImage(ImageQt.ImageQt(new)))  # convert for Qt


class Data:

    def __init__(self, subj_id, exp_name, proj_id=None):
        """Returns an instance of the `Data` object.

        `Data` objects contain all the necessary details to run a given subject
        in a given experiment and save the data. It allows any experiment to be
        resumed if prematurely aborted and prevents a subject for completing
        the same experiment twice.

        Args:
            subj_id (str): Subject's ID.
            exp_name (str): Name of the experiment.
            proj_id (:obj:`str`, optional): Project the data belongs to.
                Defaults to `None`.

        Returns:
            Data: The Data object.

        """
        # set subject ID and experiment name

        self.subj_id = subj_id
        self.exp_name = exp_name

        # set defaults

        self.timestamp = datetime.now()
        self.proj_id = proj_id
        self.user_id = getuser()
        self.exp_started = False
        self.exp_done = False
        self.control = None
        self.results = None
        self.relpath = '%s_%s.dic' % (self.subj_id, self.exp_name)
        self.abspath = os.path.join(data_path, self.relpath)

        # make the dictionary that gets pickled when .save() is called

        self.dic = locals()

        # load pre-existing data, if any exist

        self.load()

    def load(self):
        """Load pre-existing data if any exist.

        """

        if os.path.exists(self.abspath):

            self.dic = pickle.load(open(self.abspath))

            # sanity checks

            assert self.subj_id == self.dic['subj_id'], 'wrong subject id'

            assert self.exp_name == self.dic['exp_name'], 'wrong experiment'

            # load important details into the namespace of this instance

            self.exp_done = self.dic['exp_done']
            self.exp_started = self.dic['exp_started']
            self.control = self.dic['control']
            self.results = self.dic['results']
            self.timestamp = datetime.now()

    def save(self):
        """Save the data.

        """

        pickle.dump(self.dic, open(self.abspath, 'w'))


class MainWindow(QMainWindow):

    def __init__(self):
        """This is the very top-level instance for running an experiment or
        experiments in loocius.

        """

        super(MainWindow, self).__init__()

        # parse the command-line arguments

        self.args = get_parser().parse_args()
        self.subj_id = self.args.subj_id
        self.exp_name = None
        self.exp_names = self.args.exp_names.split()

        # TODO: programatically find names of available experiments

        self.available_exps = {
            'color-priors': ColourPriors
        }

        # set up the main window

        self.setFixedSize(768, 512)
        self.setStyleSheet("background-color:lightGray;")
        self.set_central_widget()
        # self.status_bar = QStatusBar()
        # self.setStatusBar(self.status_bar)

        # show on screen

        self.show()

    def set_central_widget(self):

        if self.exp_names:

            self.exp_name = self.exp_names.pop(0)
            widget = self.available_exps[self.exp_name]
            self.setCentralWidget(widget(self))

        else:

            self.close()


class ExpWidget(QWidget):

    def __init__(self, parent=None):
        """Base class for experiment widgets.

        """

        # set the parent (always should be an instance of MainWindow)

        super(ExpWidget, self).__init__(parent)

        # initialise data

        s_ = self.parent().subj_id
        e_ = self.parent().exp_name
        self.data_obj = Data(s_, e_)

        # set defaults

        self.vis_stim_path = os.path.join(vis_stim_path, e_)
        self.window_size = (768, 521)
        self.iti = 2

        # generate a control sequence if not found

        if not self.data_obj.control and not self.data_obj.exp_done:

            self.data_obj.control = self.gen_control()

        # run experiment-specific setup

        self.setup()

        # show on screen

        self.setMinimumSize(*self.window_size)
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

    def trial(self):
        """Override this method.

        """

        pass

    def save(self):

        self.data_obj.save()


class ColourPriors(ExpWidget):
    """Experiment widget for the colour-priors experiment.

    """

    def gen_control(self):
        """Random control sequence. Contains 100 repetitions of each stimulus,
        duration, and mode.

        """
        modes = ('random', 'telephone')
        stimuli = (s for s in os.listdir(self.vis_stim_path) if '.png' in s)
        durs = (0.1, 0.2, 0.3)

        return rand_control_sequence(100, mode=modes, stim=stimuli, dur=durs)

    def response(self, src=None):
        """Record the colour value of the dial and update the test image.

        """
        hue = self.sender().value()
        test_image = colourise_hsv(src, hue)
        self.right.setPixmap(test_image)

        return hue

    def setup(self):

        # set up the widget area

        self.window_size = (768, 256)
        self.resize_window()
        self.setStyleSheet("background-color:lightGray;")

        # draw the colour wheel

        wheel = QLabel(self)
        cwp = os.path.join(vis_stim_path, 'wheel', 'wheel.png')
        wheel.setPixmap(QPixmap(cwp))
        wheel.move(256 + 64, 64)

        # draw the dial on top of the wheel and connect it its method

        self.dial = QDial(self, wrapping=True, minimum=-1, maximum=359)
        self.dial.setStyleSheet("color:rgba(255, 0, 0, 50%);")
        self.dial.setGeometry(256 + 64 + 6, 64 + 6, 128 - 13, 128 - 13)

        # draw the left image area, put a mask in it

        self.left = QLabel(self)
        pixmap = square_mask(256, 32)
        self.left.setPixmap(pixmap)
        self.left.show()

        # draw the right image area, put a mask in it

        self.right = QLabel(self)
        self.right.move(512, 0)
        pixmap = square_mask(256, 32)
        self.right.setPixmap(pixmap)
        self.right.show()

        # begin trials

    def trial(self, trial_details):

        if trial_details['mode'] == 'random':

            hue = randint(0, 360)

        else:

            hue = [t for t in self.data_obj.results if
                   t['stim'] == trial_details['stim']][0]['rsp']

        # load visual stimuli

        src = os.path.join(vis_stim_path, trial_details['stim'])
        sample_image = colourise_hsv(self.src, hue)
        left_mask = square_mask(256, 32)
        right_mask = square_mask(256, 32)

        # reset the right side

        self.right.setPixmap(right_mask)
        self.right.show()

        # reset the left side, after flashing the sample image

        def reset_left():

            self.left.setPixmap(left_mask)
            self.left.show()

        def flash_sample_image():

            self.left.show()
            QTimer.singleShot(trial_details['dur'] * 1000, reset_left)

        self.left.setPixmap(sample_image)
        QTimer.singleShot(self.intertrial_interval * 1000, flash_sample_image)

        # connect the dial

        self.dial.valueChanged.connect(lambda: self.response(src=src))


def main():

    app = QApplication(sys.argv)
    ex = MainWindow()
    sys.exit(app.exec_())


if __name__ == '__main__':

    main()














#
# import numpy as np
# from loocius.tools.paths import colourwheel_path, vis_stim_path
# from loocius.tools.control import rand_control_sequence
# from loocius.tools.visual import load_colourised_pixmap, colour_mask
# from os import listdir
# from os.path import join as pj
# from PyQt5.QtCore import QTimer
# from PyQt5.QtGui import QPixmap
# from PyQt5.QtWidgets import *
#
#
# test_name = 'color-priors'
# stim_path = pj(vis_stim_path, test_name)
# exp_window_size = (256 * 3, 256)
# mask_duration = 0.2
# intertrial_interval = 2
# modes = ('random', 'telephone')
# stimuli = (s for s in listdir(stim_path) if '.png' in s)
# durations = (0.1, 0.2, 0.3)
# trials_per_condition = 100
#
#
# # the experiment
#
# class ExpWidget(QWidget):
#
#     def __init__(self, parent=None):
#
#         super(ExpWidget, self).__init__(parent)
#
#         control = self.parent().control
#
#         if control:
#
#             self.control = control
#
#         else:
#
#             self.control = rand_control_sequence(
#                 stimulus=stimuli, mode=modes, duration=durations,
#                 _t=range(trials_per_condition)
#             )
#
#         self.results = self.parent().results
#         self.setup()
#         self.show()
#
#     def setup(self):
#
#         # set up window
#
#         self.resize(*exp_window_size)
#         self.setStyleSheet("background-color:lightGray;")
#
#         # draw colour wheel and dial
#
#         wheel = QLabel(self)
#         wheel.setPixmap(QPixmap(colourwheel_path))
#         wheel.move(256 + 64, 64)
#         dial = QDial(self, wrapping=True, minimum=-1, maximum=359)
#         dial.setStyleSheet("color:rgba(255, 0, 0, 50%);")
#         dial.setGeometry(256 + 64 + 6, 64 + 6, 128 - 13, 128 - 13)
#         dial.valueChanged.connect(self.response)
#
#         # set up left area
#
#         self.left = QLabel(self)
#         self.show_mask('left')
#
#         self.right = QLabel(self)
#         self.right.move(512, 0)
#         self.show_mask('right')
#
#         self.show_sample('tree.png', .1, 0)
#
#     def show_image(self, stimulus, position, hue):
#
#
#         if position == 'left':
#
#             image = self.left
#
#         else:
#
#             image = self.right
#
#         pixmap = load_colourised_pixmap(pj(stim_path, stimulus), hue)
#         image.setPixmap(pixmap)
#         image.show()
#
#     def show_mask(self, position):
#
#         if position == 'left':
#
#             image = self.left
#
#         else:
#
#             image = self.right
#
#         pixmap = colour_mask()
#         image.setPixmap(pixmap)
#         image.show()
#
#     def show_sample(self, stimulus, duration, hue):
#
#         QTimer.singleShot(intertrial_interval * 1000,
#                           lambda: self.show_image(stimulus, 'left', hue))
#         QTimer.singleShot(intertrial_interval * 1000,
#                           lambda: self.show_image(stimulus, 'right', hue))
#         # timings = np.array([intertrial_interval, duration]).cumsum() * 1000
#         # events = [,
#         #           lambda: self.show_mask('left')]
#         #
#         # for t, e in zip(timings, events):
#         #
#         #     QTimer.singleShot(t, e)
#
#
#
#     def response(self):
#
#         value = self.sender().value()
#         self.show_image('banana.png', 'right', value)
#
#
#     #
#     #     # dial.move(332, 78)
#     #
#     #
#     #
#     #
#     #
#     #
#     #
#     #     # self.resize(*exp_window_size)
#     #     # self.setStyleSheet("background-color:lightGray;")
#     #     # self.center()
#     #     # self.trial(trial_details)
#     #     # self.show()
#     #
#     # def trial(self):
#     #
#     #
#     #
#     #     hue = 200
#     #     sat = 80
#     #
#     #     # left_pixmap = colour_mask()
#     #     # left_image_label = QLabel(self)
#     #     # left_image_label.setPixmap(left_pixmap)
#     #
#     #     wheel = QLabel(self)
#     #     wheel.setPixmap(QPixmap(colourwheel_path))
#     #     wheel.move(256, 64)
#     #     #
#     #     # rpixmap = QPixmap(stim_details['tree']['path'])
#     #     # rimg = QLabel(self)
#     #     # rimg.setPixmap(rpixmap)
#     #     # rimg.move(256 * 2, 0)
#     #
#     #     # dial = QDial(self, wrapping=True, maximum=360)
#     #     # dial.move(332, 78)
#     #
#     #
#     #
#     # def center(self):
#     #
#     #     qr = self.frameGeometry()
#     #     cp = QDesktopWidget().availableGeometry().center()
#     #     qr.moveCenter(cp)
#     #     self.move(qr.topLeft())
#
#
# def main():
#     """Run the experiment.
#
#     """
#     import sys
#
#     app = QApplication(sys.argv)
#     ex = ExpWidget()
#     sys.exit(app.exec_())
#
#
# if __name__ == '__main__':
#
#     main()
