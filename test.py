import omgl as gl
import numpy as np
from OpenGL import GL
from quickwindow import quick_window
import pyrr as rr

def test_shader():
    from omgl.shader.glsl import (AttributeBlock, UniformBlock,
                                          ShaderInterface, FragmentShaderOutputBlock,
                                          samplerBuffer, texelFetch, vec2,
                                          vec3, vec4, mat4)
    from omgl.shader.shader import VertexStage, FragmentStage

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

with quick_window(640, 480, "test") as window:
    program = gl.Program(list(test_shader()))
    data, indices = rr.geometry.create_cube((5.,5.,5.,), st=True, dtype=np.float32)
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
