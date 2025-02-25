from OpenGL import GL
import numpy as np
from queue import Queue
from .object import DescriptorMixin
from .shader import Program, StaticProgram
from .texture import Texture
from .buffer.vertex_array import VertexArray
from .buffer.buffer_pointer import BufferPointer
from .buffer.buffer import TextureBuffer, VertexBuffer

class DrawCall(DescriptorMixin):
    
    def __init__(self,
                 program: Program | StaticProgram,
                 indices=None,
                 primitive=GL.GL_TRIANGLES,
                 initial_data: np.ndarray | list = None):
        self._properties = set([])
        self._program = program
        self._vbo = None
        self.primitive = primitive
        self.indices = indices
        self._vertex_array = None 
        self._dirty = True
        self.data = bytearray()
        if initial_data.any():
            self.add_data(initial_data)
    
    def __del__(self):
        if self._vbo is not None:
            del self._vbo
        if self._vertex_array is not None:
            del self._vertex_array

    def add_data(self, data: np.ndarray | list):
        if isinstance(data, list):
            data = np.array(data)
        self.data.extend(data.tobytes())
        self._dirty = True

    def __setattr__(self, name, value):
        if name[0] != '_':
            self._properties.add(name)
        object.__setattr__(self, name, value)

    def __delattr__(self, name):
        if name in self._properties:
            del self._properties[name]
        object.__delattr__(self, name)

    def _build(self):
        if not self._vertex_array:
            self._vertex_array = VertexArray()
        else:
            self._vertex_array.clear()
        # assign our pointers to the vertex array
        if self._vbo is not None:
            del self._vbo
        data = self._program.format(np.frombuffer(self.data, dtype=np.uint8))
        self._vbo = VertexBuffer(data)
        for name, pointer in self._vbo.pointers.items():
            if not isinstance(pointer, BufferPointer):
                raise ValueError('Must be a buffer pointer')
            attribute = self._program.attributes.get(name)
            if attribute:
                self._vertex_array[attribute.location] = pointer
        self._dirty = False

    def _set_uniforms(self, **uniforms):
        for name, value in uniforms.items():
            if hasattr(self._program, name):
                if isinstance(value, TextureBuffer):
                    value = value.texture
                if isinstance(value, Texture):
                    unit = getattr(self._program, name)
                    if unit is not None:
                        Texture.active_unit = unit
                        value.bind()
                else:
                    setattr(self._program, name, value)

    def draw(self, **uniforms):
        if self._dirty:
            self._build()
        self._set_uniforms(**uniforms)
        with self._program:
            properties = dict((name, getattr(self, name)) for name in self._properties)
            self._set_uniforms(**properties)
            if self.indices is not None:
                self._vertex_array.render_indices(self.indices, self.primitive)
            else:
                self._vertex_array.render(self.primitive)
            for name in self._properties:
                value = getattr(self, name)
                if isinstance(value, Texture):
                    unit = getattr(self._program, name)
                    if unit is not None:
                        Texture.active_unit = unit
                        value.unbind()