from itertools import product
from random import shuffle


def rand_control_sequence(**kwargs):
    """This hacky function generates a randomised control sequence for any
    experiment. Supply an iterable containing all levels of a factor as a
    kwarg named after the factor. Returns a list of dictionaries whose keys
    are factors and values are levels. To use a factor but not include it
    explicitly in the control sequence, make sure the first letter of the kwarg
    name is `'_'`. For example, if you want 100 repetitions of each condition,
    use rand_control_sequence(<other conditions>, _t=range(100).


    """
    factors = kwargs.keys()
    levels = [[l for l in kwargs[f]] for f in factors]
    control = [{f: l for f, l in zip(factors, trial) if f[0] != '_'} for trial
               in product(*levels)]
    shuffle(control)
    return control


if __name__ == '__main__':

    modes = ('telephone', 'random')
    durations = (0.1, 0.2, 0.3)
    trials = range(100)
    control = rand_control_sequence(mode=modes, duration=durations, _t=trials)
    print(control)
