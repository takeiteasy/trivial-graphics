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

from .glsl import *

class VsAttrs(AttributeBlock):
    position = vec3()
    texcoord = vec2()
    color = vec4()

class VsUniforms(UniformBlock):
    modelview = mat4()
    projection = mat4()

class VsOut(ShaderInterface):
    gl_Position = vec4()
    texcoord = vec2()
    color = vec4()

def default_vertex_shader(attr: VsAttrs, uniforms: VsUniforms) -> VsOut:
    return VsOut(gl_Position=uniforms.projection * uniforms.modelview * vec4(attr.position, 1.0),
                 texcoord=attr.texcoord,
                 color=attr.color)

class FsOut(FragmentShaderOutputBlock):
    fs_color = vec4()

def default_fragment_shader(vs_out: VsOut) -> FsOut:
    return FsOut(fs_color=vs_out.color)
