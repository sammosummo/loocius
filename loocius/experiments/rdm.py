"""Random-dot motion (RDM).

This is an example experiment to demonstrate the features of loocius.

On each trial, the participant sees a random-dot kinematogram, a score number,
and a countdown timer. Participants judge whether some proportion of the dots
are moving to the left or right, using the left and right arrow keys. Trials
are completed in blocks with a fixed duration, and participants should aim to
achieve the highest score possible within a block.

This script is heavily commented to show how everything works. Future
experiments should use this script as a template.

"""
# Import everything necessary for the particular experiment here. These may be
# part of loocius already or from third-party Python packages. Generally, it is
# good practice to define as few new things here as possible. If an experiment
# requires a new function, for example, put it in an appropriate module in
# loocius.tools. If it requires new stimuli, create a new subdirectory within
# loocius.stimuli and place them there. That way, they can be used by other
# experiments in the future.

from loocius.tools.control import make_control_list
from loocius.tools.instructions import read_instructions
from loocius.tools.qt import ExpWidget


class Experiment(ExpWidget):
    """Experiment widget for the experiment, which overrides the generic
    ExpWidget class. It should always be called Experiment. This is the most
    important thing in an experiment script.

    """

    def gen_control(self):
        """Generate a control list.

        A control list dictates the details of each trial or the details of
        each block, with trial details randomly generated later. A control list
        is required for every participant and every experiment.

        Control lists and deliberately mutable: a trial/block is removed from
        the list upon completion. This, among other things, lets a participant
        resume an experiment where they left off, and lets loocius know when an
        experiment is over.

        Control lists are generated via this method only when a new participant
        first begins a new experiment. If the participant is coming back for a
        repeat session, their previous control sequence is loaded from their
        data object.

        In this example, the experiment has a two-factorial design, and each
        factor has two levels, so four conditions in total. The control
        sequence defines blocks, not trials, because the number of trials in a
        block is variable.

        In principle control lists can be generated any which way, but the
        preferred approach is to use `make_control_list`.

        """
        coherence = [.5, .25]
        ratios = [(0, 1), (1, 1)]

        return make_control_list(10, False, coherence=coherence, ratio=ratios)

    def setup(self):
        """Overrides the empty method from ExpWidget.

        This method sets everything up at the beginning of a new experimental
        session, and handles things like pre-loading the stimuli, showing the
        initial instructions, etc.

        """

        intro_message = self.instructions_dic['intro']
        _rmv = self.display_message(intro_message, self.block)

    def block(self):
        """Method for setting up a new block of trials.

        This might not be necessary for every experiment, for instance if
        conditions are not presented in blocks which need to be clearly
        delineated. Hence there is no corresponding method in the base class.

        For this experiment, each new block starts with popping an item from
        the control sequence.

        """
        trial_details = self.data_obj.control.pop(0)
        coherence, ratio = trial_details.values()
        difficulty = {.5: 'Easy', .25: 'Hard'}[coherence]
        penalty, reward = ratio
        block_num = len(self.data_obj.results) + 1
        message = self.instructions_dic['block']
        message = message.format(
            block_num=block_num, difficulty=difficulty, reward=reward,
            penalty=penalty
        )
        self.display_message(message, self.trial)

    def trial(self):
        """Initiate a new trial, saving the results of the previous trial (if
        applicable).

        """
        self.hide_message()


        # if self.current_trial_details is not None:
        #
        #     # called after the first trial, so save results
        #
        #     rt = self.trial_time.elapsed()
        #     rsp = self.dial.value()
        #     hue = self.current_trial_details['hue']
        #     err = (rsp - hue, rsp + 360 - hue)[
        #         (abs(rsp - hue), abs(rsp + 360 - hue)).index(
        #             min(abs(rsp - hue), abs(rsp + 360 - hue)))]
        #     accept = all([err < 40, 300 < rt < 5000])
        #     self.current_trial_details['rt'] = rt
        #     self.current_trial_details['rsp'] = rsp
        #     self.current_trial_details['err'] = err
        #     self.current_trial_details['accept'] = accept
        #     self.data_obj.results.append(self.current_trial_details)
        #
        #     # if not acceptable trial, add back to control sequence
        #
        #     self.data_obj.control.append(self.current_trial_details)
        #     shuffle(self.data_obj.control)
        #
        # # begin next trial
        #
        # self.current_trial_details = self.data_obj.control.pop(0)
        # stim = self.current_trial_details['stim']
        # dur = self.current_trial_details['dur']
        #
        # if self.current_trial_details['mode'] == 'random':
        #
        #     # random hue
        #
        #     hue = randint(0, 360)
        #
        # else:
        #
        #     # hue selected adaptively
        #
        #     chain = self.current_trial_details['chain']
        #     results = [
        #         t for t in self.data_obj.results if t['mode'] == 'telephone'
        #             and t['stim'] == stim and t['chain'] == chain
        #     ]
        #
        #     if len(results) > 0:
        #
        #         hue = results[-1]['hue']
        #
        #     else:
        #
        #         # no previous trial in this chain
        #
        #         hue = randint(0, 360)
        #
        # self.current_trial_details['hue'] = hue
        #
        # # load sample image
        #
        # src = pj(self.vis_stim_path, stim)
        # ix = (stim, hue)
        #
        # if ix in self.pixmaps.keys():
        #
        #     sample_pixmap = self.pixmaps[ix]
        #
        # else:
        #
        #     sample_pixmap = colourise_hsv(src, hue)
        #     self.pixmaps[(stim, hue)] = sample_pixmap
        #
        # # load masks
        #
        # left_mask_1 = square_mask(256, 32)
        # left_mask_2 = square_mask(256, 32)
        # right_mask = square_mask(256, 32)
        #
        # # reset the dial
        #
        # # reset the right side
        #
        # self.right.setPixmap(right_mask)
        #
        # # reset the left side
        #
        # self.left.setPixmap(left_mask_1)
        #
        # # show the sample image
        #
        # def flash_sample():
        #
        #     self.left.setPixmap(sample_pixmap)
        #     QTimer.singleShot(dur * 1000,
        #                       lambda: self.left.setPixmap(left_mask_2))
        #
        # QTimer.singleShot(self.iti * 1000, flash_sample)

