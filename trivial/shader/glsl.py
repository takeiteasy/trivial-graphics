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

from .interface import ShaderInterface, UniformBlock, AttributeBlock, FragmentShaderOutputBlock
from .types import GlslType, GlslArray

bool = GlslType
int = GlslType
uint = GlslType
float = GlslType
double = GlslType

vec2 = GlslType
vec3 = GlslType
vec4 = GlslType
bvec2 = GlslType
bvec3 = GlslType
bvec4 = GlslType
ivec2 = GlslType
ivec3 = GlslType
ivec4 = GlslType
uvec2 = GlslType
uvec3 = GlslType
uvec4 = GlslType
dvec2 = GlslType
dvec3 = GlslType
dvec4 = GlslType

mat2 = GlslType
mat3 = GlslType
mat4 = GlslType
mat2x2 = GlslType
mat2x3 = GlslType
mat2x4 = GlslType
mat3x2 = GlslType
mat3x3 = GlslType
mat3x4 = GlslType
mat4x2 = GlslType
mat4x3 = GlslType
mat4x4 = GlslType

dmat2 = GlslType
dmat3 = GlslType
dmat4 = GlslType
dmat2x2 = GlslType
dmat2x3 = GlslType
dmat2x4 = GlslType
dmat3x2 = GlslType
dmat3x3 = GlslType
dmat3x4 = GlslType
dmat4x2 = GlslType
dmat4x3 = GlslType
dmat4x4 = GlslType

sampler1D = GlslType
sampler2D = GlslType
sampler3D = GlslType
samplerCube = GlslType
sampler1DShadow = GlslType
sampler2DShadow = GlslType
samplerCubeShadow = GlslType

isampler1D = GlslType
isampler2D = GlslType
isampler3D = GlslType
isamplerCube = GlslType
usampler1D = GlslType
usampler2D = GlslType
usampler3D = GlslType
usamplerCube = GlslType
sampler2DRect = GlslType
sampler2DRectShadow = GlslType
isampler2DRect = GlslType
usampler2DRect = GlslType
samplerBuffer = GlslType
isamplerBuffer = GlslType
usamplerBuffer = GlslType
sampler1DArray = GlslType
sampler2DArray = GlslType
samplerCubeArray = GlslType
sampler1DArrayShadow = GlslType
sampler2DArrayShadow = GlslType
samplerCubeArrayShadow = GlslType
isampler1DArray = GlslType
isampler2DArray = GlslType
isamplerCubeArray = GlslType
usampler1DArray = GlslType
usampler2DArray = GlslType
usamplerCubeArray = GlslType

image1D = GlslType
iimage1D = GlslType
uimage1D = GlslType
image2D = GlslType
iimage2D = GlslType
uimage2D = GlslType
image3D = GlslType
iimage3D = GlslType
uimage3D = GlslType
image2DRect = GlslType
iimage2DRect = GlslType
uimage2DRect = GlslType
imageCube = GlslType
iimageCube = GlslType
uimageCube = GlslType
imageBuffer = GlslType
iimageBuffer = GlslType
uimageBuffer = GlslType
image1DArray = GlslType
iimage1DArray = GlslType
uimage1DArray = GlslType
image2DArray = GlslType
iimage2DArray = GlslType
uimage2DArray = GlslType
imageCubeArray = GlslType
iimageCubeArray = GlslType
uimageCubeArray = GlslType

Array1 = GlslArray
Array2 = GlslArray
Array3 = GlslArray
Array4 = GlslArray
Array5 = GlslArray
Array6 = GlslArray
Array7 = GlslArray
Array8 = GlslArray
Array9 = GlslArray
Array10 = GlslArray
Array11 = GlslArray
Array12 = GlslArray
Array13 = GlslArray
Array14 = GlslArray
Array15 = GlslArray
Array16 = GlslArray

class void(object):
    pass

def abs(*args, **kwargs):
    pass

def ceil(*args, **kwargs):
    pass

def floor(*args, **kwargs):
    pass

def round(*args, **kwargs):
    pass

def mod(*args, **kwargs):
    pass

def min(*args, **kwargs):
    pass

def max(*args, **kwargs):
    pass

def clamp(*args, **kwargs):
    pass

def mix(*args, **kwargs):
    pass

def step(*args, **kwargs):
    pass

def smoothstep(*args, **kwargs):
    pass

def sqrt(*args, **kwargs):
    pass

def pow(*args, **kwargs):
    pass

def exp(*args, **kwargs):
    pass

def log(*args, **kwargs):
    pass

def exp2(*args, **kwargs):
    pass

def log2(*args, **kwargs):
    pass

def sin(*args, **kwargs):
    pass

def cos(*args, **kwargs):
    pass

def tan(*args, **kwargs):
    pass

def asin(*args, **kwargs):
    pass

def acos(*args, **kwargs):
    pass

def atan(*args, **kwargs):
    pass

def atan2(*args, **kwargs):
    pass

def radians(*args, **kwargs):
    pass

def degrees(*args, **kwargs):
    pass

def length(*args, **kwargs):
    pass

def distance(*args, **kwargs):
    pass

def dot(*args, **kwargs):
    pass

def cross(*args, **kwargs):
    pass

def normalize(*args, **kwargs):
    pass

def reflect(*args, **kwargs):
    pass

def refract(*args, **kwargs):
    pass

def vecX(*args, **kwargs):
    pass

def matX(*args, **kwargs):
    pass

def transpose(*args, **kwargs):
    pass

def inverse(*args, **kwargs):
    pass

def outerProduct(*args, **kwargs):
    pass

def determinant(*args, **kwargs):
    pass

def texture(*args, **kwargs):
    pass

def textureLod(*args, **kwargs):
    pass

def textureProj(*args, **kwargs):
    pass

def textureOffset(*args, **kwargs):
    pass

def texelFetch(*args, **kwargs):
    pass

def noise1(*args, **kwargs):
    pass

def noise2(*args, **kwargs):
    pass

def noise3(*args, **kwargs):
    pass

def noise4(*args, **kwargs):
    pass

def dFdx(*args, **kwargs):
    pass

def dFdy(*args, **kwargs):
    pass

def fwidth(*args, **kwargs):
    pass

def any(*args, **kwargs):
    pass

def all(*args, **kwargs):
    pass

def isnan(*args, **kwargs):
    pass

def isinf(*args, **kwargs):
    pass

def floatBitsToInt(*args, **kwargs):
    pass

def intBitsToFloat(*args, **kwargs):
    pass

def packUnorm2x16(*args, **kwargs):
    pass

def unpackUnorm2x16(*args, **kwargs):
    pass
