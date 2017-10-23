import numpy as np
from PIL import Image, ImageQt
from PyQt5.QtGui import QImage, QPixmap
from colour.models.rgb.deprecated import RGB_to_HSV, HSV_to_RGB


def load_colourised_pixmap(src, hue):
    """Returns a colourised image for use in a Qt widget.

    Args:
        src (str): Path to a stimulus. Stimuli should all be PNGs with an
            alpha channel; this function will fail otherwise.
        hue (int): Colour of the image (0-359).

    Return:
         QPixmap: A Qt object that can be placed in a QLabel and displayed in
            a widget.

    Notes:
        `PIL` documentation is misleading; it can't convert to/from HSV. We 
        therefore use the third-party package  `colour-science`. This package
        seems to have some very nice features that I might use in the future,
        so I'm making it a requirement.

    """
    orig = Image.open(src)
    rgb = np.array(orig)[..., : -1] / 255.
    a = orig.split()[-1]  # save this for later
    hsv = RGB_to_HSV(rgb)
    hue = hue / 360.  # colour-science normalises all values
    hsv[..., [0]] = hue
    rgb = HSV_to_RGB(hsv)
    new = Image.fromarray((rgb * 255).astype('uint8'), 'RGB')
    new.putalpha(a)  # reinstate transparency
    return QPixmap.fromImage(QImage(ImageQt.ImageQt(new)))  # convert for Qt


def colour_mask(shape=256, tile=32):
    """Create a randomly-coloured image to use a mask for visual stimuli.

    """
    assert shape % tile == 0, '%i not a divisor of %i' % (tile, shape)
    reps = int(shape / tile)
    rgb = np.random.random_integers(0, 255 + 1, (reps, reps, 3))
    rgb = np.repeat(rgb, tile, axis=0)
    rgb = np.repeat(rgb, tile, axis=1)
    new = Image.fromarray((rgb * 255).astype('uint8'), 'RGB')
    return QPixmap.fromImage(QImage(ImageQt.ImageQt(new)))


if __name__ == '__main__':

    colour_mask()
