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
from typing import Optional, Union, Sequence, List, Callable, Any, get_type_hints
from pyglsl.interface import snake_case, ShaderInterface
from pyglsl.parse import parse, GlslVisitor

class NoDeclAssign(ast.Assign):
    """Mark an assignment as one that doesn't need to be declared.

    For example, `return Output(pos=vec2(0, 1))` should have GLSL output
       pos = vec2(0, 1);
    instead of
       vec2 pos = vec2(0, 1);
    """
    pass

def kwargs_as_assignments(call_node, parent):
    """Yield NoDeclAssign nodes from kwargs in a Call node."""
    if not isinstance(call_node, ast.Call):
        raise TypeError('node must be an ast.Call')

    if len(call_node.args) > 0:
        raise ValueError('positional args not allowed')

    for keyword in call_node.keywords:
        dst_name = keyword.arg

        if dst_name.startswith('gl_'):
            # Write to builtins directly
            target = [ast.Name(id=keyword.arg, ctx=ast.Load())]
        else:
            # Non-builtins are part of an interface block
            target = [ast.Attribute(value=parent, attr=keyword.arg,
                                    ctx=ast.Store())]

        yield NoDeclAssign(targets=target, value=keyword.value)

class _RewriteReturn(ast.NodeTransformer):
    def __init__(self, interface):
        self.interface = interface

    def _output_to_list(self, node):
        parent = ast.Name(id=self.interface.instance_name(), ctx=ast.Load())
        x = list(kwargs_as_assignments(node.value, parent))
        return x

    def visit_Return(self, node):  # pylint: disable=invalid-name
        return self._output_to_list(node)

    def visit_Expr(self, node):  # pylint: disable=invalid-name
        return node

class _Renamer(ast.NodeTransformer):
    # pylint: disable=invalid-name
    def __init__(self, names):
        self.names = names

    def visit_Name(self, node):
        new_name = self.names.get(node.id)
        if new_name is not None:
            node.id = new_name
        return node

    def visit_Attribute(self, node):
        node.value = self.visit(node.value)

        new_name = self.names.get(node.attr)
        if new_name is not None:
            node.attr = new_name

        return node

class _Remover(ast.NodeTransformer):
    def __init__(self, names):
        self.names = names

    def visit_Attribute(self, node):
        if hasattr(node, "value"):
            if isinstance(node.value, ast.Attribute):
                node.value = self.visit(node.value)
            elif isinstance(node.value, ast.Name) and node.value.id in self.names:
                delattr(node, "value")
        return node

class Stage:
    def __init__(self,
                 func: Callable[..., Any],
                 version: Optional[Union[str, int]] = "330 core",
                 library: Optional[List[Callable[..., Any]]] = []):
        self.library = library
        self.version = version
        self.root = parse(func)
        self.params = get_type_hints(func)
        self.params.pop("return", None)
        self.return_type = get_type_hints(func).get('return')

    def add_function(self, func: Union[Callable[..., Any], List[Callable[..., Any]]]):
        self.library = list(set(self.library + (func if isinstance(func, list) else [func])))

    def compile(self, is_fragment: Optional[bool] = False):
        lines = [f"#version {self.version}"]
        visitor = GlslVisitor()

        for name, ptype in sorted(self.params.items()):
            origin = getattr(ptype, "__origin__", None)
            is_array = None
            if origin is not None and origin == Sequence:
                ptype = ptype.__parameters__[0]
                is_array = True
            lines += ptype.declare_input_block(instance_name=name,
                                               array=is_array)

        node = self.root.body[0]
        if not isinstance(node, ast.FunctionDef):
            raise TypeError('input must be an ast.FunctionDef', node)
        node.name = "main"
        node.args.args = []
        node.returns = None

        node = _RewriteReturn(self.return_type).visit(node)
        ast.fix_missing_locations(node)
        node = _Renamer({'gl_position': 'gl_Position',
                         'gl_fragcolor': 'gl_FragColor'}).visit(node)

        if is_fragment:
            rem_names = [name for name, ptype in self.params.items() if ptype.__bases__[0].__name__ != 'ShaderInterface']
            rem_names.append(snake_case(self.return_type.__name__))
        else:
            rem_names = [name for name, _ in self.params.items()]
        node = _Remover(rem_names).visit(node)

        if self.return_type is not None:
            lines += self.return_type.declare_output_block()

        # TODO(nicholasbishop): for now we don't attempt to check if
        # the function is actually used, just define them all
        if self.library is not None:
            for f in self.library:
                lines.extend(GlslVisitor().visit(parse(f)).lines)

        return '\n'.join(lines + visitor.visit(self.root).lines)

class VertexStage(Stage):
    pass

class FragmentStage(Stage):
    def compile(self, is_fragment=True):
        return super().compile(is_fragment=True)
