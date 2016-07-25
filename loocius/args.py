import argparse
import getpass
import socket


def get_parser():
    """Returns a parser object that allows an individual test or a batch of
    tests to accept arguments from the command line.
    """
    description = \
        'Loocius: A skeleton for creating psychological tests in Python.'
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        '-s', '--subject_id', default='TEST',
        help='Subject ID (if omitted, no data will be saved).'
    )
    parser.add_argument(
        '-l', '--language', choices=['EN'], default='EN',
        help='Testing language (only EN works right now).'
    )
    parser.add_argument(
        '-u', '--user_id', default=getpass.getuser(),
        help='Experimenter/user ID (if omitted, system username is used).'
    )
    parser.add_argument(
        '-b', '--batch_file', default='',
        help='Name of a batch or path to a batch file.'
    )
    parser.add_argument(
        '-j', '--proj_id', default='unnamed_proj_on_%s' % socket.gethostname(),
        help='Project ID (if omitted, system name is used).'
    )
    parser.add_argument(
        '-t', '--test_name', default='',
        help='Individual test name (ignored if -b included).'
    )
    parser.add_argument(
        '-q', '--questionnaires', default='',
        help='Names of questionnaires or name of questionnaire list.'
    )
    parser.add_argument(
        '-g', '--gui', action="store_true",
        help='Load the GUI (overrides other options).'
    )
    parser.add_argument(
        '-a', '--backup', choices=['', 'sftp'], default='',
        help="Backup method (e.g., 'sftp')"
    )
    parser.add_argument(
        '-r', '--repeat', action="store_false",
        help='Is this a repetition?'
    )
    return parser


def get_args():
    """
    Retrieve all command-line arguments.
    """
    return get_parser().parse_args()
