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

import ast
import attr
from typing import SupportsAbs, SupportsInt, SupportsFloat, TypeVar, Generic

class GlslType(SupportsAbs, SupportsInt, SupportsFloat):
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def __getattr__(self, name) -> 'GlslType':
        return GlslType(self, name)

    def __getitem__(self, index) -> 'GlslType':
        return GlslType(self, index)

    def __setitem__(self, index, val) -> 'GlslType':
        return GlslType(self, index, val)

    def __abs__(self) -> 'GlslType':
        return GlslType(self)

    def __add__(self, other) -> 'GlslType':
        return GlslType(self, other)

    def __sub__(self, other) -> 'GlslType':
        return GlslType(self, other)

    def __mul__(self, other) -> 'GlslType':
        return GlslType(self, other)

    def __truediv__(self, other) -> 'GlslType':
        return GlslType(self, other)

    def __int__(self):
        pass

    def __float__(self):
        pass

GlslArrayElem = TypeVar('GlslArrayElem')
class GlslArray(Generic[GlslArrayElem]):
    def __init__(self, gtype):
        pass

    def __getitem__(self, index):
        return GlslType(self, index)

    def __setitem__(self, index, val):
        return GlslType(self, index, val)

@attr.s
class ArraySpec(object):
    """Represents an array declaration.

    This type isn't currently intended to be used by client code
    directly, it's just a convenient form for internal use.
    """

    element_type = attr.ib()
    length = attr.ib()

    @classmethod
    def from_ast_node(cls, node):
        """Create a GlslArray from an AST node if possible.

        If the node cannot be converted then None is returned.
        """
        if not isinstance(node, ast.Subscript):
            return None
        if not isinstance(node.value, ast.Name):
            return None
        name = node.value.id
        prefix = 'Array'
        if not name.startswith(prefix):
            return None
        try:
            num = int(name[len(prefix):])
        except ValueError:
            return None
        if not isinstance(node.slice, ast.Name):
            return None
        gtype = node.slice.id
        return cls(gtype, num)
