from OpenGL import GL
from .buffer import IndexBuffer
from .buffer_pointer import BufferPointer
from ..object import ManagedObject, BindableObject, UnmanagedObject


class VertexArray(BindableObject, ManagedObject):
    _create_func = GL.glGenVertexArrays
    _delete_func = GL.glDeleteVertexArrays
    _bind_func = GL.glBindVertexArray

    def __init__(self):
        super(VertexArray, self).__init__()
        self._pointers = {}
        self._count = 0

    def __getitem__(self, index):
        return self._pointers[index]

    def __setitem__(self, index, value):
        if not isinstance(index, int):
            raise ValueError('Indices must be integers')

        if not isinstance(value, BufferPointer):
            raise ValueError('Requires BufferPointer')

        with self:
            value.enable(index)

        self._pointers[index] = value
        self._update_count()

    def __delitem__(self, index):
        if not isinstance(index, int):
            raise ValueError('Indices must be integers')

        with self:
            GL.glDisableVertexAttribArray(index)

        del self._pointers[index]
        self._update_count()

    def __iter__(self):
        return self._pointers.keys()

    def __len__(self):
        return len(self._pointers.keys())

    def _update_count(self):
        v = self._pointers.values()
        self._count = 0 if not v else min(map(lambda x: x.size, v))

    def clear(self):
        while self._pointers:  # Continue until the dictionary is empty
            location = next(iter(self._pointers))  # Get the first key
            del self[location]

    def render(self, primitive=GL.GL_TRIANGLES, start=None, count=None):
        start = start or 0
        count = count or (self._count - start)
        with self:
            GL.glDrawArrays(primitive, start, int(count))

    def render_indices(self, indices, primitive=GL.GL_TRIANGLES, start=None, count=None):
        if not isinstance(indices, IndexBuffer):
            raise ValueError('Indices must be of type IndexBuffer')

        with self:
            indices.render(primitive, start, count)

class UnmanagedVertexArray(VertexArray, UnmanagedObject):
    pass