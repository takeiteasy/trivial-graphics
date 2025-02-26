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

class DataType(object):
    def __init__(self, integer, signed, np_type, gl_type, gl_enum, basic_type, char_code=None):
        self._integer = integer
        self._signed = signed
        self._np_type = np_type
        self._gl_type = gl_type
        self._gl_enum = gl_enum
        self._char_code = char_code
        self._basic_type = basic_type

    @property
    def dtype(self):
        return self._np_type

    @property
    def gl_type(self):
        return self._gl_type

    @property
    def gl_enum(self):
        return self._gl_enum

    @property
    def char_code(self):
        return self._char_code

boolean = DataType(True, True, np.bool, GL.constants.GLbyte, GL.GL_BOOL, bool)
int8 = DataType(True, True, np.int8, GL.constants.GLbyte, GL.GL_BYTE, int, 'b')
uint8 = DataType(True, False, np.uint8, GL.constants.GLubyte, GL.GL_UNSIGNED_BYTE, int, 'ub')
int16 = DataType(True, True, np.int16, GL.constants.GLshort, GL.GL_SHORT, int)
uint16 = DataType(True, False, np.uint16, GL.constants.GLushort, GL.GL_UNSIGNED_SHORT, int)
int32 = DataType(True, True, np.int32, GL.constants.GLint, GL.GL_INT, int, 'i')
uint32 = DataType(True, False, np.uint32, GL.constants.GLuint, GL.GL_UNSIGNED_INT, int, 'ui')
int64 = DataType(True, True, np.uint64, GL.constants.GLuint64, GL.GL_UNSIGNED_INT64, int, 'l')
uint64 = DataType(True, False, np.uint64, GL.constants.GLuint64, GL.GL_UNSIGNED_INT64, int, 'ul')
float16 = DataType(False, True, np.float16, GL.constants.GLhalfARB, GL.GL_HALF_NV, float, 'f16')
float32 = DataType(False, True, np.float32, GL.constants.GLfloat, GL.GL_FLOAT, float, 'f')
float64 = DataType(False, True, np.float64, GL.constants.GLdouble, GL.GL_DOUBLE, float, 'd')

data_types = [boolean, int8, uint8, int16, uint16, int32, uint32, int64, uint64, float16, float32, float64]

def for_enum(enum):
    return dict((int(dtype.gl_enum), dtype) for dtype in data_types)[int(enum)]

def for_code(code):
    return dict((str(dtype.char_code), dtype) for dtype in data_types)[str(code)]

def for_dtype(dtype):
    if isinstance(dtype, np.dtype):
        # handle subdtypes being converted to np.void
        if dtype.subdtype:
            dtype = dtype.subdtype[0]
        else:
            dtype = dtype.type
    return dict((dtype.dtype, dtype) for dtype in data_types)[dtype] # type: ignore
