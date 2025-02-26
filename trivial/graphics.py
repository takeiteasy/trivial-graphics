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

import numpy as np
from enum import Enum
from contextlib import contextmanager

def _mat4(dtype=None):
    return np.zeros((4, 4), dtype=dtype)

def _identity(dtype=None):
    return np.identity(4, dtype=dtype)

def _matmul(a, b):
    return np.dot(a, b)

def as_mat4(func):
    def wrapper(*args, **kwargs):
        mat = func(*args, **kwargs)
        if mat.shape == (3, 3,):
            mat4 = np.identity(4, dtype=kwargs.get('dtype', None))
            mat4[0:3, 0:3] = mat
            return mat4
        else:
            return mat
    return wrapper

@as_mat4
def _translation(vec, dtype=None):
    mat = _identity(dtype)
    mat[3, 0:3] = vec[:3]
    return mat

@as_mat4
def _xrotation(theta, dtype=None):
    cosT = np.cos(theta)
    sinT = np.sin(theta)
    return np.array([[ 1.0, 0.0, 0.0 ],
                     [ 0.0, cosT,-sinT ],
                     [ 0.0, sinT, cosT ]],
                     dtype=dtype)

@as_mat4
def _yrotation(theta, dtype=None):
    cosT = np.cos(theta)
    sinT = np.sin(theta)
    return np.array([[ cosT, 0.0,sinT ],
                     [ 0.0, 1.0, 0.0 ],
                     [-sinT, 0.0, cosT ]],
                     dtype=dtype)

@as_mat4
def _zrotation(theta, dtype=None):
    cosT = np.cos(theta)
    sinT = np.sin(theta)
    return np.array([[ cosT,-sinT, 0.0 ],
                     [ sinT, cosT, 0.0 ],
                     [ 0.0, 0.0, 1.0 ]],
                     dtype=dtype)

def _rotation(vec, dtype=None):
    rot_x = _xrotation(vec[0], dtype=dtype)
    rot_y = _yrotation(vec[1], dtype=dtype)
    rot_z = _zrotation(vec[2], dtype=dtype)
    return rot_x @ rot_y @ rot_z

def _scale(scale, dtype=None):
    if isinstance(scale, float) or isinstance(scale, int):
        scale = [scale, scale, scale]
    m = np.diagflat([scale[0], scale[1], scale[2], 1.0])
    if dtype:
        m = m.astype(dtype)
    return m

def _transpose(mat):
    return np.transpose(mat)

def _invert(mat):
    return np.linalg.inv(mat)

class MatrixStack:
    def __init__(self, initial: np.ndarray = _mat4()):
        self.stack: list[np.ndarray] = [initial]
    
    def push(self, mat: np.ndarray):
        self.stack.append(mat)
    
    def pop(self):
        if not self.stack:
            raise IndexError("Stack is empty")
        return self.stack.pop()
    
    @property
    def head(self):
        if not self.stack:
            raise IndexError("Stack is empty")
        return self.stack[-1]
    
    def load_identity(self):
        if not self.stack:
            self.stack.append(_identity())
        else:
            self.stack[-1][:] = _identity()
    
    def mul(self, mat):
        if not self.stack:
            raise IndexError("Stack is empty")
        self.stack[-1] = _matmul(self.stack[-1], mat)
    
    def translate(self, vec):
        self.mul(_translation(vec))
    
    def scale(self, scale):
        self.mul(_scale(scale))
    
    def rotate(self, vec):
        self.mul(_rotation(vec))
    
    def rotate_x(self, theta):
        self.mul(_xrotation(theta))
    
    def rotate_y(self, theta):
        self.mul(_yrotation(theta))

    def rotate_z(self, theta):
        self.mul(_zrotation(theta))

class MatrixMode(Enum):
    MODELVIEW = 0
    PROJECTION = 1
    TEXTURE = 2

class GLState:
    def __init__(self):
        self.stacks = {k: MatrixStack() for k in MatrixMode}
        self._current_mode = MatrixMode.MODELVIEW

    @property
    def current_mode(self):
        return self._current_mode

    @current_mode.setter
    def current_mode(self, mode: MatrixMode):
        if mode not in MatrixMode:
            raise ValueError("Invalid matrix mode")
        self._current_mode = mode

    def push(self):
        self.stacks[self.current_mode].push(self.stacks[self.current_mode].head)
    
    def pop(self):
        return self.stacks[self.current_mode].pop()
    
    def load_identity(self):
        self.stacks[self.current_mode].load_identity()
    
    def translate(self, vec):
        self.stacks[self.current_mode].translate(vec)
    
    def rotate(self, vec):
        self.stacks[self.current_mode].rotate(vec)
    
    def xrotate(self, theta):
        self.stacks[self.current_mode].rotate_x(theta)

    def yrotate(self, theta):
        self.stacks[self.current_mode].rotate_y(theta)
    
    def zrotate(self, theta):
        self.stacks[self.current_mode].rotate_z(theta)
    
    def scale(self, scale):
        self.stacks[self.current_mode].mul(_scale(scale))

__state__ = GLState()

@contextmanager
def matrix_mode(mode: MatrixMode):
    original = __state__.current_mode
    __state__.current_mode = mode
    yield
    __state__.current_mode = original 

def push_matrix():
    __state__.push()

def pop_matrix():
    return __state__.pop()

def load_identity():
    __state__.load_identity()

def translate(x, y, z):
    __state__.translate([x, y, z])

def rotate(x, y, z):
    __state__.rotate([x, y, z])

def xrotate(theta):
    __state__.xrotate(theta)

def yrotate(theta):
    __state__.yrotate(theta)

def zrotate(theta):
    __state__.zrotate(theta)

def scale(scale):
    __state__.scale(scale)

def get_modelview_matrix():
    return __state__.stacks[MatrixMode.MODELVIEW].head

def get_projection_matrix():
    return __state__.stacks[MatrixMode.PROJECTION].head

def get_texture_matrix():
    return __state__.stacks[MatrixMode.TEXTURE].head