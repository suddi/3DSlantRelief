from json import dump

from os.path import join, isfile

from pyglet.event import EVENT_HANDLED
from pyglet.clock import schedule_once
from pyglet.window import Window, key

from sys import exit

from time import time

from winsound import Beep

from inclinometer import Inclinometer
# from projection import Projection
from render import Render
from settings import (
                      BREAK_DURATION, BREAK_INTERVAL, ENABLE_SHADER,
                      FIX_DUR,
                      STIMULI_ONLY,
                      # SCALE_X, SCALE_Y
)
from stimuli import Stimuli
from tools import get_time


class Viewer(Window):
    """
    Create the Window and process OpenGL
    """
# ------------------------------------------------------------------
# HANDLE INITIALIZATION
# ------------------------------------------------------------------
    def __init__(self, participant, *args, **kwargs):
        """
        Setup window using default settings, disable visibility of
        the mouse cursor
        Setup the window for stimulus
        """
        # Record the start of the experiment
        self.exp_start = time()

        super(Viewer, self).__init__(*args, **kwargs)
        # Clear the scene as soon as the window is loaded
        self.clear()
        # Disable visibility of the mouse
        self.set_mouse_visible(False)

        if STIMULI_ONLY:
            self.states = [self.__display_stimuli]
        else:
            # INITIATE THE STATES REQUIRED FOR THE EXPERIMENT
            # Declare all the possible action states for Viewer
            self.states = [
                           self.__display_message, self.__ready_block
            ]

            # Set requirement of practice
            self.practice = participant['practice']
            # Set to True, when it is break time
            self.on_break = False
            # Set to True, when the experiment has run its course
            self.ended = False

            self.directory = participant['dir']
            self.session = participant['day']
            self.data = []
            # Initiate reaction time list
            self.reaction_times = []

            # If practice is required, add the states required onto itself
            # to create 2 blocks
            if self.practice:
                self.states += self.states

            # Add a __display_message state at the end to show the thank
            # you message
            self.states += [self.__display_message]

        # Set the state to be used
        self.run_state = self.states.pop(0)

        if participant:
            # Set the initial parameters for the window
            self.__setup(participant['eyeshift'], participant['stereo'])
        else:
            self.__setup()

        # Set the draw module
        self.on_draw = self.__draw

    def __setup(self, eyeshift=[-3.0, 3.0], stereo=False):
        """
        Initialize parameters for OpenGL and ready the
        texture for rendering
        """
        # Set the projection settings for OpenGL
        # self.projection = Projection(self.width, self.height, eyeshift)

        # Prepare OpenGL and display textures for rendering
        self.render = Render(self.width, self.height, eyeshift, stereo)

        # Create the Vertex Buffer Objects needed
        self.render.create_VBO(self.width, self.height)

        # Create the shaders as necessary
        self.render.create_shaders()

        # Initiate the variable that will hold the current image to
        # be rendered
        self.current_img = None

        # Instantiate the stimuli class and setup the order in which
        # to display the stimuli for practice or for the experimental
        # block
        self.stimulus = Stimuli()
        # Now setup the stimuli
        if hasattr(self, 'practice'):
            self.stimulus.setup(self.practice)
        else:
            self.stimulus.setup()
        # Ready the next stimuli block
        self.stimulus.run_state()

        # Keep a list of possible stimuli rotations about the Z-axis
        # self.z_rotation = [0]

        if not STIMULI_ONLY:
            self.inclinometer = Inclinometer()
            self.inclinometer.set_offset_Y()
            self.slants = []

        print 'Setting up of the experiment took %s seconds'\
              % get_time(self.exp_start, time())
        # Run the state that is required
        self.run_state()

# ------------------------------------------------------------------
# HANDLE KEYBOARD EVENTS
# ------------------------------------------------------------------

    def on_key_press(self, symbol, modifier):
        if symbol == key.ESCAPE:
            self.render.disable_GL_STATE()
            self.render.unbind_all()
            if not STIMULI_ONLY:
                self.inclinometer.close()
                self.__compile_data()
            exit(1)
        elif symbol == key.SPACE:
            if not self.on_break or self.states[0] == self.__display_message:
                if self.run_state == self.__display_stimuli:
                    if hasattr(self, 'reaction_times'):
                        self.reaction_times.append(time() - self.stimuli_presented)
                    press_time = time()
                    self.slants.append(self.inclinometer.get_Y() + 90.0)
                    print get_time(press_time, time())
                    Beep(2500, 500)
                # If there are still some states to be run
                # We continue onto them
                if self.states:
                    if not self.run_state == self.__display_fix:
                        # Move to the next state
                        self.run_state = self.states.pop(0)
                        # And run it
                        self.run_state()
                # Else we exit the experiment
                else:
                    exit(1)

# ------------------------------------------------------------------
# HANDLE STATES
# ------------------------------------------------------------------

    def __display_message(self):
        """
        Display the message as necessary
        """
        # If the experiment has not already ended, we prepare the next
        # stimulus
        if not self.ended and not self.on_break:
            # Get the next stimuli colormap and heightmap ready
            self.stimulus.run_state()
        # Tell the Render instance not attempt to render stimuli
        self.render_stimuli = False

        # If the experimental has ended, we display the message:
        # Thank you for your participation in the experiment!
        if self.ended:
            self.current_img = self.render.messages['thank_you']
            self.inclinometer.close()
            self.__compile_data()
        # If the practice block needs to be run, we display the message:
        # Please press [SPACE] to begin the practice block
        elif self.practice:
            self.current_img = self.render.messages['begin_practice']
        # If it is break time during the experimental block, we display
        # the message:
        # Take a break, please
        elif not self.practice and self.on_break:
            self.current_img = self.render.messages['break']
            # We then schedule the end of the break, to take place after
            # a certain number of seconds, set by BREAK_DURATION
            schedule_once(self.__end_break, BREAK_DURATION)
        # If the experimental block can be run, we display the message:
        # Please press [SPACE] to begin the formal experiment
        elif not self.practice and not self.on_break:
            self.__compile_data(False)
            self.current_img = self.render.messages['begin_exp']

        # Set the shaders to not be used, bind the VBO using bind_message
        # and assign current_img as the texture
        self.__ready_texture(False, self.render.bind_message)

    def __ready_block(self):
        """
        Extend the list of states so as to include the state change
        as the practice or experimental block is run
        """
        # Add further states in accordance with whether practice or
        # the formal experiment is to run
        states = []
        for i in range(0, len(self.stimulus.order) + 1):
            # Interchange between fixation point display and the stimuli
            states.append(self.__display_fix)
            states.append(self.__display_stimuli)

        # Add the newly created states to the front of the list of states
        self.states = states + self.states

        # If it is not the practice block, we must schedule a break
        # The interval to a break is determined by the setting: BREAK_INTERVAL
        schedule_once(self.__break_time, BREAK_INTERVAL)

        if states:
            # Pop the foremost state and run it
            self.run_state = self.states.pop(0)
        self.run_state()

    def __display_fix(self):
        """
        Display the fixation point
        """
        # Tell the Render instance not attempt to render stimuli
        self.render_stimuli = False

        # Set current_img to the fixation point image
        self.current_img = self.render.fix_image

        # Set the shaders to not be used, bind the VBO using bind_message
        # and assign current_img as the texture
        self.__ready_texture(False, self.render.bind_message)

        # Ready the change over in state
        schedule_once(self.__next_state, FIX_DUR)

    def __display_stimuli(self):
        """
        Display the stimuli images in order
        """
        if not STIMULI_ONLY:
            temp_data = []
            for data in self.stimulus.current:
                temp_data.append(data)
                self.data.append(temp_data)

        # Set current_img to the next stimulus image to be displayed
        self.current_img = self.stimulus.colormap[self.stimulus.current[0]]

        # Set the shaders to be used, bind the VBO and assign current_img
        # as the texture
        # Use the shader only if allowed by ENABLE_SHADER
        self.__ready_texture(True, self.render.bind_stimuli)

        # Randomly choose rotation for stimuli about the X-axis
        # from the list of POSSIBLE_SLANTS
        # num = randint(0, len(POSSIBLE_SLANTS) - 1)
        # self.render.rotation['X'] = POSSIBLE_SLANTS[num]

        self.render.scale['Z'] = self.stimulus.current[1]
        self.render.rotation['X'] = self.stimulus.current[2]

        # Randomly choose rotation for stimuli about the Z-axis
        # from the list of possible Z-axis rotations
        # num = randint(0, len(self.z_rotation) - 1)
        # self.render.rotation['Z'] = self.z_rotation[num]

        # If there are no more stimulus to present in this block
        if not self.stimulus.run_state():
            # If the practice block is currently ongoing
            # We must now prepare for the experimental block
            if self.practice:
                # Since we just finished the practice block
                # We can set self.practice to False now
                self.practice = False
                # Prepare the experimental block
                self.stimulus.run_state()
            # If the practice block is not running, it must be the
            # experimental block that has ended
            else:
                # Set ended to true
                self.ended = True

    def __break_time(self, dt):
        """
        Add a __display_message state into self.states to display a break
        """
        if self.states and not self.ended:
            # Set on_break to True, as we are now on a break
            self.on_break = True

            # If the next state is to display the fixation point, we can
            # schedule the break before the next stimuli process begins
            if self.states[0] == self.__display_fix:
                # Place the __display_message state before the other states
                self.states = [self.__display_message] + self.states
            # If the next state is to display the stimuli, we must schedule
            # the break after it is completed
            elif self.states[0] == self.__display_stimuli:
                # We pop out the __display_stimuli state
                self.states.pop(0)
                # We then add it back in, with the __display_message state
                self.states = [self.__display_stimuli, self.__display_message] +\
                               self.states

    def __end_break(self, dt):
        """
        Add a __display_message state into self.states to display the
        end of the break
        """
        # Set on_break to False, as the break has now ended
        self.on_break = False

        # Tell the Render instance not attempt to render stimuli
        self.render_stimuli = False
        # Set the current_img to the resume_exp image
        self.current_img = self.render.messages['resume_exp']

        # Set the shaders to not be used, bind the VBO using bind_message
        # and assign current_img as the texture
        self.__ready_texture(False, self.render.bind_message)
        schedule_once(self.__break_time, BREAK_INTERVAL)

    def __next_state(self, dt=FIX_DUR):
        """
        Move onto the next state and run it
        """
        self.run_state = self.states.pop(0)
        self.run_state()

    def __ready_texture(self, shader_use, bind_function):
        """
        Set the shader use, call the binding function for the Vertex
        Buffer Objects and assign the texture as necessary
        """
        # Set the use of the shaders
        self.__shader_use(shader_use)

        # Call the appropriate VBO binding function
        bind_function()

        if ENABLE_SHADER:
            i = self.stimulus.current[0]
            if shader_use:
                textures = [self.current_img, self.stimulus.heightmap[i],
                            self.stimulus.normalmap[i]]
            else:
                textures = [self.current_img]
            for img in textures:
                # Assign the texture
                self.render.assign_texture(img, img.width, img.height)
        else:
            # Assign the texture
            self.render.assign_texture(self.current_img,
                                       self.current_img.width,
                                       self.current_img.height)

# ------------------------------------------------------------------
# HANDLE SHADER USE
# ------------------------------------------------------------------

    def __shader_use(self, use):
        """
        If the shader is enabled and is set to be used for the rendering,
        run it.
        Otherwise pass boolean value [use] to not use shaders in the
        rendering, even if ENABLE_SHADER is set to True
        """
        # Store identification of stimuli or non-stimuli image rendering
        self.render_stimuli = use

        # If the shader is enabled, pass values to the shader
        if ENABLE_SHADER:
            i = self.stimulus.current[0]
            # Pass stimuli colormap and heightmap to shaders
            self.render.pass_to_shaders(self.render.shader, use,
                                        self.current_img,
                                        self.stimulus.heightmap[i],
                                        self.stimulus.normalmap[i])

# ------------------------------------------------------------------
# HANDLE RENDERING
# ------------------------------------------------------------------

    def __draw(self):
        """
        Overwriting Window's own on_draw() module
        This will simply call upon self.render.draw() after all the
        states have been set
        """
        # for i in range(0, len(self.projection.eyeshiftset)):
            # Set the view
        # self.projection.set_perspective(50.0)
        # projection = self.projection.set_projection_matrix(self.projection.\
        #                                                    eyeshiftset[1])

        # Call the general draw module in Render
        if self.render_stimuli:
            self.render.draw(self.render_stimuli, self.render.rotation['X'])
            # for i in [-1, 0, 1]:
                # for j in [0, 1, 2]:
                    # self.render.translation['X'] = i * SCALE_X
                    # self.render.translation['Y'] = j * SCALE_Y
                    # self.render.draw(self.render_stimuli)
            self.stimuli_presented = time()
        else:
            self.render.draw()

        # Return success of rendering
        return EVENT_HANDLED

    def __compile_data(self, exp_ended=True):
        if exp_ended:
            total_exp_time = get_time(self.exp_start, time())
            print 'The experiment ran for %s seconds' % total_exp_time

        compiled_data = {}
        for count, data in enumerate(self.data):
            if count < len(self.reaction_times):
                compiled_data[count] = {}
                compiled_data[count]['image'] = data[0]
                compiled_data[count]['height_ratio'] = data[1]
                compiled_data[count]['slant'] = data[2]
                compiled_data[count]['rt'] = self.reaction_times[count]
                compiled_data[count]['answer'] = self.slants[count]
            else:
                break

        if compiled_data:
            self.data = []
            self.reaction_times = []
            self.slants = []

            path = 'session'
            if not exp_ended:
                path = 'practice'
            ext = ''
            loop = 0
            while True:
                t = join(self.directory, '%s_%d%s.json' % (path,
                                                           self.session, ext))
                if not isfile(t):
                    path = t
                    break
                ext = chr(65 + loop)
                loop += 1

            with open(path, 'wb') as f:
                dump(compiled_data, f)

if __name__ == '__main__':
    # Run the experiment even without running it directly from main.py
    from main import run_experiment
    run_experiment()
