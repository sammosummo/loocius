"""Contains a bunch of default values for variables.

"""
import sys
from os.path import abspath, dirname, join as pj

# paths

pkg_path = abspath(dirname(dirname(__file__)))
stim_path = pj(pkg_path, 'stimuli')
vis_stim_path = pj(stim_path, 'visual')
audio_stim_path = pj(stim_path, 'audio')
icon_path = pj(vis_stim_path, 'logo', 'favicon_256.png')

# settings

window_size = (600, 600)
eps = sys.float_info.epsilon


