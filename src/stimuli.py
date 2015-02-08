from Image import open as img_open

from pyglet.image import load
from pyglet.resource import texture

from random import randint, shuffle

from settings import (
                      # FILENAMES,
                      COLORMAPS, HEIGHTMAPS, NORMALMAPS,
                      # GAUSSIAN_BLURS,
                      STIMULI_REPETITION, PRACTICE_STIMULI,
                      # PREPROCESSED_IMAGES,
                      HEIGHT_RATIO, POSSIBLE_SLANTS,
                      STIMULI_ONLY, WIDTH, HEIGHT
)

# The Gaussian Blur provided by PIL only allows for a radius of 2
# thus I have implemented my own version of Gaussian Blur in tools
# from tools import GaussianBlur2
# from tools import pixel_access
# from tools import save_to_file


class Stimuli(object):
    """
    Load the voronoi image stimuli and heightmap in order to create
    the stimuli

    NOTE: All colormaps are preloaded but the heightmaps are loaded
    as required
    """

# ------------------------------------------------------------------
# HANDLE INITIALIZATION
# ------------------------------------------------------------------

    # def __init__(self, *args, **kwargs):
        #  """
        # If the images have not been processed and made into heightmaps,
        # Stimuli will take care of it during the initialization
        # """
        # If the images have not had blurred renderings made for them,
        # we can make it at this stage in the pipeline
        # if not PREPROCESSED_IMAGES:
            # Create blurred imaged with varying radii
            # self.__blur_images()
            # Handle any situation if it arises in future that the
            # initialization module is called again

    def setup(self, practice=False):
        """
        Load up all the unique stimuli into memory

        NOTE: This does not include heightmaps
        """
        # MULTIPLE STIMULI IMAGES
        # Load up all the images that will be used as colormaps
        # We will store the colormaps in self.colormaps
        # self.colormap = []
        # Iterating through the filenames
        # for filename in FILENAMES:
            # Load the image and store it in memory
            # self.colormap.append(load(filename))

        # SINGLE STIMULI IMAGE
        self.colormap = COLORMAPS

        # Store the number of stimuli available
        self.num_maps = len(COLORMAPS)

        self.heightmap = HEIGHTMAPS
        self.normalmap = NORMALMAPS

        self.colormap = self.__load_image(self.colormap)
        self.heightmap = self.__load_image(self.heightmap)
        self.normalmap = self.__load_image(self.normalmap)

        # print self.colormap, self.heightmap, self.normalmap

        if STIMULI_ONLY:
            self.states = [self.__run_block]
            self.order = [self.__random_stimuli(), None]
        else:
            # Declare possible action states for Stimuli
            self.states = [
                          # This would handle the practice
                          self.__prepare_practice, self.__run_block,
                          # This would handle the experiment
                          self.__prepare_exp, self.__run_block,
                          # This would signify the end of stimuli and end of
                          # the experiment, this will be used to set run_state
                          None
            ]
            # Check if practice is not required
            if not practice:
                # Pop out the first two elements which are the practice blocks
                self.states.pop(0)
                self.states.pop(0)
        # Set the first run state to be used
        self.run_state = self.states.pop(0)

    def __blur_images(self):
        """
        Blur all the provided images and save the blurred image to file
        """
        # Iterating through the images provided in settings
        # for filename in FILENAMES:
            # Open the image
            # img = img_open(filename)
            # Select radius for Gaussian Blur
            # for radius in GAUSSIAN_BLURS:
                # gblur = GaussianBlur2(radius)
                # Apply the blur
                # temp_img = img.filter(gblur)
                # Save to file
                # temp_img.save(self.__blur_imagename(filename, radius))

    def __blur_imagename(self, filename, radius):
        """
        Return the filename for the Gaussian Blurred image
        """
        return '%s_gblur%d.jpg' % (filename[:-4], radius)

    def __load_image(self, imgs):
        maps = []

        # Iterating through the filenames
        for img in imgs:
            # Load the image and store it in memory
            maps.append(load(img))

        return maps

    def __load_pixel(self, imgs):
        maps = []
        fmat = 'RGB'
        pitch = WIDTH * len(fmat)

        for img in imgs:
            img_pil = img_open(img)
            img_pyglet = load(img)
            pixels = img_pil.load()

            all_pixels = []
            for x in range(WIDTH):
                for y in range(HEIGHT):
                    all_pixels.append(pixels[x, y])

            img_pyglet.set_data(fmat, pitch, all_pixels)
            maps.append(img_pyglet)

        return maps

# ------------------------------------------------------------------
# HANDLE STIMULI STATES
# ------------------------------------------------------------------
    def __prepare_practice(self):
        """
        Prepare the stimuli for the practice block
        """
        # This will house the order in which stimuli are to be called
        # in the practice block
        self.order = []
        # For all the practice stimuli required, choose an image for
        # stimuli
        for i in range(0, PRACTICE_STIMULI):
            self.order.append(self.__random_stimuli())

        # Set the next action state
        self.run_state = self.states.pop(0)

    def __run_block(self):
        """
        Load the heightmap image as the final step in stimuli preparation
        before rendering
        """
        # If empty
        if not self.order:
            # Set the next action state
            self.run_state = self.states.pop(0)
            # Return false as the practice block is now complete
            return False
        # If not empty
        else:
            # Move onto the next stimuli
            self.current = self.order.pop(0)

        # MULTIPLE STIMULI IMAGES
        # Randomly select a variation of Guassian Blurred images
        # num = randint(0, len(GAUSSIAN_BLURS) - 1)
        # Select the radius of the blur requested
        # num = GAUSSIAN_BLURS[num]
        # Get the filename of the blurred image
        # filename = self.__blur_imagename(FILENAMES[self.current], num)
        # Load the heightmap image to be used next
        # self.heightmap = load(filename)

        # Return true and continue with the practice block
        return True

    def __prepare_exp(self):
        """
        Prepare the stimuli for the experimental block
        """
        # This will house the order in which stimuli are to be called
        # in the experimental block
        self.order = []

        temp_order = []
        for i in range(0, self.num_maps):
                for j in range(0, len(HEIGHT_RATIO)):
                    for k in range(0, len(POSSIBLE_SLANTS)):
                        temp_order.append((i, HEIGHT_RATIO[j],
                                          POSSIBLE_SLANTS[k]))

        for i in range(0, STIMULI_REPETITION):
            self.order += temp_order

        # print self.order
        shuffle(self.order)
        shuffle(self.order)
        shuffle(self.order)
        # self.__print_order()
        # print len(self.order)
        # print self.order

        # Figure out if further stimuli are needed
        # diff = EXP_STIMULI - len(self.order)
        # if diff:
            # For the additional experimental stimuli required,
            # choose an image as stimuli
            # for i in range(0, diff):
                # self.order.append(randint(0, self.num_maps - 1))

        # Set the next action state
        self.run_state = self.states.pop(0)

    def __random_stimuli(self):
        stimuli = randint(0, self.num_maps - 1)
        j = randint(0, len(HEIGHT_RATIO) - 1)
        k = randint(0, len(POSSIBLE_SLANTS) - 1)
        return (stimuli, HEIGHT_RATIO[j], POSSIBLE_SLANTS[k])

    def __print_order(self):
        print 'There are %d stimuli to be presented and the order will be as follows:'\
              % len(self.order)
        print 'IMAGE\tHEIGHT_RATIO\tSLANT'
        for img, height_ratio, slant in self.order:
            print '%s\t%s\t\t%s' % (img, height_ratio, slant)

# ------------------------------------------------------------------
# DEPRECATED MODULES
# ------------------------------------------------------------------

    # def __filterBlur(self):
        # """
        # Apply blurring to the image
        # """
        # gblur = GaussianBlur2(2)
        # return self.img.filter(gblur)

    # def __depthMap(self, mat):
        # """
        # Produce displacement map from image matrix
        # """
        # Create empty matrix with image width and height
        # zmap = numpy.zeros((self.width, self.height), dtype=numpy.int)
        # Iterate through the image matrix
        # for i in range(0, self.width):
            # for j in range(0, self.height):
                # block = [
                            # mat[j, i],
                            # mat[j, (i + 1) % self.width],
                            # mat[(j + 1) % self.height, i],
                            # mat[(j + 1) % self.height, (i + 1) % self.width]
                # ]

                # zmap[j, i] = min(block)
        # return zmap

    # def __tileImage(self, img):
        # """
        # Tile the image as necessary to fit the resolution of the
        # monitor
        # """
        # Assign the image size
        # w = img.size[0]
        # h = img.size[1]

        # WILL WORK ON WINDOWS ONLY
        # Use ctypes.windll.user32 to get the screen resolution
        # user32 = ctypes.windll.user32
        # screensize = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)

        # Calculate screensize divided by image width and height to
        # figure out which is the larger value, then use the ceiling
        # integer value to create a square tiled image
        # size = max((float(screensize[0]) / w), (float(screensize[1]) / h))
        # size = int(numpy.ceil(size))

        # Create empty image
        # tile = Image.new('L', (size * w, size * h))

        # Paste in tiles into empty image
        # for i in range(0, size):
            # for j in range(0, size):
                # tile.paste(img, (i * w, j * h))

        # return tile


if __name__ == '__main__':
    # Run the experiment even without running it directly from main.py
    from main import run_experiment
    run_experiment()
