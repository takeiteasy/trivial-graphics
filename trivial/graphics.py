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

import numpy as np

def mat4(dtype=None):
    return np.zeros((4, 4), dtype=dtype)

def identity(dtype=None):
    return np.identity(4, dtype=dtype)

def matmul(a, b):
    return np.dot(a, b)

def as_mat4(func):
    def wrapper(*args, **kwargs):
        mat = func(*args, **kwargs)
        mat4 = np.identity(4, dtype=kwargs.get('dtype', None))
        mat4[0:3, 0:3] = mat
        return mat4
    return wrapper

@as_mat4
def translation(vec, dtype=None):
    mat = identity(dtype)
    mat[3, 0:3] = vec[:3]
    return mat

@as_mat4
def xrotation(theta, dtype=None):
    cosT = np.cos(theta)
    sinT = np.sin(theta)
    return np.array([[ 1.0, 0.0, 0.0 ],
                     [ 0.0, cosT,-sinT ],
                     [ 0.0, sinT, cosT ]],
                     dtype=dtype)

@as_mat4
def yrotation(theta, dtype=None):
    cosT = np.cos(theta)
    sinT = np.sin(theta)
    return np.array([[ cosT, 0.0,sinT ],
                     [ 0.0, 1.0, 0.0 ],
                     [-sinT, 0.0, cosT ]],
                     dtype=dtype)

@as_mat4
def zrotation(theta, dtype=None):
    cosT = np.cos(theta)
    sinT = np.sin(theta)
    return np.array([[ cosT,-sinT, 0.0 ],
                     [ sinT, cosT, 0.0 ],
                     [ 0.0, 0.0, 1.0 ]],
                     dtype=dtype)

def rotation(vec, dtype=None):
    rot_x = xrotation(vec[0], dtype=dtype)
    rot_y = yrotation(vec[1], dtype=dtype)
    rot_z = zrotation(vec[2], dtype=dtype)
    return rot_x @ rot_y @ rot_z


def scale(scale, dtype=None):
    if isinstance(scale, float) or isinstance(scale, int):
        scale = [scale, scale, scale]
    m = np.diagflat([scale[0], scale[1], scale[2], 1.0])
    if dtype:
        m = m.astype(dtype)
    return m

def transpose(mat):
    return np.transpose(mat)

def invert(mat):
    return np.linalg.inv(mat)