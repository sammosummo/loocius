"""Data management.

"""
from loocius.tools.paths import data_path
from os.path import exists, join as pj
from datetime import datetime
from pickle import dump, load
from getpass import getuser


class Data:

    def __init__(self, subj_id, exp_name, proj_id=None):
        """Returns an instance of the `Data` object.

        `Data` objects contain all the necessary details to run a given subject
        in a given experiment and save the data. It allows any experiment to be
        resumed if prematurely aborted and prevents a subject for completing
        the same experiment twice.

        Args:
            subj_id (str): Subject's ID.
            exp_name (str): Name of the experiment.
            proj_id (:obj:`str`, optional): Project the data belongs to.
                Defaults to `None`.

        Returns:
            Data: The Data object.

        """
        # set subject ID and experiment name

        self.subj_id = subj_id
        self.exp_name = exp_name

        # set defaults

        self.timestamp = datetime.now()
        self.proj_id = proj_id
        self.user_id = getuser()
        self.exp_done = False
        self.control = None
        self.results = []
        self.relpath = '%s_%s.dic' % (self.subj_id, self.exp_name)
        self.abspath = pj(data_path, self.relpath)

        # make the dictionary that gets pickled when .save() is called

        self.dic = locals()

        # load pre-existing data, if any exist

        self.load()

    def load(self):
        """Load pre-existing data if any exist.

        """

        if exists(self.abspath):

            self.dic = load(open(self.abspath))

            # sanity checks

            assert self.subj_id == self.dic['subj_id'], 'wrong subject id'

            assert self.exp_name == self.dic['exp_name'], 'wrong experiment'

            # load important details into the namespace of this instance

            self.exp_done = self.dic['exp_done']
            self.control = self.dic['control']
            self.results = self.dic['results']

    def save(self):
        """Save the data.

        """

        dump(self.dic, open(self.abspath, 'w'))

