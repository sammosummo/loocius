import cPickle
from datetime import datetime
from defaults import *
from os import makedirs
from os.path import exists


def save_data(data_obj):
    """Saves the raw data to the path specified within the data instance. If
    data_obj.proband_id is 'TEST', this function does nothing.

    """
    if exists(data_obj.data_directory) is False:

        makedirs(data_obj.data_directory)

    if exists(data_obj.log_directory) is False:

        makedirs(data_obj.log_directory)

    if data_obj.subj_id != 'TEST':

        with open(data_obj.data_abs_filename, 'w') as fw:

            cPickle.dump(data_obj, fw)


def load_data(subj_id, lang, user_id, proj_id, test_name,
              create_if_not_found=True):
    """Returns the pickled instance of a data class corresponding to the
    specific subject and test, if it exists. By default, a new instance is
    returned if an existing one is not found.

    """
    data_obj = Data(subj_id, lang, user_id, proj_id, test_name)

    if exists(data_obj.data_abs_filename) is False:

        with open(data_obj.data_abs_filename, 'r') as fr:

            old_data_obj = cPickle.load(fr)
            fr.close()
            old_data_obj.last_opened = datetime.now()

        return old_data_obj

    else:

        if create_if_not_found is True:

            return data_obj


class Data:
    """This class contains attributes and methods necessary for recording a
    proband's progress in a given test. There must be one such instance per
    proband and per test, pickled within the RAW_DATA_PATH. If proband_id is
    'TEST', the instance is never pickled.

    """

    def __init__(self, subj_id, lang, user_id, proj_id, test_name):

        self.subj_id = subj_id
        self.lang = lang
        self.user_id = user_id
        self.proj_id = proj_id
        self.test_name = test_name
        self.initialised = datetime.now()
        self.last_opened = datetime.now()
        self.last_updated = datetime.now()
        self.log = []
        self.log_directory = pj(log_path, self.proj_id, self.subj_id)
        self.log_filename = '%s.log' % str(self.initialised)
        self.log_abs_filename = pj(self.log_directory, self.log_filename)
        self.data_directory = pj(data_path, self.proj_id, self.subj_id)
        self.data_filename = '%s.data' % str(self.initialised)
        self.data_abs_filename = pj(self.data_directory, self.data_filename)
        self.control = None
        self.data = None
        self.test_started = False
        self.date_started = None
        self.test_done = False
        self.date_done = None
        self.to_log('created')

    def update(self, save=True, save_log=False):
        """Saves the Data instance in its current state.

        """
        self.last_updated = datetime.now()

        if self.test_done:

            self.date_done = datetime.now()

        self.to_log('updated')

        if save is True:

            save_data(self)

        if save_log is True:

            self.to_log('attempting save', True)

    def to_log(self, s, save=False):
        """Adds the string s to the log.

        """
        entry = '%s\t%s' % (str(datetime.now()), s)
        self.log.append(entry)

        if save is True:

            with open(self.log_abs_filename, 'w') as fw:

                fw.write('\n'.join(self.log))
                fw.close()
