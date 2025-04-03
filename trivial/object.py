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

class DescriptorMixin(object):
    """Mixin to enable runtime-added descriptors."""
    def __getattribute__(self, name):
        attr = super(DescriptorMixin, self).__getattribute__(name)
        if (hasattr(attr, "__get__") and attr.__get__ is not None) and not callable(attr):
            return attr.__get__(self, self.__class__)
        else:
            return attr

    def __setattr__(self, name, value):
        try:
            attr = super(DescriptorMixin, self).__getattribute__(name)
            return attr.__set__(self, value)
        except AttributeError:
            return super(DescriptorMixin, self).__setattr__(name, value)


class GLObject(object):
    def __init__(self, **kwargs):
        super(GLObject, self).__init__()


class ManagedObject(GLObject):
    _create_func = None
    _delete_func = None

    def __init__(self, handle=None, dontdelete=False, **kwargs):
        super(ManagedObject, self).__init__(handle=handle, **kwargs)
        self.dontdelete = dontdelete
        self._create(handle)

    def _create(self, handle):
        if handle:
            self._handle = handle
        else:
            func = self._create_func
            if hasattr(self._create_func, 'wrappedOperation'):
                func = self._create_func.wrappedOperation

            if len(func.argNames) == 2:
                self._handle = self._create_func(1)
            elif len(func.argNames) == 1:
                self._handle = self._create_func(self._type)
            else:
                self._handle = self._create_func()

    def __del__(self):
        self._destroy()

    def _destroy(self):
        if self.dontdelete:
            return
        func = self._delete_func
        if hasattr(self._delete_func, 'wrappedOperation'):
            func = self._delete_func.wrappedOperation

        if len(func.argNames) == 2:
            try:
                self._delete_func(1, [self._handle])
            except TypeError:
                from ctypes import c_uint
                handle_array = (c_uint * 1)(self._handle)
                self._delete_func(1, handle_array)
        else:
            self._delete_func(self._handle)
        self._handle = None

    @property
    def handle(self):
        return self._handle
    
    @property
    def id(self):
        return self._handle

class UnmanagedObject(ManagedObject):
    def __init__(self, handle=None, **kwargs):
        ManagedObject.__init__(self, handle, dontdelete=True, **kwargs)

    def __del__(self):
        pass


class BindableObject(GLObject):
    _bind_function = None
    _target = None

    def __init__(self, **kwargs):
        super(BindableObject, self).__init__(**kwargs)

    def bind(self):
        func = self._bind_func
        if hasattr(self._bind_func, 'wrappedOperation'):
            func = self._bind_func.wrappedOperation

        if len(func.argNames) == 2:
            self._bind_func(self._target, self._handle)
        else:
            self._bind_func(self._handle)

    def unbind(self):
        func = self._bind_func
        if hasattr(self._bind_func, 'wrappedOperation'):
            func = self._bind_func.wrappedOperation

        if len(func.argNames) == 2:
            self._bind_func(self._target, 0)
        else:
            self._bind_func(0)

    def __enter__(self):
        self.bind()

    def __exit__(self, exc_type, exc_value, traceback):
        self.unbind()
