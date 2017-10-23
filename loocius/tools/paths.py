from os.path import abspath, dirname, join as pj


pkg_path = abspath(dirname(dirname(__file__)))
stim_path = pj(pkg_path, 'stimuli')
vis_stim_path = pj(stim_path, 'visual')
audio_stim_path = pj(stim_path, 'audio')
colourwheel_path = pj(vis_stim_path, 'wheel', 'wheel.png')
