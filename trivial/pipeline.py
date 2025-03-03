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

from .object import DescriptorMixin, BindableObject
from .texture import Texture
from .buffer import TextureBuffer
import numpy as np

class Pipeline(DescriptorMixin, BindableObject):
    def __init__(self, program, **properties):
        self._program = program
        self._properties = set(properties.keys())
        for name, value in properties.items():
            setattr(self, name, value)

    def __setattr__(self, name, value):
        if name[0] is not '_':
            self._properties.add(name)
        object.__setattr__(self, name, value)

    def __delattr__(self, name):
        if name in self._properties:
            del self._properties[name]
        object.__delattr__(self, name)

    def bind(self):
        # set our local properties as uniforms
        # bind the textures
        uniforms = dict((name, getattr(self, name)) for name in self._properties)
        self.set_uniforms(**uniforms)
        # bind our shader
        self._program.bind()

    def unbind(self):
        # unbind the textures
        for name in self._properties:
            value = getattr(self, name)
            if isinstance(value, Texture):
                unit = getattr(self._program, name)
                if unit is not None:
                    Texture.active_unit = unit
                    value.unbind()
        # unbind the shader
        self._program.unbind()

    def set_uniforms(self, **uniforms):
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

    @property
    def program(self):
        return self._program

    @property
    def properties(self):
        return dict((name, getattr(self, name)) for name in self._properties)
    
    def format(self, data: np.ndarray):
        return self._program.format(data)