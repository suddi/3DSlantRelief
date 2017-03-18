from PIL.Image import fromarray
from PIL.ImageFilter import Filter

from math import pi

from numpy import ndarray, uint8

from OpenGL.GL import (
                       glGetString,
                       GL_VERSION, GL_SHADING_LANGUAGE_VERSION, GL_VENDOR,
                       GL_RENDERER,
)

from settings import WIDTH, HEIGHT


class GaussianBlur2(Filter):
    """
    GaussianBlur is implemented incorrectly in the PIL ImageFilter library
    The radius of the GaussianBlur cannot be changed in the original
    implementation
    """
    name = "GaussianBlur"

    def __init__(self, radius=2):
        """
        Set the radius if provided, else use 2
        This is where the original implementation fails
        radius is set to 2 regardless of input
        """
        self.radius = radius

    def filter(self, image):
        """
        Apply Gaussian Blurring as provided by the PIL library
        """
        return image.gaussian_blur(self.radius)


# ------------------------------------------------------------------
# GENERAL TESTING FUNCTIONS
# ------------------------------------------------------------------

def opengl_info():
    """
    Print out information relating to OpenGL, such as the version of
    OpenGL and the OpenGL Shading Language being used, the vendor and
    renderer
    """
    print "OpenGL version:\t\t%s" % glGetString(GL_VERSION)
    print "GLSL version:\t\t%s" % glGetString(GL_SHADING_LANGUAGE_VERSION)
    print "Vendor:\t\t\t%s" % glGetString(GL_VENDOR)
    print "Renderer:\t\t%s" % glGetString(GL_RENDERER)


def save_to_file(filename, content):
    """
    Save to ".txt", the image matrix or other string
    """
    # Append ".txt" to filename if not present
    filename = append_type(filename, '.txt')
    with open(filename, 'w') as f:
        # Check if image matrix is being passed or plain text
        if isinstance(content, ndarray):
            for i in content:
                for j in i:
                    f.write(str(j))
                f.write('\n')
        else:
            f.write(str(content))


def save_to_image(filename, img):
    """
    Save to ".jpg", the image
    """
    # Append ".jpg" to filename if not present
    filename = append_type(filename, '.jpg')

    # If img is numpy array, convert it to PIL image
    if isinstance(img, ndarray):
        img = fromarray(uint8(img))
    # Convert the image as necessary
    if not img.mode == 'L':
        img = img.convert('L')
    img.save(filename, 'jpeg')


def append_type(filename, filetype):
    """
    Append the filetype if it is not present
    """
    if not filename[-4:] == filetype:
        filename += filetype
    return filename


def get_coords(X, Y, scaleX, scaleY):
    """
    Helper module to calculate the normalized coordinates
    for the texture coordinates: glMultiTexCoord2f and the
    vertices: glVertex2f
    """
    x = X / float(WIDTH)
    y = Y / float(HEIGHT)

    # Use convert_scale
    [vertX, vertY] = convert_scale(x, y)
    [vertX, vertY] = [vertX * scaleX, vertY * scaleY]
    return [x, y, vertX, vertY]


def convert_scale(*args):
    """
    Convert any arguments passed on a 0.0 - 1.0 scale to a
    -1.0 - 1.0 scale
    """
    # To store the results
    result = []
    # Run through the arguments
    for arg in args:
        # Print error if argument passed does not form to the correct scale
        if 0.0 > arg or arg > 1.0:
            print 'ERROR: Arguments passed to tools.convert_scale must ' +\
                  'be on a scale of 0.0 - 1.0. Received: %s' % arg
            continue
        # Convert number to 4 decimal places
        arg = round((arg - 0.5) * 2, 4)
        result.append(arg)
    return result


def pixel_access(image):
    """
    Get access to the pixel data to be able to render the OpenGL
    texture
    """
    # Access raw pixel data of the image
    rawimage = image.get_image_data()

    # Set format of image data
    fmat = 'RGBA'
    # Calculate the pitch
    pitch = rawimage.width * len(fmat)
    # Return the pixel by pixel data for the rawimage
    return rawimage.get_data(fmat, pitch)


def get_time(start, end):
    return round(end - start, 4)


def deg_to_rad(degrees):
    """
    Converts value passed in degrees into radians
    """
    # Return value in radians
    return (degrees * pi) / 180


if __name__ == "__main__":
    import doctest
    doctest.testmod()
