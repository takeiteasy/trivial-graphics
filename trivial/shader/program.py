# Forked by George Watson (https://github.com/takeiteasy)
# Copyright (c) 2025.
# All rights reserved.
#
# trivial-graphics
#
# Copyright (C) 2025  George Watson
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# Original license:
#
# Created by Adam Griffiths (https://github.com/adamlwgriffiths)
#
# Copyright (c) 2015.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met: 
#
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer. 
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution. 
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# The views and conclusions contained in the software and documentation are those
# of the authors and should not be interpreted as representing official policies, 
# either expressed or implied, of the FreeBSD Project.

from OpenGL import GL
import numpy as np
from .variables import ProgramVariable, Attribute, Uniform
from ..object import ManagedObject, UnmanagedObject, BindableObject, DescriptorMixin
from ..proxy import Integer32Proxy
from ..proxy import Proxy
from .stage import Stage, VertexStage, FragmentStage
from .shader import Shader, VertexShader, FragmentShader, WrappedShader

type ShaderSource = Shader | Stage

"""
TODO: https://www.opengl.org/registry/specs/ARB/separate_shader_objects.txt
TODO: https://www.opengl.org/registry/specs/ARB/shading_language_include.txt
TODO: https://www.opengl.org/registry/specs/ARB/sampler_objects.txt
"""

class ProgramProxy(Proxy):
    def __init__(self, property, dtype=None):
        super(ProgramProxy, self).__init__(
            getter=GL.glGetProgramiv, getter_args=[property],
            dtype=dtype, prepend_args=['_handle'],
        )


class VariableStore(DescriptorMixin, dict):
    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError as e:
            raise AttributeError(e)

    def __setattr__(self, name, value):
        self[name] = value

    def __setitem__(self, index, value):
        if not isinstance(value, ProgramVariable):
            raise ValueError('Attempted to set to a non-ProgramVariable, use the ProgramVariable.data setter instead')
        super(VariableStore, self).__setitem__(index, value)


class Program(DescriptorMixin, BindableObject, ManagedObject):
    _create_func = GL.glCreateProgram
    _delete_func = GL.glDeleteProgram
    _bind_func = GL.glUseProgram
    _current_program = Integer32Proxy(GL.GL_CURRENT_PROGRAM, bind=False)

    active_attribute_max_length = ProgramProxy(GL.GL_ACTIVE_ATTRIBUTE_MAX_LENGTH)
    active_attributes = ProgramProxy(GL.GL_ACTIVE_ATTRIBUTES)
    active_uniform_max_length = ProgramProxy(GL.GL_ACTIVE_UNIFORM_MAX_LENGTH)
    active_uniforms = ProgramProxy(GL.GL_ACTIVE_UNIFORMS)
    link_status = ProgramProxy(GL.GL_LINK_STATUS, dtype=np.bool)
    delete_status = ProgramProxy(GL.GL_DELETE_STATUS, dtype=np.bool)

    def __init__(self, shaders: list[ShaderSource], frag_locations: str | dict[str, int] | list[str] = None):
        super(Program, self).__init__()
        self._uniforms = {}
        self._attributes = {}
        self._loaded = False

        for i, shader in enumerate(shaders):
            if isinstance(shader, Stage):
                if isinstance(shader, VertexStage):
                    shader = VertexShader(shader)
                elif isinstance(shader, FragmentStage):
                    shader = FragmentShader(shader)
                else:
                    assert False
            if isinstance(shader, Shader):
                if isinstance(shader, VertexShader):
                    self._attributes = shader.attributes
                    self._uniforms |= shader.uniforms
                elif isinstance(shader, FragmentShader):
                    self._uniforms |= shader.uniforms
                else:
                    assert False
            else:
                raise ValueError("Invalid Shader type")
            self._attach(shader)
            shaders[i] = shader

        if frag_locations:
            if isinstance(frag_locations, str):
                frag_locations = {frag_locations: 0}
            if isinstance(frag_locations, list):
                frag_locations = { k: i for i, k in enumerate(frag_locations) }
            for name, number in frag_locations:
                self._set_frag_location(name, number)
        self._link()

        if self._attributes:
            store = VariableStore()
            for i, _ in enumerate(self._attributes.items()):
                attr = Attribute(self, i, self.active_attribute_max_length)
                store[attr.name] = attr
                self.__dict__[attr.name] = attr
                GL.glBindAttribLocation(self._handle, i, attr.name)
            self.__dict__['_attributes'] = store

        if self._uniforms:
            store = VariableStore()
            for i, (name, type) in enumerate(self._uniforms.items()):
                uniform = Uniform(self,
                                  i,
                                  self.active_uniform_max_length)
                store[name] = uniform
                self.__dict__[uniform.name] = uniform
            self.__dict__['_uniforms'] = store

        for shader in shaders:
            self._detach(shader)
        self._loaded = True

    @property
    def attributes(self):
        return self._attributes

    @property
    def uniforms(self):
        return self._uniforms

    def __getattr__(self, name):
        # noinspection PyBroadException
        try:
            if self._loaded:
                stores = [self.__dict__['_uniforms'], self.__dict__['_attributes']]
                for store in stores:
                    if name in store:
                        return store[name.encode("utf-8")].__get__(store, store.__class__)
        except Exception as e:
            pass
        raise AttributeError

    def __setattr__(self, name, value):
        return super(Program, self).__setattr__(name, value)

    def _attach(self, shader):
        GL.glAttachShader(self._handle, shader.handle)

    def _detach(self, shader):
        GL.glDetachShader(self._handle, shader.handle)

    def _link(self):
        GL.glLinkProgram(self._handle)
        if not self.link_status:
            raise ValueError(self.log)
        # linking sets the program as active
        # ensure we unbind the program
        self.unbind()
    
    def format(self, data: np.ndarray):
        def convert_dtype(dt):
            if dt == np.dtype('float32'):
                return np.float32
            elif dt == np.dtype('int32'):
                return np.int32
            elif dt == np.dtype('uint32'):
                return np.uint32
            elif dt == np.dtype('float64'):
                return np.float64
            return dt
        # Sort by OpenGL attribute locations
        return data.view(dtype=sorted([(k, convert_dtype(v.dtype), v.dimensions[0]) for k, v in self._attributes.items()], key=lambda x: getattr(self, x[0])))

    @property
    def valid(self):
        return bool(GL.glValidateProgram(self._handle))

    @property
    def log(self):
        return GL.glGetProgramInfoLog(self._handle)

    def _set_frag_location(self, name, number):
        GL.glBindFragDataLocation(self._handle, number, name)

class UnmanagedProgram(Program, UnmanagedObject):
    pass

class StaticProgram:
    version = "330 core"
    vertex_source = None
    vertex_functions = None
    fragment_source = None
    fragment_functions = None
    id = None

    @classmethod
    def __init__(cls):
        if not cls.id:
            p = UnmanagedProgram([VertexStage(cls.vertex_source,
                                              version=cls.version,
                                              library=cls.vertex_functions),
                                  FragmentStage(cls.fragment_source,
                                                version=cls.version,
                                                library=cls.fragment_functions)])
            cls.id = p.handle

    @classmethod
    def valid(cls):
        return id is not None and bool(GL.glValidateProgram(cls.id))

    def __int__(self):
        return self.__class__.id

    @classmethod
    def delete(cls):
        if cls.id:
            GL.glDeleteProgram(cls.id)
            cls.id = None