"""Coherent-motion speed-accuracy tradeoff experiment (single-script version).

On each trial, the participant sees a random dot kinematogram (RDK) and judges
whether there is coherent motion to the left or right. The number of trials in
a round is flexible, but the duration of a round is fixed at 120 s. Rounds
differ in the proportion of coherent dots, gamma, and the ratio of reward to
punishment, lambda. The idea is to determine whether participants can modify
their behavior to maximize the reward.

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
from tqdm import tqdm
from PIL import Image, ImageQt
from PyQt5.QtCore import pyqtSignal, QTime, QTimer, QObject
from PyQt5.QtGui import QImage, QPixmap, QFont
from PyQt5.QtWidgets import QApplication, QPushButton, QDial, QLabel, QMainWindow, QStatusBar, QWidget


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
        self.exp_done = False
        self.control = None
        self.results = []
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
            self.control = self.dic['control']
            self.results = self.dic['results']

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
            'colour-priors': ColourPriors
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

        # initialise data object inhereted from parent

        s_ = self.parent().subj_id
        e_ = self.parent().exp_name
        self.data_obj = Data(s_, e_)

        # set default values

        self.vis_stim_path = os.path.join(vis_stim_path, e_)
        self.window_size = (768, 521)
        self.iti = 2
        self.current_trial_details = None
        self.exp_time = QTime()
        self.trial_time = QTime()

        # generate a control sequence if not found in data object

        if not self.data_obj.control and not self.data_obj.exp_done:

            self.data_obj.control = self.gen_control()

        # run experiment-specific setup method

        self.setup()

        # show on screen

        self.setStyleSheet("background-color:lightGray;")
        self.setMinimumSize(*self.window_size)
        self.exp_time.start()
        self.trial_time.start()
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


class ColourPriors(ExpWidget):
    """Experiment widget for the colour-priors experiment.

    """

    def gen_control(self):
        """Random control sequence. Contains 100 repetitions of each stimulus,
        duration, and mode.

        """
        modes = ['random', 'telephone'][1:]
        stimuli = [s for s in os.listdir(self.vis_stim_path) if '.png' in s][1:2]
        durs = [0.1, 0.2, 0.3][:1]
        chains = range(1)
        seq = rand_control_sequence(
            100, mode=modes, stim=stimuli, dur=durs, chain=chains
        )

        return seq

    def dial_moved(self):
        """Update the test image.

        """
        hue = self.sender().value()
        stim = self.current_trial_details['stim']
        ix = (stim, hue)
        if ix in self.pixmaps.keys():

            pixmap = self.pixmaps[ix]

        else:

            src = os.path.join(self.vis_stim_path, stim)
            pixmap = colourise_hsv(src, hue)
            self.pixmaps[(stim, hue)] = pixmap

        self.right.setPixmap(pixmap)
        self.right.show()

    def setup(self):

        self.pixmaps = {}

        # draw the colour wheel

        wheel = QLabel(self)
        cwp = os.path.join(vis_stim_path, 'wheel', 'wheel.png')
        wheel.setPixmap(QPixmap(cwp))
        wheel.move(256, -16)

        # draw the dial on top of the wheel

        self.dial = QDial(self, wrapping=True, minimum=-1, maximum=359)
        self.dial.setGeometry(288, 16, 192, 192)
        self.dial.valueChanged.connect(self.dial_moved)

        # draw the left image area, put a mask in it

        self.left = QLabel(self)
        self.left.setPixmap(square_mask(256, 32))
        self.left.show()

        # draw the right image area, put a mask in it

        self.right = QLabel(self)
        self.right.move(512, 0)
        self.right.setPixmap(square_mask(256, 32))
        self.right.show()

        # draw the confirm button

        self.button = QPushButton('Continue', self)
        self.button.setFont(QFont('', 24))
        self.button.resize(256, self.button.sizeHint().height())
        self.button.move(384 - (self.button.size().width() / 2),
                         256 - self.button.size().height())
        self.button.clicked.connect(self.trial)

        # now all elements are place, resize window

        self.window_size = (768, 256)
        self.resize_window()

        # begin trials

        self.trial()

    def trial(self):
        """Initiate a new trial, saving the results of the previous trial (if
        applicable).

        """

        if self.current_trial_details is not None:

            # called after the first trial, so save results

            rt = self.trial_time.elapsed()
            rsp = self.dial.value()
            hue = self.current_trial_details['hue']
            err = (rsp - hue, rsp + 360 - hue)[
                (abs(rsp - hue), abs(rsp + 360 - hue)).index(
                    min(abs(rsp - hue), abs(rsp + 360 - hue)))]
            accept = all([err < 40, 300 < rt < 5000])
            self.current_trial_details['rt'] = rt
            self.current_trial_details['rsp'] = rsp
            self.current_trial_details['err'] = err
            self.current_trial_details['accept'] = accept
            self.data_obj.results.append(self.current_trial_details)

            # if not acceptable trial, add back to control sequence

            self.data_obj.control.append(self.current_trial_details)
            shuffle(self.data_obj.control)

        # begin next trial

        self.current_trial_details = self.data_obj.control.pop(0)
        stim = self.current_trial_details['stim']
        dur = self.current_trial_details['dur']

        if self.current_trial_details['mode'] == 'random':

            # random hue
        
            hue = randint(0, 360)

        else:

            # hue selected adaptively

            chain = self.current_trial_details['chain']
            results = [
                t for t in self.data_obj.results if t['mode'] == 'telephone' 
                    and t['stim'] == stim and t['chain'] == chain
            ]
            
            if len(results) > 0:
                
                hue = results[-1]['hue']
            
            else:
                
                # no previous trial in this chain

                hue = randint(0, 360)

        self.current_trial_details['hue'] = hue
        
        # load sample image

        src = os.path.join(self.vis_stim_path, stim)
        ix = (stim, hue)

        if ix in self.pixmaps.keys():

            sample_pixmap = self.pixmaps[ix]

        else:

            sample_pixmap = colourise_hsv(src, hue)
            self.pixmaps[(stim, hue)] = sample_pixmap

        # load masks

        left_mask_1 = square_mask(256, 32)
        left_mask_2 = square_mask(256, 32)
        right_mask = square_mask(256, 32)

        # reset the dial

        # reset the right side

        self.right.setPixmap(right_mask)

        # reset the left side

        self.left.setPixmap(left_mask_1)

        # show the sample image

        def flash_sample():

            self.left.setPixmap(sample_pixmap)
            QTimer.singleShot(dur * 1000,
                              lambda: self.left.setPixmap(left_mask_2))

        QTimer.singleShot(self.iti * 1000, flash_sample)


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
# test_name = 'colour-priors'
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
