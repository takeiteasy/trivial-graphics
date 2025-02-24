from typing import override, Callable, Any, TypeVar, Generic
from OpenGL import GL
from OpenGL.raw.GL.VERSION import GL_2_0
import numpy as np
from ..object import ManagedObject
from ..proxy import Proxy
from pyglsl import VertexStage, FragmentStage, Stage
import re
import textwrap

class ShaderProxy(Proxy):
    def __init__(self, property, dtype=None):
        super(ShaderProxy, self).__init__(
            getter=GL.glGetShaderiv, getter_args=[property],
            dtype=dtype, prepend_args=['_handle']
        )


class ShaderError(object):
    parsers = [
        # ATI
        # ERROR: 0:131: '{' : syntax error parse error
        re.compile(r'(?P<type>\w+):\s+(\d+):(?P<line>\d+):\s+(?P<description>.*)', flags=re.I),
        # Nvidia
        # 0(7): error C1008: undefined variable "MV"
        re.compile(r'\d+(?P<line>\d+):\s+(?P<type>\w)\s+\w:\s+(?P<description>.*)', flags=re.I),
        # Nouveau
        # 0:28(16): error: syntax error, unexpected ')', expecting '('
        re.compile(r'\d+:\d+\((?P<line>\d+)\):\s+(?P<type>\w):\s+(?P<description>.*)', flags=re.I),
    ]

    @classmethod
    def parse(cls, shader, source, log):
        def p(error, src):
            cls_name = shader.__class__.__name__
            for parser in cls.parsers:
                match = parser.match(error)
                if match:
                    t = match.group('type').lower()
                    description = match.group('description')
                    line_number = int(match.group('line'))
                    line_source = src[line_number - 1]
                    return cls(cls_name, description, t, line_number, line_source)
            # unable to parse error, please file a bug!
            print('Unable to determine error format, please file a bug!')
            return cls(cls_name, error)
        source = source.split('\n')
        lines = log.strip().split('\n')
        errors = [p(line, source) for line in lines if line]
        return errors

    def __init__(self, cls, description, type='Error', line_number=-1, line_source=''):
        self.cls = cls
        self.type = type
        self.description = description
        self.line = line_number
        self.source = line_source

    def __str__(self):
        args = {
            'cls': self.cls,
            'type': self.type.title(),
            'description': self.description,
            'line': self.line,
            'source': self.source.strip(),
        }
        return textwrap.dedent(
            """
            Class:\t{cls}
            {type}:\t{description}
            Line:\t{line}
            Source:\t{source}
            """.format(**args)
        )

class ShaderException(Exception):
    def __init__(self, source: str, log: str):
        self.message = '\n'.join(map(lambda x: str(x), ShaderError.parse(self, source, log)))

class Shader(ManagedObject):
    _create_func = GL.glCreateShader
    _delete_func = GL.glDeleteShader

    compile_status = ShaderProxy(GL.GL_COMPILE_STATUS, dtype=np.bool)
    delete_status = ShaderProxy(GL.GL_DELETE_STATUS, dtype=np.bool)
    source_length = ShaderProxy(GL.GL_SHADER_SOURCE_LENGTH)

    @classmethod
    def open(cls, filename):
        with open(filename, 'r') as f:
            source = f.read()
            return cls(source)

    def __init__(self, source):
        super().__init__()
        self._set_source(source)
        self._compile()

    def _set_source(self, source):
        GL.glShaderSource(self._handle, source)

    def _compile(self):
        GL.glCompileShader(self._handle)
        if not self.compile_status:
            log = self.log
            errors = ShaderError.parse(self, self.source, log)
            string = '\n'.join(map(lambda x: str(x), errors))
            raise ValueError(string)

    @property
    def log(self):
        return GL.glGetShaderInfoLog(self._handle)

    @property
    def source(self):
        # BUG IN PYOPENGL!
        #   OpenGL/GL/VERSION/GL_2_0.py", line 356, in glGetShaderSource
        #   length = int(glGetShaderiv(obj, GL_OBJECT_SHADER_SOURCE_LENGTH))
        #   NameError: global name 'GL_OBJECT_SHADER_SOURCE_LENGTH' is not defined
        #return GL.glGetShaderSource(self._handle)

        # use the non-wrapped version
        length = self.source_length
        size = (GL.constants.GLint)()
        source = (GL.constants.GLchar * length)()
        GL_2_0.glGetShaderSource(self._handle, length, size, source)
        return source.value

ShaderStage = TypeVar("ShaderStage", bound=None)

class WrappedShader(Shader, Generic[ShaderStage]):
    @override
    def __init__(self, source: str | ShaderStage | Callable[..., Any]):
        self._attributes = {}
        self._uniforms = {}
        super().__init__(source)

    @property
    def attributes(self):
        return self._attributes

    @property
    def uniforms(self):
        return self._uniforms

    @override
    def _set_source(self, source):
        if not source:
            raise ValueError("Shader source empty")
        if isinstance(source, Stage):
            GL.glShaderSource(self._handle, source.compile())
        elif callable(source):
            stage = self.__class__.__orig_bases__[0].__args__[0]
            if stage is VertexStage:
                GL.glShaderSource(self._handle, VertexStage(source).compile())
            elif stage is FragmentStage:
                GL.glShaderSource(self._handle, FragmentStage(source).compile())
            else:
                raise ValueError("Invalid Shader source")
        elif isinstance(source, str):
            GL.glShaderSource(self._handle, source)
        else:
            raise ValueError("Invalid Shader source type")

    @override
    def _compile(self):
        Shader._compile(self)
        source = self.source.decode('utf-8')
        self._attributes = {}
        for line in source.split('\n'):
            p = [x for x in line.lstrip().split(' ') if x]
            if p:
                if p[0] == "in" or p[0].startswith("layout"):
                    self._attributes[p[-1][:-1]] = p[-2]
                elif p[0] == "uniform":
                    self._uniforms[p[-1][:-1]] = p[-2]

class VertexShader(WrappedShader[VertexStage]):
    _type = GL.GL_VERTEX_SHADER
    _shader_bit = GL.GL_VERTEX_SHADER_BIT

class FragmentShader(WrappedShader[FragmentStage]):
    _type = GL.GL_FRAGMENT_SHADER
    _shader_bit = GL.GL_FRAGMENT_SHADER_BIT

class GeometryShader(Shader):
    _type = GL.GL_GEOMETRY_SHADER
    _shader_bit = GL.GL_GEOMETRY_SHADER_BIT

class TesseleationControlShader(Shader):
    _type = GL.GL_TESS_CONTROL_SHADER
    _shader_bit = GL.GL_TESS_CONTROL_SHADER_BIT

class TesselationEvaluationShader(Shader):
    _type = GL.GL_TESS_EVALUATION_SHADER
    _shader_bit = GL.GL_TESS_EVALUATION_SHADER_BIT

class ComputeShader(Shader):
    _type = GL.GL_COMPUTE_SHADER
    _shader_bit = GL.GL_COMPUTE_SHADER_BIT
