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

from .glsl import *

class VsAttrs(AttributeBlock):
    position = vec3()
    texcoord = vec2()
    color = vec4()

class VsUniforms(UniformBlock):
    model = mat4()
    view = mat4()
    projection = mat4()

class VsOut(ShaderInterface):
    gl_Position = vec4()
    texcoord = vec2()
    color = vec4()

def default_vertex_shader(attr: VsAttrs, uniforms: VsUniforms) -> VsOut:
    return VsOut(gl_Position=uniforms.projection * uniforms.view * uniforms.model * vec4(attr.position, 1.0),
                 texcoord=attr.texcoord,
                 color=attr.color)

class FsUniforms(UniformBlock):
    texture0 = sampler2D()
    diffuse = vec4()

class FsOut(FragmentShaderOutputBlock):
    fs_color = vec4()

def default_fragment_shader(vs_out: VsOut, uniforms: FsUniforms) -> FsOut:
    return FsOut(fs_color=texture(uniforms.texture0, vs_out.texcoord) * uniforms.diffuse * vs_out.color)

from .program import StaticProgram

class DefaultShader(StaticProgram):
    vertex_source = default_vertex_shader
    fragment_source = default_fragment_shader