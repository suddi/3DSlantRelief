from numpy import array, float32, set_printoptions

from OpenGL.GL import (
                       glLoadIdentity, glMatrixMode,
                       glViewport, glDepthRange,
                       GL_PROJECTION,
                       glGetFloatv, GL_PROJECTION_MATRIX
)
from OpenGL.GLU import gluPerspective

from settings import SCREEN_WIDTH, SCREEN_HEIGHT, VIEW_DIST


class Projection(object):
    """
    Sets the perspective projection matrix

    >>> a = Projection(1920, 1080, [-3.0, 3.0])
    >>> a.frust = [-0.5 * 50, 0.5 * 50, -0.5 * 50, 0.5 * 50, -200, 40]
    >>> a.set_projection_matrix(a.eyeshiftset[1])
    array([[   4.  ,    0.  ,   -0.12,    0.  ],
           [   0.  ,    4.  ,    0.  ,   -0.  ],
           [   0.  ,    0.  ,   -1.5 ,    0.  ],
           [   0.  ,    0.  ,   -1.  ,  100.  ]], dtype=float32)
    """
    def __init__(self, width, height, eyeshift, *args, **kwargs):
        """
        Initiate the projection by recording the width and height of
        the opened window
        """
        self.width = width
        self.height = height

        self.eyeshiftset = [
                            [eyeshift[0].real, eyeshift[0].imag, VIEW_DIST],
                            [eyeshift[1].real, eyeshift[1].imag, VIEW_DIST]
        ]
        self.frust = [
                      -0.5 * SCREEN_WIDTH, 0.5 * SCREEN_WIDTH,
                      -0.5 * SCREEN_HEIGHT, 0.5 * SCREEN_HEIGHT,
                      -200, 40
        ]

        glViewport(0, 0, self.width, self.height)
        glDepthRange(0, 10)

    def set_perspective(self, fovy):
        """
        Set the perspective view
        """
        # Calculate aspect
        aspect = self.width / self.height

        # Make changes to projection matrix
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        # Set the perspective accordingly
        gluPerspective(fovy, aspect, 0.1, 10.0)

        self.matrix = glGetFloatv(GL_PROJECTION_MATRIX)

    def set_projection_matrix(self, eyepos):
        """
        Makes a projection matrix for use in OpenGL
        Adapted from previous c++ code

        This module assumes that screen is at depth of 0
        positive depth pointing out of the screen toward viewer
        far and near clipping planes defined relative to screen
        (so far is negative number, near is generally small positive)
        eye position relative to screen center

        frust is six values: left, right, bottom, top, far, near
        width and height of frustum specify values at screen distance
        eye position defined by eyepos
        the screen is at Z = 0.0
        near and far clipping planes defined relative to screen
        """
        m00 = 2.0 * eyepos[2] / (self.frust[1] - self.frust[0])
        m11 = 2.0 * eyepos[2] / (self.frust[3] - self.frust[2])

        # The eye position subtracted is to adjust for when
        # eye position is not centered relative to clipping box
        # 2.0 because the average of right and left are not normalized
        A = (self.frust[1] + self.frust[0] - 2.0 * eyepos[0]) /\
            (self.frust[1] - self.frust[0])
        B = (self.frust[3] + self.frust[2] - 2.0 * eyepos[1]) /\
            (self.frust[3] - self.frust[2])

        # NOTE: There is some ambiguity about the signs of C and D
        # This affects sign of depth component after projection
        # but not the projected X and Y coordinates
        if eyepos[2] > self.frust[5]:
            # This is the normal case, in which clipping past eye
            C = -(2.0 * eyepos[2] - self.frust[4] - self.frust[5]) /\
                (self.frust[5] - self.frust[4])
            D = -2.0 * (eyepos[2] - self.frust[4]) * \
                (eyepos[2] - self.frust[5]) / (self.frust[5] - self.frust[4])
        else:
            # If bad near clipping plane (behind eye)
            # use 80% of distance to eye as near clipping plane
            C = -(2.0 * eyepos[2] - self.frust[4] - 0.8 * eyepos[2]) /\
                (0.8 * eyepos[2] - self.frust[4])
            D = -2.0 * (eyepos[2] - self.frust[4]) *\
                (eyepos[2] - 0.8 * eyepos[2]) /\
                (0.8 * eyepos[2] - self.frust[4])

        E = -1 * m00 * eyepos[0] - eyepos[2] * A
        F = -1 * m11 * eyepos[1] - eyepos[2] * B
        G = D - C * eyepos[2]

        # The matrix is:
        # m00    0    0    0
        # 0    m11    0    0
        # A      B    C -1.0
        # E      F    G    eyepos[2]
        mproj = array([
                       round(m00, 4), 0.0, 0.0, 0.0,
                       0.0, round(m11, 4), 0.0, 0.0,
                       round(A, 4), round(B, 4), round(C, 4), -1.0,
                       round(E, 4), round(F, 4), round(G, 4),
                       round(eyepos[2], 4)
        ], dtype=float32)

        # Discovered that the above is the transpose of the desired matrix
        self.matrix = mproj.transpose()

        set_printoptions(suppress=True)
        print self.matrix

        return self.matrix

if __name__ == "__main__":
    import doctest
    doctest.testmod()
