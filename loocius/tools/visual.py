import numpy as np
from PIL import Image


def shift_hue(arr, hout):
    r, g, b, a = np.rollaxis(arr, axis=-1)
    h, s, v = rgb_to_hsv(r, g, b)
    h = hout
    r, g, b = hsv_to_rgb(h, s, v)
    arr = np.dstack((r, g, b, a))
    return arr


def colorize(orig, hue):
    """Colorize an image.

    Args:
        orig (PIL image): Original image
        hue (int): Hue value between 0 and 360.
    """
    img = orig.convert('RGBA')
    orig.convert('HSV')
    arr = np.array(np.asarray(img).astype('float'))

    new = Image.fromarray(shift_hue(arr, hue/360.).astype('uint8'), 'RGBA')

    return new