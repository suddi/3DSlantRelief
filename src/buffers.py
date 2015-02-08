from OpenGL.GL import (
                       glBindBuffer, glBufferData,
                       glDeleteBuffers,
                       glColorPointer, glEdgeFlagPointer, glIndexPointer,
                       glNormalPointer, glTexCoordPointer, glVertexPointer,
                       glEnableVertexAttribArray, glVertexAttribPointer,
                       GL_FALSE, GL_STATIC_DRAW
)
from OpenGL.arrays import ArrayDatatype as ADT

from pyglet.gl import (
                       glGenBuffers,
                       GL_ARRAY_BUFFER,
                       GLuint
)


class VertexBuffer(object):
    """
    Handle VertexBufferObjects of all types
    """

    def __init__(self, data, usage=GL_STATIC_DRAW):
        """
        Initiate the vertex buffer object on the CPU
        """
        self.buffer = GLuint(0)
        glGenBuffers(1, self.buffer)
        self.buffer = self.buffer.value

        glBindBuffer(GL_ARRAY_BUFFER, self.buffer)
        glBufferData(GL_ARRAY_BUFFER, ADT.arrayByteCount(data),
                     ADT.voidDataPointer(data), usage)

    def __del__(self):
        glDeleteBuffers(1, GLuint(self.buffer))

# ------------------------------------------------------------------
# BINDING MODULES
# ------------------------------------------------------------------

    def bind(self):
        glBindBuffer(GL_ARRAY_BUFFER, self.buffer)

    def unbind(self):
        glBindBuffer(GL_ARRAY_BUFFER, 0)

    def bind_attribute(self, attribute, size, var_type, stride=0):
        self.bind()
        glEnableVertexAttribArray(attribute)
        glVertexAttribPointer(attribute, size, var_type, GL_FALSE, stride,
                              None)

    def bind_colors(self, size, var_type, stride=0):
        self.bind()
        glColorPointer(size, var_type, stride, None)

    def bind_edgeflags(self, stride=0):
        self.bind()
        glEdgeFlagPointer(stride, None)

    def bind_indexes(self, var_type, stride=0):
        self.bind()
        glIndexPointer(var_type, stride, None)

    def bind_normals(self, var_type, stride=0):
        self.bind()
        glNormalPointer(var_type, stride, None)

    def bind_texcoords(self, size, var_type, stride=0):
        self.bind()
        glTexCoordPointer(size, var_type, stride, None)

    def bind_vertices(self, size, var_type, stride=0):
        self.bind()
        glVertexPointer(size, var_type, stride, None)


if __name__ == '__main__':
    # Run the experiment even without running it directly from main.py
    from main import run_experiment
    run_experiment()
