"""Paths to various subdirectories.

"""
import loocius
from pkgutil import iter_modules
from os import listdir
from os.path import dirname, exists, join as pj
from importlib import import_module


loocius_path = dirname(loocius.__file__)
data_path = pj(loocius_path, 'data')
stim_path = pj(loocius_path, 'stimuli')
vis_stim_path = pj(stim_path, 'visual')
aud_stim_path = pj(stim_path, 'audio')
exp_path = pj(loocius_path, 'experiments')
exp_list = [name for _, name, _ in iter_modules([exp_path])]
instructions_path = pj(loocius_path, 'instructions')
icon_path = pj(vis_stim_path, 'icon', 'icon.png')


def is_experiment(s):
    """Returns True if `s` is an existing experiment.

    """
    return s in exp_list


def find_experiments(s):
    """Parses `s` and returns a list of experiments to run. Returns an error if
    any of the entries are not valid experiments.

    """

    if exists(s) is True:

        exp_names = [i.rstrip() for i in open(s).readlines()]

    else:

        exp_names = s.split()

    assert all(is_experiment(s) for s in
               exp_names), 'one or more invalid experiment names'

    return exp_names


def import_experiment(s):
    """Import the Experiment class from an experiment.

    """

    assert is_experiment(s), 'not an experiment'

    return import_module('loocius.experiments.' + s).Experiment
