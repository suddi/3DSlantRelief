from json import dump

from os.path import join, isfile

from pyglet.app import run
from pyglet.gl import Config

from sys import exit

from participant import init_input
from settings import DEPTH_SIZE, EXP_NAME, FULLSCREEN, STIMULI_ONLY
from stimuli import Stimuli
from viewer import Viewer


class Controller(object):
    """
    Controls the entire experiment
    """
    def __init__(self, *args, **kwargs):
        # Hold the information pertaining to the participant here
        self.participant = {}

# ------------------------------------------------------------------
# HANDLE STIMULI CLASS
# ------------------------------------------------------------------

    def init_Stimuli(self):
        """
        Initialize the stimuli to check if the images are preprocessed,
        if they have not been, we need to process and save blurred heightmaps
        for all of the stimuli
        """
        stimuli = Stimuli()
        del stimuli

# ------------------------------------------------------------------
# HANDLE PARTICIPANT CLASS
# ------------------------------------------------------------------

    def init_Participant(self):
        """
        Create a Participant instance using init_input() from participant.py,
        collect input data for the experiment and delete the class instance
        when done
        """
        # Create a Participant instance and collect input data
        subject = init_input()

        # Store the participant information to this class
        if subject:
            self.participant['id'] = subject.subject_id
            self.participant['name'] = subject.name
            self.participant['day'] = subject.day
            self.participant['pupilsize'] = subject.pupilsize
            self.participant['practice'] = subject.practice
            self.participant['stereo'] = subject.stereo
        else:
            # If the input is not provided exit the program
            exit(1)

        # Store the directory in which to store the participant data
        self.participant['dir'] = subject.subject_dir

        # Delete the now defunct Participant object
        del subject

        # Calculate the eyeshift needed
        self.participant['eyeshift'] = [self.participant['pupilsize'] * -0.5,
                                        self.participant['pupilsize'] * 0.5]

        # Create the JSON data file using the participant information
        self.__create_json()

    def __create_json(self):
        """
        Create a JSON file with the participant information

        This is done automatically, when a new participant is added
        """
        # Get the file path for creating JSON file
        filepath = join(self.participant['dir'], 'data.json')
        # Check if file already exists
        # In which case no action needs to be taken
        if not isfile(filepath):
            # Choose the data to store into JSON file
            data = {
                    'ID': self.participant['id'],
                    'Name': self.participant['name'],
                    'Pupil Size': self.participant['pupilsize']
            }

            # Create/open the JSON file and store the data
            with open(filepath, 'wb') as f:
                dump(data, f)

# ------------------------------------------------------------------
# HANDLE VIEWER CLASS
# ------------------------------------------------------------------

    def init_Viewer(self):
        """
        Open the pyglet window and initiate OpenGL from within
        viewer.Viewer
        """
        if self.participant:
            enable_stereo = self.participant['stereo']
        else:
            enable_stereo = False

        # Setup the config
        config = Config(depth_size=DEPTH_SIZE, double_buffer=True,
                        sample_buffers=1, samples=4,
                        stereo=enable_stereo)
        # Open the window using pyglet
        self.window = Viewer(self.participant,
                             caption=EXP_NAME,
                             config=config, fullscreen=FULLSCREEN,
                             resizable=False, screen=0)

        # Run pyglet
        run()


def run_experiment():
    """
    This function will run the experiment, it created as such so that
    other files may also run the experiment through this function
    """
    # Initiate the Controller class
    # This will run the default __init__ module for object
    exp = Controller()
    if STIMULI_ONLY:
        # Initiate the pyglet window
        exp.init_Viewer()
    else:
        # Run this if heightmaps need to be rendered for the stimuli
        # Otherwise this action will do nothing
        # exp.init_Stimuli()
        # Collect information from the participant
        exp.init_Participant()
        # Initiate the pyglet window
        exp.init_Viewer()


if __name__ == '__main__':
    run_experiment()
