from math import cos, sin

from numpy import array, float32

from tools import deg_to_rad


class ModelView(object):
    def __init__(self, *args, **kwargs):
        # The matrix is:
        # 1    0    0    0
        # 0    1    0    0
        # 0    0    1    0
        # 0    0    0    1
        self.matrix = array([
                             1.0, 0.0, 0.0, 0.0,
                             0.0, 1.0, 0.0, 0.0,
                             0.0, 0.0, 1.0, 0.0,
                             0.0, 0.0, 0.0, 1.0
        ], dtype=float32)

    def set_matrix(self, rotation, scale, translation):
        theta = deg_to_rad(rotation['X'] * -1)
        sin_x = sin(theta)
        cos_x = cos(theta)

        theta = deg_to_rad(rotation['Y'] * -1)
        sin_y = sin(theta)
        cos_y = cos(theta)

        theta = deg_to_rad(rotation['Z'] * -1)
        sin_z = sin(theta)
        cos_z = cos(theta)

        # Determine left (X) axis
        left_x = (cos_y * cos_z)
        left_y = (sin_x * sin_y * cos_z + cos_x * sin_z)
        left_z = (-cos_x * sin_y * cos_z + sin_x * sin_z)

        # Determine up (Y) axis
        up_x = (-cos_y * sin_z)
        up_y = (-sin_x * sin_y * sin_z + cos_x * cos_z)
        up_z = (cos_x * sin_y * sin_z + sin_x * cos_z)

        # Determine forward (Z) axis
        forward_x = (sin_y)
        forward_y = (-sin_x * cos_y)
        forward_z = (cos_x * cos_y)

        t_x = translation['X']
        t_y = translation['Y']
        t_z = translation['Z']

        self.normal = array([
                             [left_x, left_y, left_z],
                             [up_x, up_y, up_z],
                             [forward_x, forward_y, forward_z]
        ], dtype=float32)

        left_x *= scale['X']
        left_y *= scale['X']
        left_z *= scale['X']

        up_x *= scale['Y']
        up_y *= scale['Y']
        up_z *= scale['Y']

        forward_x *= scale['Z']
        forward_y *= scale['Z']
        forward_z *= scale['Z']

        self.matrix = array([
                             [left_x, left_y, left_z, 0.0],
                             [up_x, up_y, up_z, 0.0],
                             [forward_x, forward_y, forward_z, 0.0],
                             [t_x, t_y, t_z, 1.0]
        ], dtype=float32)
