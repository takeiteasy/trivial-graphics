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
from .object import DescriptorMixin
from .buffer.vertex_array import VertexArray
from .buffer.buffer_pointer import BufferPointer

class Mesh(DescriptorMixin):
    def __init__(self, pipeline, indices=None, primitive=GL.GL_TRIANGLES, **pointers):
        self._pointers = pointers
        self._pipeline = pipeline
        self.primitive = primitive
        self.indices = indices

        for pointer in pointers.values():
            if not isinstance(pointer, BufferPointer):
                raise ValueError('Must be of type BufferPointer')

        self._vertex_array = VertexArray()
        self._bind_pointers()

    def _bind_pointers(self):
        # TODO: make this more efficient, don't just clear all pointers
        self._vertex_array.clear()

        # assign our pointers to the vertex array
        for name, pointer in self._pointers.items():
            if not isinstance(pointer, BufferPointer):
                raise ValueError('Must be a buffer pointer')

            attribute = self._pipeline.program.attributes.get(name)
            if attribute:
                self._vertex_array[attribute.location] = pointer

    def draw(self, **uniforms):
        # set our uniforms
        self._pipeline.set_uniforms(**uniforms)

        # render
        with self._pipeline:
            if self.indices is not None:
                self._vertex_array.render_indices(self.indices, self.primitive)
            else:
                self._vertex_array.render(self.primitive)

    @property
    def pipeline(self):
        return self._pipeline

    @pipeline.setter
    def pipeline(self, pipeline):
        self._pipeline = pipeline
        self._bind_pointers()

    @property
    def vertex_array(self):
        return self._vertex_array