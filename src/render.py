from math import cos, sin

from numpy import array, float32

from pyglet.image import load

from OpenGL.GL import *

# from pyglet.gl import GLfloat

from re import findall

from time import time

from buffers import VertexBuffer
from modelview import ModelView
from projection import Projection
from settings import (
                      ENABLE_SHADER, GLSL_VERSION, VERTEX_SHADER_FILE, FRAGMENT_SHADER_FILE,
                      IMG_FIX, IMG_MSG,
                      LIGHT_COLOR, LIGHT_POSITION, LIGHT_DIRECTION, NUM_LIGHTS,
                      RENDER_SOLID,
                      SCALE_X, SCALE_Y, STIMULI_DEPTH,
                      STEP_SIZE, WIDTH, HEIGHT,
                      STIMULI_ONLY, PER_PIXEL
)
from shaders import FragmentShader, VertexShader, ShaderProgram
from tools import get_coords, get_time, opengl_info, pixel_access, deg_to_rad
# from vbo import VBO


class Render(object):
    """
    This class handles the OpenGL rendering process

    This is separate from the pyglet rendering, as it runs using OpenGL
    directly
    """

# ------------------------------------------------------------------
# HANDLE INITIALIZATION
# ------------------------------------------------------------------

    def __init__(self, *args, **kwargs):
        """
        General initialization function for OpenGL, readying all the
        non-stimuli images and setting the parameters for rendering
        parameters
        """
        # Initialize the OpenGL parameters
        self.__init_GL()
        opengl_info()
        stereo = False

        if not STIMULI_ONLY:
            # Initiate the message textures we will use in the experiment
            self.__init_messages()
            # Initiate the fixation point texture we will use
            self.__init_fix()

        # Initialize the geometry
        self.__init_geometry()
        # Initialize the lighting
        self.__init_lighting()

        if args:
            # self.__init_VBO(args)
            self.__init_projection(args)
            stereo = args[-1]
        self.__init_modelview()

        self.__init_stereo(stereo)
        self.__init_grid()

        # Enable the basic GL_STATES that will be in use throughout
        # the experiment
        self.enable_GL_STATE()

    def __init_GL(self):
        """
        General initialization module for OpenGL, setting all of the
        parameters to be use throughout the experiment
        """
        # Set the background color to black
        glClearColor(0.0, 0.0, 0.0, 1.0)
        # Set the clearing depth buffer
        glClearDepth(1.0)

        # Select type of depth test to perform
        glDepthFunc(GL_LEQUAL)
        # Really good for perspective calculations
        glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)

    def __init_messages(self):
        """
        Prepare all the message images for rendering as textures
        """
        # Store all the message images here
        self.messages = {}
        # Iterating through all the message images
        for filename in IMG_MSG:
            # Get the name of the message state
            state = findall(r'\\(\w+)\.jpg', filename)
            # If the regex finds something, use the first element
            # of the resultant list
            if state:
                state = state[0]
            # Load the image
            self.messages[state] = load(filename)

    def __init_fix(self):
        # Load the fixation point image from directory
        self.fix_image = load(IMG_FIX)

    def __init_stereo(self, stereo):
        if stereo:
            self.buffers = [GL_BACK_LEFT, GL_BACK_RIGHT]
        else:
            self.buffers = [GL_BACK]

    def __init_grid(self):
        self.translate_stimuli = [
                                  (-2.0, 4.0), (0.0, 4.0), (2.0, 4.0),
                                  (-2.0, 2.0), (0.0, 2.0), (2.0, 2.0),
                                  (-2.0, 0.0), (0.0, 0.0), (2.0, 0.0),
                                  (-2.0, -2.0), (0.0, -2.0), (2.0, -2.0)
        ]
        self.translate_stimuli = [(0.0, 0.0)]
        self.translate_message = [(0.0, 0.0)]

    # def __init_VBO(self, args):
        # Calculate the width displacement from the midpoint of the screen
        # wd = round(self.fix_image.width / float(args[0]), 2)
        # Calculate the height displacement from the midpoint of the screen
        # hd = round(self.fix_image.height / float(args[1]), 2)

        # self.vbo = VBO(wd, hd)

# ------------------------------------------------------------------
# HANDLE GEOMETRY
# ------------------------------------------------------------------

    def __init_geometry(self):
        """
        This module sets the geometry to be used in the rendering of
        the display messages and stimuli
        """
        # Set values for geometry that will be used later
        self.rotation = {'X': 0.0, 'Y': 0.0, 'Z': 0.0}
        self.translation = {'X': 0.0, 'Y': 0.0, 'Z': STIMULI_DEPTH}
        self.scale = {'X': 1.0, 'Y': 1.0, 'Z': 1.0}

    def __set_geometry(self):
        """
        Setup the geometry for the model
        Takes care of the translation, rotation and scaling needs of the model
        """
        # Switch to modelview
        glMatrixMode(GL_MODELVIEW)
        # Reset The View
        glLoadIdentity()

        # Move into the screen
        glTranslatef(self.translation['X'],
                     self.translation['Y'],
                     self.translation['Z'])

        # Rotate the texture on its X-axis
        glRotatef(self.rotation['X'] * -1, 1.0, 0.0, 0.0)
        # Rotate the texture on its Y-axis
        glRotatef(self.rotation['Y'] * -1, 0.0, 1.0, 0.0)
        # Rotate the texture on its Z-axis
        glRotatef(self.rotation['Z'] * -1, 0.0, 0.0, 1.0)

        # Scale the texture
        # For Z-axis, multiply it by the HEIGHT_RATIO set
        glScalef(self.scale['X'], self.scale['Y'],
                 self.scale['Z'])

# ------------------------------------------------------------------
# HANDLE MATRICES
# ------------------------------------------------------------------

    def __init_projection(self, args):
        self.projection = Projection(args[0], args[1], args[2])

    def __init_modelview(self):
        self.modelview = ModelView()

    def __set_modelview(self):
        self.modelview.set_matrix(self.rotation, self.scale, self.translation)

# ------------------------------------------------------------------
# HANDLE LIGHTING
# ------------------------------------------------------------------

    def __init_lighting(self):
        """
        This module sets the lighting parameters to be used by the shaders
        in the rendering of the stimuli

        NOTE: This is used only with the rendering of stimuli, it is
              not used with the display of messages or the fixation point
        """
        # Set the light position
        # If there is only light source being used, set it to the first
        # element of LIGHT_POSITION
        if len(LIGHT_POSITION) == 1:
            self.light_position = LIGHT_POSITION[0]
        # If there are multiple light sources, we keep it as a list
        else:
            self.light_position = LIGHT_POSITION

        # Set the light color
        # If there is only light source being used, set it to the first
        # element of LIGHT_COLOR
        if len(LIGHT_COLOR) == 1:
            self.light_color = LIGHT_COLOR[0]
        # If there are multiple light sources, we keep it as a list
        else:
            self.light_color = LIGHT_COLOR

# ------------------------------------------------------------------
# HANDLE OPENGL STATES
# ------------------------------------------------------------------

    def enable_GL_STATE(self):
        """
        Enables all required OpenGL states

        This module will enable:
            - Depth Test
            - Texture
            - Array Buffers
        """
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_TEXTURE_2D)

        if not ENABLE_SHADER or GLSL_VERSION == 130:
            # Enable all the corresponding buffer arrays
            glEnableClientState(GL_TEXTURE_COORD_ARRAY)
            glEnableClientState(GL_VERTEX_ARRAY)
            glEnableClientState(GL_NORMAL_ARRAY)

    def disable_GL_STATE(self):
        """
        Disables all enabled OpenGL states

        This module will disable:
            - Depth Test
            - Array Buffers
        for complete shutdown of all GL_STATES
        """
        glDisable(GL_DEPTH_TEST)
        glDisable(GL_TEXTURE_2D)

        if not ENABLE_SHADER or GLSL_VERSION == 130:
            # Disable all the corresponding buffer arrays
            glDisableClientState(GL_VERTEX_ARRAY)
            glDisableClientState(GL_TEXTURE_COORD_ARRAY)
            glDisableClientState(GL_NORMAL_ARRAY)

# ------------------------------------------------------------------
# HANDLE VERTEX BUFFER OBJECTS
#
# THIS CODE HAS NOW BEEN MOVE TO vbo.py
# AND IMPLEMENTED WITH MULTI-THREADING
# ------------------------------------------------------------------

    def create_VBO(self, window_width, window_height):
        """
        Create OpenGL Vertex Buffer Objects as need for:
            - Non-stimuli images
            - Stimuli images
        """
        scaleX = SCALE_X
        scaleY = SCALE_Y
        if not ENABLE_SHADER or GLSL_VERSION == 130:
            scaleX = 1.0
            scaleY = 1.0

        if not STIMULI_ONLY:
            self.message_VBO = {}
            # Create the Vertex Buffer Object to house the texture
            # coordinates and vertices for message display
            self.__message_VBO(window_width, window_height, scaleX, scaleY)

        self.stimuli_VBO = {}
        # Create the Vertex Buffer Object to house the texture
        # coordinates, vertices and normals for the stimuli
        self.__stimuli_VBO(scaleX, scaleY)

    def __message_VBO(self, width, height, scaleX, scaleY):
        """
        Create the Vertex Buffer Objects for message display
        """
        # Calculate the width displacement from the midpoint of the screen
        wd = round(self.fix_image.width / float(width), 2)
        # Calculate the height displacement from the midpoint of the screen
        hd = round(self.fix_image.height / float(height), 2)

        # Create the buffer array for Vertex
        l = [
             [(0.0 - wd) * scaleX, (0.0 - hd) * scaleY],
             [(0.0 + wd) * scaleX, (0.0 - hd) * scaleY],
             [(0.0 + wd) * scaleX, (0.0 + hd) * scaleY],
             [(0.0 - wd) * scaleX, (0.0 + hd) * scaleY]
        ]
        self.message_VBO['vertex'] = VertexBuffer(array(l, dtype=float32))

        # Create the buffer array for TexCoord
        l = [[0.0, 0.0], [1.0, 0.0], [1.0, 1.0], [0.0, 1.0]]
        self.message_VBO['texcoord'] = VertexBuffer(array(l, dtype=float32))

        # Create the buffer array for Normal
        l = [[0.0, 0.0, 1.0], [0.0, 0.0, 1.0],
             [0.0, 0.0, 1.0], [0.0, 0.0, 1.0]]
        self.message_VBO['normal'] = VertexBuffer(array(l, dtype=float32))

#     def __message_VBO2(self, width, height):
#         """
#         Create the Vertex Buffer Objects for message display
#         """
#         # Calculate the width displacement from the midpoint of the screen
#         wd = round(self.fix_image.width / float(width), 2)
#         # Calculate the height displacement from the midpoint of the screen
#         hd = round(self.fix_image.height / float(height), 2)
#
#         vertices = [
#         #           VERTEX              TEXCOORD  NORMAL
#                     [0.0 - wd, 0.0 - hd, 0.0, 0.0, 0.0, 0.0, 1.0],
#                     [0.0 + wd, 0.0 - hd, 1.0, 0.0, 0.0, 0.0, 1.0],
#                     [0.0 + wd, 0.0 + hd, 1.0, 1.0, 0.0, 0.0, 1.0],
#                     [0.0 - wd, 0.0 + hd, 0.0, 1.0, 0.0, 0.0, 1.0]
#         ]
#
#         self.message_VBO = VertexBuffer(array(vertices, dtype=float32))

    def __stimuli_VBO(self, scaleX, scaleY):
        """
        Create the Vertex Buffer Objects for stimuli display
        """
        # Initiate the VBOs pertaining to the stimuli texture
        self.stimuli_VBO['vertex'] = []
        self.stimuli_VBO['texcoord'] = []
        self.stimuli_VBO['normal'] = []

        t0 = time()
        # Iterate through the points, moving up by the preset value:
        # STEP_SIZE
        for X in xrange(0, WIDTH - STEP_SIZE + 1, STEP_SIZE):
            for Y in xrange(0, HEIGHT - STEP_SIZE + 1, STEP_SIZE):

                # BOTTOM LEFT CORNER
                x, y, vertX, vertY = get_coords(X, Y, scaleX, scaleY)
                self.stimuli_VBO['vertex'].append([vertX, vertY])
                self.stimuli_VBO['texcoord'].append([x, y])

                # BOTTOM RIGHT CORNER
                x, y, vertX, vertY = get_coords(X + STEP_SIZE, Y,
                                                scaleX, scaleY)
                self.stimuli_VBO['vertex'].append([vertX, vertY])
                self.stimuli_VBO['texcoord'].append([x, y])

                # TOP RIGHT CORNER
                x, y, vertX, vertY = get_coords(X + STEP_SIZE,
                                                Y + STEP_SIZE,
                                                scaleX, scaleY)
                self.stimuli_VBO['vertex'].append([vertX, vertY])
                self.stimuli_VBO['texcoord'].append([x, y])

                # TOP LEFT CORNER
                x, y, vertX, vertY = get_coords(X, Y + STEP_SIZE,
                                                scaleX, scaleY)
                self.stimuli_VBO['vertex'].append([vertX, vertY])
                self.stimuli_VBO['texcoord'].append([x, y])

                for i in range(0, 4):
                    self.stimuli_VBO['normal'].append([0.0, 0.0, 1.0])

        # Instatiate the Vertex Buffer Objects using VertexBuffer
        self.stimuli_VBO['vertex'] = \
        VertexBuffer(array(self.stimuli_VBO['vertex'], dtype=float32))
        self.stimuli_VBO['texcoord'] = \
        VertexBuffer(array(self.stimuli_VBO['texcoord'], dtype=float32))
        self.stimuli_VBO['normal'] = \
        VertexBuffer(array(self.stimuli_VBO['normal'], dtype=float32))

        print 'Preparing the VBOs took %s seconds' % get_time(t0, time())

#     def __stimuli_VBO2(self):
#         """
#         Create the Vertex Buffer Objects for stimuli display
#         """
#         vertices = []
#         indices = []
#         next_column = HEIGHT / STEP_SIZE + 1
#
#         # Iterate through the points, moving up by the preset value:
#         # STEP_SIZE
#         for X in xrange(0, WIDTH + 1, STEP_SIZE):
#             for Y in xrange(0, HEIGHT + 1, STEP_SIZE):
#                 # Handle the VERTEX BUFFER OBJECT
#                 x, y, vertX, vertY = self.__get_coords(X, Y)
#                 vertices.append(
#                 #         VERTEX        TEXCOORD
#                          [vertX, vertY, x, y,
#                 #         NORMAL
#                           0.0, 0.0, 1.0]
#                 )
#
#                 # Handle the ELEMENT BUFFER OBJECT
#                 index_x = X / STEP_SIZE
#                 index_y = Y / STEP_SIZE
#                 origin = index_x + index_y
#
#                 indices.append(
#                 #               BOTTOM LEFT CORNER
#                                [origin,
#                 #               BOTTOM RIGHT CORNER
#                                 origin + next_column,
#                 #               TOP RIGHT CORNER
#                                 origin + next_column + 1,
#                 #               TOP LEFT CORNER
#                                 origin + 1
#                                ]
#                 )
#
#         self.stimuli_VBO = VertexBuffer(array(vertices, dtype=float32))
#         self.indices_VBO = VertexBuffer(array(indices, dtype=int32))

    def bind_message(self):
        """
        Bind all the Vertex Buffer Objects necessary for displaying
        messages and the fixation point
        """
        # Bind all the Vertex Buffer Objects
        if ENABLE_SHADER and GLSL_VERSION == 330:
            self.message_VBO['vertex'].bind_attribute(0, 2, GL_FLOAT)
            self.message_VBO['texcoord'].bind_attribute(1, 2, GL_FLOAT)
            self.message_VBO['normal'].bind_attribute(2, 3, GL_FLOAT)
        else:
            self.message_VBO['vertex'].bind_vertices(2, GL_FLOAT)
            self.message_VBO['texcoord'].bind_texcoords(2, GL_FLOAT)
            self.message_VBO['normal'].bind_normals(GL_FLOAT)

    def bind_stimuli(self):
        """
        Bind all the Vertex Buffer Objects necessary for displaying the
        stimuli
        """
        # Bind all the Vertex Buffer Objects
        if ENABLE_SHADER and GLSL_VERSION == 330:
            self.stimuli_VBO['vertex'].bind_attribute(0, 2, GL_FLOAT)
            self.stimuli_VBO['texcoord'].bind_attribute(1, 2, GL_FLOAT)
            self.stimuli_VBO['normal'].bind_attribute(2, 3, GL_FLOAT)
        else:
            self.stimuli_VBO['vertex'].bind_vertices(2, GL_FLOAT)
            self.stimuli_VBO['texcoord'].bind_texcoords(2, GL_FLOAT)
            self.stimuli_VBO['normal'].bind_normals(GL_FLOAT)

    def unbind_all(self):
        if hasattr(self, 'message_VBO'):
            self.message_VBO['vertex'].unbind()
            self.message_VBO['texcoord'].unbind()
            self.message_VBO['normal'].unbind()

        if hasattr(self, 'stimuli_VBO'):
            self.stimuli_VBO['vertex'].unbind()
            self.stimuli_VBO['texcoord'].unbind()
            self.stimuli_VBO['normal'].unbind()

# ------------------------------------------------------------------
# HANDLE SHADERS
# ------------------------------------------------------------------

    def create_shaders(self):
        """
        Create the OpenGL program on the GPU and attach the shaders
        """
        # If set to use shaders, enable them accordingly
        if ENABLE_SHADER:
            # Get the vertex shader
            vs = VertexShader(VERTEX_SHADER_FILE)
            # Get the fragment shader
            fs = FragmentShader(FRAGMENT_SHADER_FILE)
            # Assign the shader for the program
            self.shader = ShaderProgram(vs, fs)
            # Use the shader with the program
            self.shader.use()

    def pass_to_shaders(self, program, process_stimuli, colormap, heightmap,
                        normalmap):
        """
        Pass variables to shaders
        """
        # ----------------------------------------------------------
        # HANDLE DISPLACEMENT MAPPING VARIABLES
        # ----------------------------------------------------------

        # Get the texture for colormap
        colormap = colormap.get_texture()
        # Work on GL_TEXTURE0
        glActiveTexture(GL_TEXTURE0)
        # Bind the colormap
        glBindTexture(colormap.target, colormap.id)
        # Get the location of the colormap and pass it to the shader
        loc = glGetUniformLocation(program.id, 'colormap')
        glUniform1i(loc, 0)

        # Work on GL_TEXTURE_1
        glActiveTexture(GL_TEXTURE1)
        # Get the location of the heightmap
        loc = glGetUniformLocation(program.id, 'heightmap')
        # If the use of heightmaps is enabled, this must mean we are
        # rendering the stimuli
        if process_stimuli:
            # Get the texture for heightmap
            heightmap = heightmap.get_texture()
            # Bind the displacement map
            glBindTexture(heightmap.target, heightmap.id)
        # Pass the variable colormap to the loc for heightmap in
        # the vertex shader
        glUniform1i(loc, 1)

        glActiveTexture(GL_TEXTURE2)
        loc = glGetUniformLocation(program.id, 'normalmap')
        normalmap = normalmap.get_texture()
        glBindTexture(normalmap.target, normalmap.id)
        glUniform1i(loc, 2)

        # ----------------------------------------------------------
        # HANDLE LIGHTING VARIABLES
        # ----------------------------------------------------------

        # Get the location of the light position and pass it to the
        # shader
        # loc = glGetUniformLocation(program.id, 'light_position')
        # glUniform3fv(loc, NUM_LIGHTS, self.light_position)

        # Get the location of the light color and pass it to the shader
        # loc = glGetUniformLocation(program.id, 'light_color')
        # glUniform3fv(loc, NUM_LIGHTS, self.light_color)

        loc = glGetUniformLocation(program.id, 'light_direction')
        glUniform3fv(loc, 1, LIGHT_DIRECTION)

        # ----------------------------------------------------------
        # HANDLE ENABLERS
        # ----------------------------------------------------------

        # Get the location of the enable_vertex variable and pass enabled
        # to it
        loc = glGetUniformLocation(program.id, 'process_stimuli')
        glUniform1iv(loc, 1, process_stimuli)

        loc = glGetUniformLocation(program.id, 'per_pixel')
        glUniform1iv(loc, 1, PER_PIXEL)

        # ----------------------------------------------------------
        # HANDLE VERTEX BUFFER OBJECTS
        # ----------------------------------------------------------

        # loc = glGetAttribLocation(program.id, 'vertVertex')
        # glVertexAttribPointer(loc, 2, GL_FLOAT, GL_FALSE, 0, None)
        # glEnableVertexAttribArray(loc)

        # loc = glGetAttribLocation(program.id, 'vertTexCoord')
        # if process_stimuli:
            # glVertexAttribPointer(loc, 2, GL_FLOAT, GL_FALSE, 0,
            #                       self.stimuli_stride)
        # else:
            # glVertexAttribPointer(loc, 2, GL_FLOAT, GL_FALSE, 0,
            #                       self.message_stride)
        # glEnableVertexAttribArray(loc)

        # loc = glGetAttribLocation(program.id, 'vertNormal')
        # if process_stimuli:
            # glVertexAttribPointer(loc, 3, GL_FLOAT, GL_FALSE, 0,
            #                       self.stimuli_stride * 2)
        # else:
            # glVertexAttribPointer(loc, 3, GL_FLOAT, GL_FALSE, 0,
            #                       self.message_stride * 2)
        # glEnableVertexAttribArray(loc)

# ------------------------------------------------------------------
# HANDLE TEXTURE
# ------------------------------------------------------------------

    def assign_texture(self, texture, width=WIDTH, height=HEIGHT):
        """
        Assign the texture for viewing in OpenGL
        """
        # Bind the texture
        print texture.get_texture().id
        glBindTexture(GL_TEXTURE_2D, texture.get_texture().id)
        # Assign 2D texture
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, width, height, 0, GL_RGBA,
                     GL_UNSIGNED_BYTE, pixel_access(texture))

        # Settings for use of the texture
        glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)

        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)

        glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_DECAL)

# ------------------------------------------------------------------
# HANDLE OPENGL DRAWING
# ------------------------------------------------------------------

    def draw(self, render_stimuli=False, rot=0.0):
        """
        General draw module that must decide between the draw module
        to use. It can either render a stimuli image or non-stimuli
        message or fixation point
        """
        for count, color_buffer in enumerate(self.buffers):
            glDrawBuffer(color_buffer)
            # Clear the screen and the depth buffer
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

            if ENABLE_SHADER and GLSL_VERSION == 330:
                self.projection.set_projection_matrix(self.projection\
                                                      .eyeshiftset[count])
            else:
                self.projection.set_perspective(50.0)

            # If not drawing the stimuli, we can reset the geometry
            if not rot:
                # Initialize the geometry each time, to reset it
                self.__init_geometry()

            if render_stimuli:
                translate = self.translate_stimuli
            else:
                translate = self.translate_message

            if not count:
                rot = deg_to_rad(-rot)
            for x, y in translate:
                self.translation['Z'] = STIMULI_DEPTH
                self.translation['X'] = x * SCALE_X
                self.translation['Y'] = y * cos(rot) * SCALE_Y
                if y:
                    self.translation['Z'] += (y * sin(rot) * SCALE_Y)

                # Now set the values
                if ENABLE_SHADER and GLSL_VERSION == 330:
                    self.modelview.set_matrix(self.rotation, self.scale,
                                              self.translation)
                    self.__pass_matrix()
                else:
                    self.__set_geometry()

                # For testing purposes only
                # self.__print_matrices()

                # If we must render_stimuli, we call self.__draw_model
                if rot:
                    self.__draw_model()
                # If we must render a non-stimuli image,
                # we call self.__draw_message
                else:
                    self.__draw_message()

    def __pass_matrix(self):
        loc = glGetUniformLocation(self.shader.id, 'ProjectionMatrix')
        glUniformMatrix4fv(loc, 1, GL_FALSE, self.projection.matrix)

        loc = glGetUniformLocation(self.shader.id, 'ModelViewMatrix')
        glUniformMatrix4fv(loc, 1, GL_FALSE, self.modelview.matrix)

        loc = glGetUniformLocation(self.shader.id, 'NormalMatrix')
        glUniformMatrix3fv(loc, 1, GL_FALSE, self.modelview.normal)

    def __print_matrices(self):
        print 'GL_PROJECTION_MATRIX:'
        if ENABLE_SHADER:
            print self.projection.matrix
        else:
            print glGetFloatv(GL_PROJECTION_MATRIX)

        print 'GL_MODELVIEW_MATRIX:'
        if ENABLE_SHADER:
            print self.modelview.matrix
        else:
            print glGetFloatv(GL_MODELVIEW_MATRIX)

    def __draw_axis(self):
        """
        Draw the three axes to indicate their positioning

        DEPRECATED
        """
        glBegin(GL_LINES)

        # Draw line for X axis
        glColor3f(1.0, 0.0, 0.0)
        glVertex3f(0.0, 0.0, 0.0)
        glVertex3f(1.0, 0.0, 0.0)

        # Draw line for Y axis
        glColor3f(0.0, 1.0, 0.0)
        glVertex3f(0.0, 0.0, 0.0)
        glVertex3f(0.0, 1.0, 0.0)

        # Draw line for Z axis
        glColor3f(0.0, 0.0, 1.0)
        glVertex3f(0.0, 0.0, 0.0)
        glVertex3f(0.0, 0.0, 1.0)
        glEnd()

    def __draw_message(self):
        """
        Draw the message or fixation point
        """
        # Draw the quadrilateral mapping it to the texture
        glDrawArrays(GL_QUADS, 0, 4)

    def __draw_model(self):
        """
        Draw the stimulus
        """
        points = (WIDTH / STEP_SIZE) * (HEIGHT / STEP_SIZE) * 4
        # If set to render solid, render the solid version
        if RENDER_SOLID:
            # Start drawing the quadrilateral
            glDrawArrays(GL_QUADS, 0, points)
        # Else produce wireframe
        else:
            # Draw lines to indicate the wireframe
            glDrawArrays(GL_LINES, 0, points)


if __name__ == '__main__':
    # Run the experiment even without running it directly from main.py
    from main import run_experiment
    run_experiment()
