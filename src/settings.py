from os import listdir, makedirs
from os.path import exists

from sys import exit


# ------------------------------------------------------------------
# FUNCTIONS USED IN THE SETTINGS
# ------------------------------------------------------------------

def get_images(directory):
    """
    Get all the images of a certain type from a directory
    """
    images = []
    # For all files in the directory
    for files in listdir(directory):
        # If the filename ends with img_type, it is our required images
        if files.endswith('.jpg') or files.endswith('.png'):
            # Join it to the list of stimuli images
            images.append(directory + files)
    return images


def report_error(message):
    """
    Report a message and exit the application
    """
    print message
    exit(1)

# ------------------------------------------------------------------
# GENERAL EXPERIMENT SETTINGS
# ------------------------------------------------------------------
# Set experiment name
EXP_NAME = '3D_SLANT_RELIEF'

# Stimuli images directory
img_dir = '../img/stimuli'
COLORMAPS = get_images(img_dir + '/colormaps')
HEIGHTMAPS = get_images(img_dir + '/heightmaps')
NORMALMAPS = get_images(img_dir + '/normalmaps')

# If the number of stimuli images of each type are not equal
# We report an error
# if not len(COLORMAPS) == len(HEIGHTMAPS) == len(NORMALMAPS):
    # report_error('ERROR: Number of stimuli images of each type must be the same')

# Messages directory
msg_dir = '../img/msg'
# Store all the message images here
IMG_MSG = get_images(msg_dir)

# Filename of fixation point
IMG_FIX = '../img/fix.jpg'

# Directory in which to store data
DATA_DIR = '../data'
if not exists(DATA_DIR):
    makedirs(DATA_DIR)

STIMULI_ONLY = False
# Use this if loading the Vertex Buffer Object from a file
# VBO_FILE = 'coordinates.py'

# Viewing distance from monitor
VIEW_DIST = 100.0

# Duration of time that the fixation point should be displayed
FIX_DUR = 0.5
# Interval between breaks in seconds
BREAK_INTERVAL = 300
# Duration of the break in seconds
BREAK_DURATION = 10

# Number of sessions
TOTAL_SESSIONS = 2
# Number of stimuli presented in practice block
PRACTICE_STIMULI = 10
# Number of times to repeat the conditions of the stimuli
# The variants are:
#     1. Number of stimuli images, provided by COLORMAPS, HEIGHTMAPS
#        and NORMALMAPS.
#     2. Possible slants, set by the variable POSSIBLE_SLANTS
#     3. Ratio to which the displacement mapping is scaled to in the
#        Z-axis, set by the variable HEIGHT_RATIO
#
# The resulting number of stimuli is calculated by the following equation:
# EXP_STIMULI = len(COLORMAPS) * len(POSSIBLE_SLANTS) * len(HEIGHT_RATIO) * STIMULI_REPETITION
STIMULI_REPETITION = 1
# Set the slants made available to experiment
# POSSIBLE_SLANTS = [5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60]
# Comment this out for the real experiment
POSSIBLE_SLANTS = [60]

SCREEN_WIDTH = 59.5
SCREEN_HEIGHT = 33.8

# ------------------------------------------------------------------
# STIMULUS SETTINGS
# ------------------------------------------------------------------
# Set to True if the images have been preprocessed, ie. the images
# have already been blurred
# Otherwise, the images are blurred in the background as participant
# information is collected
# DEPRECATED
PREPROCESSED_IMAGES = True

# Fill in wiremesh and make solid
# NOTE: For testing purposes only
#       It should be set to True for the final version
RENDER_SOLID = True

# Choose the variety of Gaussian Blurred height maps to be used in
# the experiment
# DEPRECATED
GAUSSIAN_BLURS = [2, 4, 8]

# Width of all the stimuli images
WIDTH = 512
# Height of all the stimuli images
HEIGHT = 512

# Height map data
# Width and height of each quadrilateral grid in the meshgrid
STEP_SIZE = 1
# Ratio to which the map is scaled in the Z axis
HEIGHT_RATIO = [0.06, 0.08]

# Size by which to scale the meshgrid for the stimuli
# This will be applied to the vertices passed to the Vertex Buffer Object
SCALE_X = 30.00
SCALE_Y = 30.00

STIMULI_DEPTH = -3.0


# ------------------------------------------------------------------
# OPENGL SETTINGS
# ------------------------------------------------------------------
# Set to true to use shaders in the program
# NOTE: For testing purposes only
#       It should be set to True for the final version
ENABLE_SHADER = True
GLSL_VERSION = 330

# Set filename for vertex shader and fragment shader
if GLSL_VERSION == 130:
    VERTEX_SHADER_FILE = 'shaders/vertex130.c'
    FRAGMENT_SHADER_FILE = 'shaders/fragment130.c'
    STIMULI_DEPTH = -5.0
elif GLSL_VERSION == 330:
    VERTEX_SHADER_FILE = 'shaders/vertex330.c'
    FRAGMENT_SHADER_FILE = 'shaders/fragment330.c'
    STIMULI_DEPTH = -3.0

# Use VertexAttribPointer instead of VertexPointer, TexCoordPointer
# and NormalPointer
# DEPRECATED
# USE_ATTRIB_POINTER = True

# Set depth size
DEPTH_SIZE = 24

# Set to True to run experiment fullscreen
# Set to False and use smaller window for testing purposes only
# NOTE: For testing purposes only
#       It should be set to True for the final version
FULLSCREEN = True

# Set eye position, center position and up position for camera
# DEPRECATED
EYE_POS = (4, 5, 30)
CENTER_POS = (5, 5, 6)
UP_POS = (7, 5, 2)

# GENERAL LIGHTING VALUES ------------------------------------------
# Set the color for the light(s)
# DEPRECATED
LIGHT_COLOR = [[0.7, 0.7, 0.65]]

# POINT LIGHTING VALUES --------------------------------------------
# Number of lights
# DEPRECATED
NUM_LIGHTS = 1
# Set the position for the light(s)
LIGHT_POSITION = [[1.0, -0.366, 1.634]]

# DIRECTIONAL LIGHTING VALUES --------------------------------------
# Set the direction for the light
LIGHT_DIRECTION = [0.0, 1.0, 1.0]

PER_PIXEL = False

# ------------------------------------------------------------------
# INCLINOMETER SETTINGS
# ------------------------------------------------------------------
# Inclinometer executable
INCLINOMETER = 'inclinometer'
