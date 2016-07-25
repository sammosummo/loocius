from os.path import abspath, dirname, exists, join as pj


pkg_path = abspath(dirname(__file__))
data_path = pj(pkg_path, 'data')
stim_path = pj(pkg_path, 'stimuli')
visual_stim_path = pj(stim_path, 'visual')
audio_stim_path = pj(stim_path, 'audio')
fonts_path = pj(pkg_path, 'fonts')
tests_path = pj(pkg_path, 'tests')
batches_path = pj(pkg_path, 'batches')
log_path = pj(pkg_path, 'logs')
bg_clr = (109, 132, 155)
txt_clr = (0, 0, 0)
correct_clr = (0, 150, 0)
incorrect_clr = (150, 0, 0)
neutral_clr = (0, 0, 255)
iti_nofeedback = 0.25
iti_feedback = 1.
countdown = 5
window_size = (800, 800)
fullscreen = False

