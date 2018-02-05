"""General tools for creating visual stimuli.

"""


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
    import numpy as np
    from PIL import Image, ImageQt
    from PyQt5.QtGui import QImage, QPixmap

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
    import numpy as np
    from PIL import Image, ImageQt
    from PyQt5.QtGui import QImage, QPixmap
    from colour.models.rgb.deprecated import RGB_to_HSV, HSV_to_RGB

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
