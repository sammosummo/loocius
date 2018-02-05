"""Parse command-line arguments.

"""
import argparse


def get_parser():
    """Parse command-line arguments.

    """
    parser = argparse.ArgumentParser(
        description='Loocius: A lightweight skeleton for running '
                    'psychophysical experiments in Python.'
    )
    parser.add_argument(
        '-s', '--subj_id', default='TEST',
        help='Subject ID. WARNING: If this option is omitted, no data will be'
             'saved!'
    )
    parser.add_argument(
        '-e', '--exp_names', default='',
        help='Path of a batch file, name of an experiment, or names of '
             'multiple experiments separated by spaces.'
    )
    parser.add_argument(
        '-p', '--proj_id', default='',
        help='Name of the project the data belong to. Not necessary, but'
             'useful if a subject or experiment is involved in more than one '
             'project.'
    )
    parser.add_argument(
        '-l', '--lang', default='EN',
        help='Language in which administer the test. This will probably always'
             'be the default, EN. There must be a set of instructions '
             'available for the given language and experiment.'
    )

    return parser
