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
from .shader import Program
from .pipeline import Pipeline 
from .draw import DrawCall
from .buffer import VertexBuffer

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

def shader():
    from trivial.shader.glsl import (AttributeBlock, ShaderInterface, FragmentShaderOutputBlock,
                                     UniformBlock, sampler2D, vec2, vec3, vec4, texture)
    from trivial.shader.shader import VertexStage, FragmentStage

    class VsAttrs(AttributeBlock):
        position = vec3()
        texcoord = vec2()
        # normal = vec3()
        in_color = vec4()

    class VsOut(ShaderInterface):
        gl_Position = vec4()
        out_texcoords = vec2()
        out_color = vec4()

    def vertex(attr: VsAttrs) -> VsOut:
        return VsOut(gl_Position=vec4(attr.position.x, attr.position.y, 0.0, 1.0),
                     out_texcoords=attr.texcoord,
                     out_color=attr.in_color)

    class FsOut(FragmentShaderOutputBlock):
        out_color = vec4()

    def fragment(vs_out: VsOut) -> FsOut:
        # TODO: Add sampler2D back + default texture
        return FsOut(out_color=vs_out.out_color)

    return VertexStage(vertex), FragmentStage(fragment)

class GLState:
    def __init__(self):
        self.stacks = {k: MatrixStack() for k in MatrixMode}
        self._current_mode = MatrixMode.MODELVIEW
        self._clear_color = (0.0, 0.0, 0.0, 1.0)
        self.viewport = (0, 0, 0, 0)
        self._default_shader = None
        self._last_texcoord = (0., 0.)
        self._last_normal = (0., 0., 1.)
        self._last_color = (1., 1., 1., 1.)
        self._transform_required = False
        self._data = None

    @property
    def default_shader(self):
        return self._default_shader

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
    
    @property
    def current_stack(self):
        return self.stacks[self._current_mode]

    def push_vertex(self, x, y, z):
        vertex = np.array([x, y, z, *__state__._last_texcoord, *__state__._last_color], dtype=np.float32)
        __state__._data.append(vertex)

__state__ = GLState()

@contextmanager
def matrix_mode(mode: MatrixMode):
    original = __state__.current_mode
    __state__.current_mode = mode
    yield
    __state__.current_mode = original

def push_matrix():
    __state__.current_stack.push(__state__.current_stack.head)

def pop_matrix():
    __state__.current_stack.pop()

def load_identity():
    __state__.current_stack.load_identity()

def translate(x, y, z):
    __state__.current_stack.translate([x, y, z])

def rotate(x, y, z):
    __state__.current_stack.rotate([x, y, z])

def rotate_x(theta):
    __state__.current_stack.xrotate(theta)

def rotate_y(theta):
    __state__.current_stack.yrotate(theta)

def rotate_z(theta):
    __state__.current_stack.zrotate(theta)

def scale(scale):
    __state__.current_stack.scale(scale)

def get_modelview_matrix():
    return __state__.stacks[MatrixMode.MODELVIEW].head

def get_projection_matrix():
    return __state__.stacks[MatrixMode.PROJECTION].head

def get_texture_matrix():
    return __state__.stacks[MatrixMode.TEXTURE].head

def load_ortho(left, right, bottom, top, near, far):
    __state__.current_stack.load_ortho(left, right, bottom, top, near, far)

def load_perpective(fovy, aspect, near, far):
    __state__.current_stack.load_perspective(fovy, aspect, near, far)

def viewport(x, y, width, height):
    __state__.viewport = (x, y, width, height)

def begin(mode: DrawMode):
    if not mode in DrawMode:
        raise ValueError("Invalid draw mode")
    if __state__._data is not None:
        raise RuntimeError("Missing `end()` call")
    __state__._data = []

def end():
    if __state__._data is None:
        raise RuntimeError("Missing or empty `begin()` call")
    if not len(__state__._data):
        raise RuntimeError("No vertices to draw")
    if not __state__._default_shader:
        __state__._default_shader = Program(shaders=[*shader()])
    input = np.array(__state__._data)
    pipeline = Pipeline(__state__.default_shader)
    data = pipeline.format(input)
    vbo = VertexBuffer(data=data)
    drawable = DrawCall(pipeline, **vbo.pointers)
    drawable.draw(projection=get_projection_matrix(),
                  modelview=get_modelview_matrix())
    __state__._data = None

def flush():
    pass

@contextmanager
def draw_mode(mode: DrawMode):
    begin(mode)
    yield
    end()

def vertex2(x, y, st=None, color=None):
    vertex3(x, y, 0.0, st=st, color=color)

def vertex3(x, y, z, st=None, color=None):
    assert __state__ is not None
    if st is not None:
        texcoord2(*st)
    if color is not None:
        color4(*color)
    __state__.push_vertex(x, y, z)

def texcoord2(s, t):
    __state__._last_texcoord = (s, t)

def normal3(x, y, z):
    __state__._last_normal = (x, y, z)

def int_or_float(func):
    def wrapper(*args):
        return func(*[a if isinstance(a, float) else (float(a) / 255.) for a in args])
    return wrapper

@int_or_float
def color4(r, g, b, a):
    __state__._last_color = (r, g, b, a)

def color3(r, g, b):
    color4(r, g, b, 1.0)