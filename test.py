import trivial as gl
import numpy as np
from OpenGL import GL
from quickwindow import quick_window
import slimrr as rr

def test_shader():
    from trivial.shader.glsl import (AttributeBlock, UniformBlock,
                                          ShaderInterface, FragmentShaderOutputBlock,
                                          samplerBuffer, texelFetch, vec2,
                                          vec3, vec4, mat4)
    from trivial.shader.shader import VertexStage, FragmentStage

    class VsAttrs(AttributeBlock):
        position = vec3()
        texcoord = vec2()

    class VsUniforms(UniformBlock):
        projection = mat4()
        modelview = mat4()

    class VsOut(ShaderInterface):
        gl_Position = vec4()
        out_texcoords = vec2()

    def vertex(attr: VsAttrs, uniforms: VsUniforms) -> VsOut:
        return VsOut(gl_Position=uniforms.projection * uniforms.modelview * vec4(attr.position, 1.0),
                     out_texcoords=attr.texcoord)

    class FsUniforms(UniformBlock):
        in_buffer = samplerBuffer()

    class FsOut(FragmentShaderOutputBlock):
        out_color = vec4()

    def fragment(vs_out: VsOut, uniforms: FsUniforms) -> FsOut:
        return FsOut(out_color=texelFetch(uniforms.in_buffer, int(vs_out.out_texcoords.x * 32.0) + int(vs_out.out_texcoords.y * 32.0) * 32))

    return VertexStage(vertex), FragmentStage(fragment)

def create_cube(scale=(1.0,1.0,1.0), st=False, rgba=False, dtype='float32', type='triangles'):
    """Returns a Cube reading for rendering.

    Output is a tuple of numpy arrays.
    The first value is the vertex data, the second is the indices.

    The first dimension of the vertex data contains the list of vertices.
    The second dimension is the vertex data.

    Vertex data is always in the following order::

        [x, y, z, s, t, r, g, b, a]

    ST and RGBA are optional.
    If ST is dropped but RGBA is included the format will be::

        [x, y, z, r, g, b, a]

    If both ST and RGBA are dropped the format will be::

        [x, y, z]

    RGBA can also be of size 3 (RGB) or 4 (RGBA).

    Output format is as follows::

        numpy.array([
            # vertex 1
            [x, y, z, s, t, r, g, b, a],
            # vertex 2
            [x, y, z, s, t, r, g, b, a],
            ...
            # vertex N
            [x, y, z, s, t, r, g, b, a],
        ], dtype = dtype)

    :param bool,scalar,list,tuple,numpy.ndarray st: The ST texture co-ordinates.

        Default is False, which means ST will not be included in the array.

        If True is passed, the default ST values will be provided with the bottom-left
        of the quad being located at ST=(0.0,0.0) and the top-right being located at
        ST=(1.0,1.0).

        If a 2d list, tuple or numpy array is passed, it must have one of the following
        shapes::

            (2,2,), (4,2,), (6,2,),

        If the shape is (2,2,), the values are interpreted as the minimum and maximum
        values for ST.

        For example::

            st=((0.1,0.3),(0.2,0.4))

        S values will be between 0.1 to 0.2.
        T values will be between 0.3 to 0.4.

        The bottom left will receive the minimum of both, and the top right will receive
        the maximum.

        If the shape is (4,2,), the values are interpreted as being the actual ST values
        for the 4 vertices of each face.

        The vertices are in counter-clockwise winding order from the top right::

            [top-right, top-left, bottom-left, bottom-right,]

        If the shape is (6,2,), the values are interpreted as being the minimum and maximum
        values for each face of the cube.

        The faces are in the following order::

            [front, right, back, left, top, bottom,]


    :param bool,scalar,list,tuple,numpy.ndarray rgba: The RGBA colour.

        Default is False, which means RGBA will not be included in the array.

        If True is passed, the default RGBA values will be provided with all vertices
        being RGBA=(1.0, 1.0, 1.0, 1.0).

        If a 2d list, tuple or numpy array is passed, it must have one of the following
        shapes.::

                (3,), (4,), (4,3,), (4,4,), (6,3,), (6,4,), (24,3,), (24,4,),

        If the shape is (3,), the values are interpreted as being an RGB value (no alpha)
        to set on all vertices.

        If the shape is (4,), the values are interpreted the same as the shape (3,) except
        the alpha value is included.

        If the shape is (4,3,), the values are interpreted as being a colour to set on
        the 4 vertices of each face.

        The vertices are in counter-clockwise winding order from the top right::

            [top-right, top-left, bottom-left, bottom-right]

        If the shape is (4,4,), the values are interpreted the same as the shape (4,3,)
        except the alpha value is included.

        If the shape is (6,3,), the values are interpreted as being one RGB value (no alpha)
        for each face.

        The faces are in the following order::

            [front, right, back, left, top, bottom,]

        If the shape is (6,4,), the values are interpreted the same as the shape (6,3,) except
        the alpha value is included.

        If the shape is (24,3,), the values are interpreted as being an RGB value (no alpha)
        to set on each vertex of each face (4 * 6).

        The faces are in the following order::

            [front, right, back, left, top, bottom,]

        The vertices are in counter-clockwise winding order from the top right::

            [top-right, top-left, bottom-left, bottom-right]

        If the shape is (24,4,), the values are interpreted the same as the shape (24,3,)
        except the alpha value is included.


    :param string type: The type of indices to generate.

        Valid values are::

            ['triangles', 'triangle_strip', 'triangle_fan', 'quads', 'quad_strip',]

        If you just want the vertices without any index manipulation, use 'quads'.
    """

    shape = [24, 3]
    rgba_offset = 3

    width, height, depth = scale
    # half the dimensions
    width /= 2.0
    height /= 2.0
    depth /= 2.0

    vertices = np.array([
        # front
        # top right
        ( width, height, depth,),
        # top left
        (-width, height, depth,),
        # bottom left
        (-width,-height, depth,),
        # bottom right
        ( width,-height, depth,),

        # right
        # top right
        ( width, height,-depth),
        # top left
        ( width, height, depth),
        # bottom left
        ( width,-height, depth),
        # bottom right
        ( width,-height,-depth),

        # back
        # top right
        (-width, height,-depth),
        # top left
        ( width, height,-depth),
        # bottom left
        ( width,-height,-depth),
        # bottom right
        (-width,-height,-depth),

        # left
        # top right
        (-width, height, depth),
        # top left
        (-width, height,-depth),
        # bottom left
        (-width,-height,-depth),
        # bottom right
        (-width,-height, depth),

        # top
        # top right
        ( width, height,-depth),
        # top left
        (-width, height,-depth),
        # bottom left
        (-width, height, depth),
        # bottom right
        ( width, height, depth),

        # bottom
        # top right
        ( width,-height, depth),
        # top left
        (-width,-height, depth),
        # bottom left
        (-width,-height,-depth),
        # bottom right
        ( width,-height,-depth),
    ], dtype=dtype)

    st_values = None
    rgba_values = None

    if st:
        # default st values
        st_values = np.tile(
            np.array([
                (1.0, 1.0,),
                (0.0, 1.0,),
                (0.0, 0.0,),
                (1.0, 0.0,),
            ], dtype=dtype),
            (6,1,)
        )

        if isinstance(st, bool):
            pass
        elif isinstance(st, (int, float)):
            st_values *= st
        elif isinstance(st, (list, tuple, np.ndarray)):
            st = np.array(st, dtype=dtype)
            if st.shape == (2,2,):
                # min / max
                st_values *= st[1] - st[0]
                st_values += st[0]
            elif st.shape == (4,2,):
                # per face st values specified manually
                st_values[:] = np.tile(st, (6,1,))
            elif st.shape == (6,2,):
                # st values specified manually
                st_values[:] = st
            else:
                raise ValueError('Invalid shape for st')
        else:
            raise ValueError('Invalid value for st')

        shape[-1] += st_values.shape[-1]
        rgba_offset += st_values.shape[-1]

    if rgba:
        # default rgba values
        rgba_values = np.tile(np.array([1.0, 1.0, 1.0, 1.0], dtype=dtype), (24,1,))

        if isinstance(rgba, bool):
            pass
        elif isinstance(rgba, (int, float)):
            # int / float expands to RGBA with all values == value
            rgba_values *= rgba 
        elif isinstance(rgba, (list, tuple, np.ndarray)):
            rgba = np.array(rgba, dtype=dtype)

            if rgba.shape == (3,):
                rgba_values = np.tile(rgba, (24,1,))
            elif rgba.shape == (4,):
                rgba_values[:] = np.tile(rgba, (24,1,))
            elif rgba.shape == (4,3,):
                rgba_values = np.tile(rgba, (6,1,))
            elif rgba.shape == (4,4,):
                rgba_values = np.tile(rgba, (6,1,))
            elif rgba.shape == (6,3,):
                rgba_values = np.repeat(rgba, 4, axis=0)
            elif rgba.shape == (6,4,):
                rgba_values = np.repeat(rgba, 4, axis=0)
            elif rgba.shape == (24,3,):
                rgba_values = rgba
            elif rgba.shape == (24,4,):
                rgba_values = rgba
            else:
                raise ValueError('Invalid shape for rgba')
        else:
            raise ValueError('Invalid value for rgba')

        shape[-1] += rgba_values.shape[-1]

    data = np.empty(shape, dtype=dtype)
    data[:,:3] = vertices
    if st_values is not None:
        data[:,3:5] = st_values
    if rgba_values is not None:
        data[:,rgba_offset:] = rgba_values

    if type == 'triangles':
        # counter clockwise
        # top right -> top left -> bottom left
        # top right -> bottom left -> bottom right
        indices = np.tile(np.array([0, 1, 2, 0, 2, 3], dtype='int'), (6,1))
        for face in range(6):
            indices[face] += (face * 4)
        indices.shape = (-1,)
    elif type == 'triangle_strip':
        raise NotImplementedError
    elif type == 'triangle_fan':
        raise NotImplementedError
    elif type == 'quads':
        raise NotImplementedError
    elif type == 'quad_strip':
        raise NotImplementedError
    else:
        raise ValueError('Unknown type')

    return data, indices

with quick_window(640, 480, "test") as window:
    program = gl.Program(list(test_shader()))
    data, indices = create_cube((5.,5.,5.,), st=True, dtype=np.float32)
    flat_data = data[indices]
    call = gl.DrawCall(program, initial_data=flat_data)
    call._build()
    data = np.random.random_sample((512,512,4))
    data = data.astype(np.float32)
    tb = gl.TextureBuffer(data)
    bt = tb.texture
    bt.active_unit = program.in_buffer
    bt.bind()
    angle = 0.0
    
    for dt in window.loop():
        for e in window.events():
            print(e)
    
        width, height = window.size
        aspect = float(width) / float(height)
        projection = rr.Matrix44.perspective_projection(90., aspect, 1., 100., np.float32)
        model_view = rr.Matrix44.from_translation([0.,0.,-10.], np.float32)
        angle += dt
        if angle > 2 * np.pi:
            angle -= 2 * np.pi
        rotation = rr.Matrix44.from_y_rotation(angle, np.float32)
        model_view = model_view * rotation
    
        GL.glClearColor(0.2, 0.2, 0.2, 1.0)
        GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glDisable(GL.GL_CULL_FACE)
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
        call.draw(projection=projection, modelview=model_view)
