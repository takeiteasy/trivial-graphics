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
from OpenGL import GL
from .shader.default import DefaultShader
from .draw import DrawCall

def _mat4(dtype=np.float32):
    return np.zeros((4, 4), dtype=dtype)

def _identity(dtype=np.float32):
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
def _translation(vec, dtype=np.float32):
    mat = _identity(dtype)
    mat[3, 0:3] = vec[:3]
    return mat

@as_mat4
def _xrotation(theta, dtype=np.float32):
    cosT = np.cos(theta)
    sinT = np.sin(theta)
    return np.array([[ 1.0, 0.0, 0.0 ],
                     [ 0.0, cosT,-sinT ],
                     [ 0.0, sinT, cosT ]],
                     dtype=dtype)

@as_mat4
def _yrotation(theta, dtype=np.float32):
    cosT = np.cos(theta)
    sinT = np.sin(theta)
    return np.array([[ cosT, 0.0,sinT ],
                     [ 0.0, 1.0, 0.0 ],
                     [-sinT, 0.0, cosT ]],
                     dtype=dtype)

@as_mat4
def _zrotation(theta, dtype=np.float32):
    cosT = np.cos(theta)
    sinT = np.sin(theta)
    return np.array([[ cosT,-sinT, 0.0 ],
                     [ sinT, cosT, 0.0 ],
                     [ 0.0, 0.0, 1.0 ]],
                     dtype=dtype)

def _rotation(vec, dtype=np.float32):
    rot_x = _xrotation(vec[0], dtype=dtype)
    rot_y = _yrotation(vec[1], dtype=dtype)
    rot_z = _zrotation(vec[2], dtype=dtype)
    return rot_x @ rot_y @ rot_z

def _scale(scale, dtype=np.float32):
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

def _perspective(fovy, aspect, near, far, dtype=np.float32):
    ymax = near * np.tan(fovy * np.pi / 360.0)
    xmax = ymax * aspect
    left = -xmax
    right = xmax
    bottom = -ymax
    top = ymax
    A = (right + left) / (right - left)
    B = (top + bottom) / (top - bottom)
    C = -(far + near) / (far - near)
    D = -2. * far * near / (far - near)
    E = 2. * near / (right - left)
    F = 2. * near / (top - bottom)
    return np.array((
        (  E, 0., 0., 0.),
        ( 0.,  F, 0., 0.),
        (  A,  B,  C,-1.),
        ( 0., 0.,  D, 0.),
    ), dtype=dtype)

def _ortho(left, right, bottom, top, near, far, dtype=np.float32):
    rml = right - left
    tmb = top - bottom
    fmn = far - near
    A = 2. / rml
    B = 2. / tmb
    C = -2. / fmn
    Tx = -(right + left) / rml
    Ty = -(top + bottom) / tmb
    Tz = -(far + near) / fmn
    return np.array((
        ( A, 0., 0., 0.),
        (0.,  B, 0., 0.),
        (0., 0.,  C, 0.),
        (Tx, Ty, Tz, 1.),
    ), dtype=dtype)

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

    def load(self, mat):
        if not self.stack:
            self.stack.append(mat)
        else:
            self.stack[-1][:] = mat

    def load_identity(self):
        self.load(_identity())

    def load_ortho(self, left, right, bottom, top, near, far):
        self.load(_ortho(left, right, bottom, top, near, far))

    def load_perspective(self, fovy, aspect, near, far):
        self.load(_perspective(fovy, aspect, near, far))

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
    MODELVIEW = GL.GL_MODELVIEW
    PROJECTION = GL.GL_PROJECTION
    TEXTURE = GL.GL_TEXTURE

class DrawMode(Enum):
    POINTS = GL.GL_POINTS
    LINES = GL.GL_LINES
    TRIANGLES = GL.GL_TRIANGLES
    QUADS = GL.GL_QUADS

class GLState:
    def __init__(self):
        self.stacks = {k: MatrixStack() for k in MatrixMode}
        self._current_mode = MatrixMode.MODELVIEW
        self._clear_color = (0.0, 0.0, 0.0, 1.0)
        self.viewport = (0, 0, 0, 0)
        self._default_shader = DefaultShader()
        self._draw_calls = []

    @property
    def default_shader(self):
        return self._default_shader

    @property
    def last_draw_call(self):
        return self._draw_calls[-1] if self._draw_calls else None

    @property
    def current_mode(self):
        return self._current_mode

    @current_mode.setter
    def current_mode(self, mode: MatrixMode):
        if mode not in MatrixMode:
            raise ValueError("Invalid matrix mode")
        self._current_mode = mode

    @property
    def clear_color(self):
        return self._clear_color

    @clear_color.setter
    def clear_color(self, color):
        self._clear_color = [*np.clip([(c if isinstance(c, float) else float(c) / 255.) for c in (color if len(color) == 4 else (*color, 1.0))], 0., 1.)]
        assert len(self._clear_color) == 4

    def push(self):
        self.stacks[self.current_mode].push(self.stacks[self.current_mode].head)

    def pop(self):
        return self.stacks[self.current_mode].pop()

    def load_identity(self):
        self.stacks[self.current_mode].load_identity()

    def load_ortho(self, left, right, bottom, top, near, far):
        self.stacks[self.current_mode].load_ortho(left, right, bottom, top, near, far)

    def load_perspective(self, fovy, aspect, near, far):
        self.stacks[self.current_mode].load_perspective(fovy, aspect, near, far)

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

def rotate_x(theta):
    __state__.xrotate(theta)

def rotate_y(theta):
    __state__.yrotate(theta)

def rotate_z(theta):
    __state__.zrotate(theta)

def scale(scale):
    __state__.scale(scale)

def get_modelview_matrix():
    return __state__.stacks[MatrixMode.MODELVIEW].head

def get_projection_matrix():
    return __state__.stacks[MatrixMode.PROJECTION].head

def get_texture_matrix():
    return __state__.stacks[MatrixMode.TEXTURE].head

def load_ortho(left, right, bottom, top, near, far):
    __state__.load_ortho(left, right, bottom, top, near, far)

def load_perpective(fovy, aspect, near, far):
    __state__.load_perspective(fovy, aspect, near, far)

def viewport(x, y, width, height):
    __state__.viewport = (x, y, width, height)

def begin(mode: DrawMode):
    if not mode in DrawMode:
        raise ValueError("Invalid draw mode")
    last_call = __state__.last_draw_call
    if last_call:
        if last_call.dirty:
            raise RuntimeError('Missing `end` call')
    draw_call = DrawCall(program=__state__.default_shader, primitive=mode.value)
    __state__._draw_calls.append(draw_call)

def end():
    last_call = __state__.last_draw_call
    if last_call:
        last_call.build()

def flush():
    while __state__._draw_calls:
        draw_call = __state__._draw_calls.pop(0)
        # draw_call.draw()

@contextmanager
def draw_mode(mode: DrawMode):
    begin(mode)
    yield
    end()

def vertex2f(x, y):
    pass

def vertex3f(x, y, z):
    pass

def vertex2i(x, y):
    pass

def texcoord2f(s, t):
    pass

def normal3f(x, y, z):
    pass

def color3f(r, g, b):
    pass

def color4f(r, g, b, a):
    pass

def color3ub(r, g, b):
    pass

def color4ub(r, g, b, a):
    pass
