from os.path import abspath, dirname, exists, join as pj


def get_default_paths():
    """Returns a dictionary containing all default paths. These should be
    overloaded by specific projects.

    """
    pkg_path = abspath(dirname(__file__))
    data_path = pj(pkg_path, 'data')
    stim_path = pj(pkg_path, 'stimuli')
    visual_stim_path = pj(stim_path, 'visual')
    audio_stim_path = pj(stim_path, 'audio')
    fonts_path = pj(pkg_path, 'fonts')
    tests_path = pj(pkg_path, 'tests')
    batches_path = pj(pkg_path, 'batches')
    paths = locals()

    assert all(exists(paths[p]) for p in paths), 'Not all paths exist.'

    return paths