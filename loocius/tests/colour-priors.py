"""Experiment for measuring priors on the colours of everyday objects. On each
trial, the subject sees two monochrome images of the same real-world visual
object. The images are identical apart from their colour. Using a dial, the
subject adjusts the colour of one of the images so that it matches the other
image (the referent). On the first trial, the referent has a random colour.
On the next trial, the referent has the colour the subject chose on the first
trial. This process is repeated for a number of trials until the prior has been
effectively sampled.

Notes:
    Currently this version defines colours using the HSL model. Note that this
    isn't the best choice because it is not perceptually relevant. This should
    be changed in a later version.

Requirements:
    colour-science: 0.3.9-py36_0: `conda install -c conda-forge colour-science`

"""
import sys
import numpy as np
from colour.models.rgb.deprecated import RGB_to_HSV, HSV_to_RGB
from itertools import product
from loocius.tools.defaults import vis_stim_path
from os.path import join as pj
from PIL import Image, ImageQt
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import (
    QApplication, QDesktopWidget, QWidget, QLabel, QDial
)
from random import randint


test_name = 'color-priors'
stim_path = pj(vis_stim_path, test_name)
stim_details = {
    'banana': {'path': pj(stim_path, 'banana.png')},
    'mailbox': {'path': pj(stim_path, 'mailbox.png')},
    'tree': {'path': pj(stim_path, 'tree.png')},
    'stopsign': {'path': pj(stim_path, 'stopsign.png')},
    'cardinal': {'path': pj(stim_path, 'cardinal.png')},
    'taxi': {'path': pj(stim_path, 'taxi.png')},
    'orange': {'path': pj(stim_path, 'orange.png')},
    'sky': {'path': pj(stim_path, 'sky.png')},
}
stims = stim_details.keys()
exp_window_size = (256 * 3, 256)
wheel_path = pj(vis_stim_path, 'wheel', 'wheel.png')
modes = ('telephone', 'random')
durations = (0.1, 0.2, 0.3)
conditions = [c for c in product(stims, modes, durations)]
mask_duration = 0.1
intertrial_interval = 0.2
saturation = 75


def load_colourised_image(stim, hue, saturation):
    """Returns a colourised image.

    Args:
        stim (str): Name of the stimulus (e.g., `'banana'`).
        hue (int): Colour of the image (0-359).
        saturation (int): Saturation of the image (0-100).

    Return:
         QPixmap object

    """
    src = stim_details[stim]['path']
    orig = Image.open(src)

    # since PIL can't convert, we use colour-science

    rgb = np.array(orig)[..., : -1] / 255.
    a = orig.split()[-1]  # save this for later
    hsv = RGB_to_HSV(rgb)

    # modify hue and saturation then convert back to RGB

    hue = hue / 360.
    saturation = saturation / 100.
    # hsv[..., [0, 1]] = (hue, saturation)
    hsv[..., [0]] = hue
    rgb = HSV_to_RGB(hsv)

    # make new image

    new = Image.fromarray((rgb * 255).astype('uint8'), 'RGB')
    new.putalpha(a)  # reinstate transparency
    # new.palette = None  # workaround for possible bug

    # convert from PIL to Qt

    return QPixmap.fromImage(QImage(ImageQt.ImageQt(new)))


class ExpWindow(QWidget):
    """Window containing the stimuli and response dial.

    """

    def __init__(self, parent=None):

        super(ExpWindow, self).__init__(parent)
        self.init()

    def init(self):

        self.resize(*exp_window_size)
        self.setStyleSheet("background-color:lightGray;")
        self.center()

        hue = 200
        sat = 80

        left_pixmap = load_colourised_image('sky', hue, sat)
        left_image_label = QLabel(self)
        left_image_label.setPixmap(left_pixmap)

        wheel = QPixmap(wheel_path)
        wimg = QLabel(self)
        wimg.setPixmap(wheel)
        wimg.move(256, 0)

        rpixmap = QPixmap(stim_details['tree']['path'])
        rimg = QLabel(self)
        rimg.setPixmap(rpixmap)
        rimg.move(256 * 2, 0)

        dial = QDial(self, wrapping=True, maximum=360)
        dial.move(332, 78)

        self.show()

    def center(self):

        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


def main():
    """Run the experiment.

    """
    app = QApplication(sys.argv)
    ex = ExpWindow()
    sys.exit(app.exec_())


if __name__ == '__main__':

    main()