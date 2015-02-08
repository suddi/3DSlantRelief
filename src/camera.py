from OpenGL.GL import (
                       glLoadIdentity, glMatrixMode,
                       GL_MODELVIEW
)
from OpenGL.GLU import gluLookAt

# Import default camera settings from settings.py
from settings import CENTER_POS, EYE_POS, UP_POS


class Camera(object):

    def __init__(self, *args, **kwargs):
        """
        Set eye position, center position and up position to their
        default settings
        """
        # Set the default values from settings for eye position, center
        # position and up position
        self.eye = EYE_POS
        self.center = CENTER_POS
        self.up = UP_POS

    def look_at(self, eye=None, center=None, up=None):
        '''
        Set the camera view with gluLookAt, use default settings
        if values are not provided
        '''
        # If the arguments passed to this module have value, set the
        # corresponding class variable to the value passed
        if eye:
            self.eye = eye
        if center:
            self.center = center
        if up:
            self.up = up

        # Switch to modelview
        self.reset()

        # Set camera lookat
        gluLookAt(
                  self.eye[0], self.eye[1], self.eye[2],
                  self.center[0], self.center[1], self.center[2],
                  self.up[0], self.up[1], self.up[2]
        )

    def reset(self):
        """
        Reset to modelview
        """
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
