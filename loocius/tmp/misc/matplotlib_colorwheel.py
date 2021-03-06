import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import cm

from loocius.tmp.tools.paths import colourwheel_path

if __name__ == '__main__':

    dpi = 100
    fig = plt.figure(figsize=(2.56, 2.56), dpi=dpi)

    display_axes = fig.add_axes([0.1,0.1,0.8,0.8], projection='polar')
    display_axes._direction = 2*np.pi ## This is a nasty hack - using the hidden field to
                                      ## multiply the values such that 1 become 2*pi
                                      ## this field is supposed to take values 1 or -1 only!!

    norm = mpl.colors.Normalize(0.0, 2*np.pi)
    display_axes.set_theta_zero_location('S')

    # Plot the colorbar onto the polar axis
    # note - use orientation horizontal so that the gradient goes around
    # the wheel rather than centre out
    quant_steps = 2056
    cb = mpl.colorbar.ColorbarBase(display_axes, cmap=cm.get_cmap('hsv_r',quant_steps),
                                       norm=norm,
                                       orientation='horizontal')

    # aesthetics - get rid of border and axis labels
    cb.outline.set_visible(False)
    display_axes.set_axis_off()
    plt.savefig(colourwheel_path, transparent=True)
