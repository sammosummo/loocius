"""Generic control logic for experiments.

"""
from itertools import product
from random import shuffle


def make_control_list(reps, shuffled, **kwargs):
    """Generate a control list.

    A control list is a list of dictionaries where each dictionary contains
    the details required to execute a new trial or block of trials.

    Args:
        reps (int): Number of repetitions per level of each condition.
        shuffled (bool): Should blocks be shuffled?

    Kwargs:
        Takes any keyword arguments where the keyword is the name of the
            factor and the argument is an iterable containing all levels of the
            factor. (e.g., `condition=('one', 'two', 'three')`).

    Returns:
        list: Control list. Each item is a dictionary of trial details.

    """
    factors = kwargs.keys()
    levels = [[l for l in kwargs[f]] for f in factors]
    control = [{f: l for f, l in zip(factors, t)} for t in product(*levels)]
    control *= reps

    if shuffled:

        shuffle(control)

    return control
