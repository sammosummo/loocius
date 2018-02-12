"""Grabs written instructions.

"""
from copy import copy
from loocius.tools.paths import instructions_path, pj, listdir


def read_instructions(exp_name, lang):
    """Grab all HTML-formatted instructions for a given experiment in the
    given language.

    """

    path = pj(instructions_path, exp_name, lang)
    html_files = [f for f in listdir(path) if '.html' in f]
    keys = [f.replace('.html', '') for f in html_files]
    paths = [pj(path, f) for f in html_files]
    text = [open(p).read().rstrip() for p in paths]
    a = {copy(k): copy(t) for k, t in zip(keys, text)}

    path = pj(instructions_path, '__general__', lang)
    html_files = [f for f in listdir(path) if '.html' in f]
    keys = [f.replace('.html', '') for f in html_files]
    keys = ['__%s__' % k for k in keys]
    paths = [pj(path, f) for f in html_files]
    text = [open(p).read().rstrip() for p in paths]
    b = {copy(k): copy(t) for k, t in zip(keys, text)}

    a.update(b)

    return a
