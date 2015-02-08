from OpenGL.error import GLError

from pyglet.gl import *


class ShaderError(Exception):
    pass


class CompileError(ShaderError):
    pass


class LinkError(ShaderError):
    pass


shader_errors = {
    GL_INVALID_VALUE: 'GL_INVALID_VALUE (bad 1st arg)',
    GL_INVALID_OPERATION: 'GL_INVALID_OPERATION '
        '(bad id or immediate mode drawing in progress)',
    GL_INVALID_ENUM: 'GL_INVALID_ENUM (bad 2nd arg)',
}


def load_source(fname):
    with open(fname) as fp:
        src = fp.read()
    return src


class _Shader(object):

    shader_type = None

    def __init__(self, files, *args, **kwargs):
        """
        Collect all the shaders that were passed and as such, files
        can be provided as a list or basestring
        """
        # Accept shader files as basestrings or lists
        if isinstance(files, basestring):
            self.files = [files]
        else:
            self.files = files

        # Initiate sources and id to None
        self.sources = None
        self.id = None

    def _get(self, paramId):
        outvalue = c_int(0)
        glGetShaderiv(self.id, paramId, byref(outvalue))
        value = outvalue.value
        if value in shader_errors.keys():
            msg = '%s from glGetShader(%s, %s, &value)'
            raise ValueError(msg % (shader_errors[value], self.id, paramId))
        return value

    def get_compile_status(self):
        return bool(self._get(GL_COMPILE_STATUS))

    def get_info_log_length(self):
        return self._get(GL_INFO_LOG_LENGTH)

    def get_info_log(self):
        length = self.get_info_log_length()
        if length == 0:
            return ''
        buf = create_string_buffer(length)
        glGetShaderInfoLog(self.id, length, None, buf)
        return buf.value

    def _sources_to_array(self):
        num = len(self.sources)
        all_source = (c_char_p * num)(*self.sources)
        return num, cast(pointer(all_source), POINTER(POINTER(c_char)))

    def _load_sources(self):
        return [load_source(fname) for fname in self.files]

    def compile(self):
        self.id = glCreateShader(self.shader_type)

        self.sources = self._load_sources()
        num, src = self._sources_to_array()
        glShaderSource(self.id, num, src, None)

        glCompileShader(self.id)

        if not self.get_compile_status():
            raise CompileError(self.get_info_log())


class VertexShader(_Shader):
    """
    VertexShader, subclass of _Shader, sets the shader_type to
    GL_VERTEX_SHADER
    """
    shader_type = GL_VERTEX_SHADER


class FragmentShader(_Shader):
    """
    FragmentShader, subclass of _Shader, sets the shader_type to
    GL_FRAGMENT_SHADER
    """
    shader_type = GL_FRAGMENT_SHADER


class ShaderProgram(object):
    """
    Creates the ShaderProgram
        1) Creates the OpenGL program on the GPU
        2) Attach the shaders to the OpenGL program
        3) Link the OpenGL program
        4) Set the OpenGL program to be used
    """

    def __init__(self, *args, **kwargs):
        """
        Initiate the ShaderProgram class
        """
        # Use the shaders provided by the argument to create the list
        # of shaders
        self.shaders = list(args)
        # Create the OpenGL shader program
        self.id = glCreateProgram()

    def _get(self, paramId):
        outvalue = c_int(0)
        glGetProgramiv(self.id, paramId, byref(outvalue))
        value = outvalue.value
        if value in shader_errors.keys():
            msg = '%s from glGetProgram(%s, %s, &value)'
            raise ValueError(msg % (shader_errors[value], self.id, paramId))
        return value

    def get_link_status(self):
        return bool(self._get(GL_LINK_STATUS))

    def get_info_log_length(self):
        return self._get(GL_INFO_LOG_LENGTH)

    def get_info_log(self):
        length = self.get_info_log_length()
        if length == 0:
            return ''
        buf = create_string_buffer(length)
        glGetProgramInfoLog(self.id, length, None, buf)
        return buf.value

    def _get_message(self):
        messages = []
        for shader in self.shaders:
            log = shader.get_info_log()
            if log:
                messages.append(log)
        log = self.get_info_log()
        if log:
            messages.append(log)
        return '\n'.join(messages)

    def use(self):
        """
        Enable the use of the previously created shaders
        """
        # Iterate through the shaders
        for shader in self.shaders:
            # Compile each shader
            shader.compile()
            # Attach the shader to OpenGL program
            glAttachShader(self.id, shader.id)

        glLinkProgram(self.id)

        # Handle if there is any errors in attaching the shaders or
        # linking the program
        message = self._get_message()
        if not self.get_link_status() and not 'No errors' in message:
            raise LinkError(message)

        # Set to use the OpenGL program and handle any errors if such
        # arise
        try:
            glUseProgram(self.id)
        except GLError:
            print glGetProgramInfoLog(self.id)
            raise

        return message
