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

def shader2():
    from trivial.shader.glsl import (AttributeBlock, ShaderInterface, FragmentShaderOutputBlock,
                                     UniformBlock, sampler2D, vec2, vec3, vec4, texture)
    from trivial.shader.shader import VertexStage, FragmentStage

    class VsAttrs(AttributeBlock):
        position = vec3()
        texcoord = vec2()

    class VsOut(ShaderInterface):
        gl_Position = vec4()
        out_texcoords = vec2()

    def vertex(attr: VsAttrs) -> VsOut:
        return VsOut(gl_Position=vec4(attr.position.x, attr.position.y, 0.0, 1.0),
                     out_texcoords=attr.texcoord)

    class FsUniforms(UniformBlock):
        in_buffer = sampler2D()

    class FsOut(FragmentShaderOutputBlock):
        out_color = vec4()

    def fragment(vs_out: VsOut, uniforms: FsUniforms) -> FsOut:
        return FsOut(out_color=texture(uniforms.in_buffer, vs_out.out_texcoords))

    return VertexStage(vertex), FragmentStage(fragment)

with quick_window(640, 480, "test") as window:
    program = gl.Program(shaders=list(test_shader()))
    pipelineA = gl.Pipeline(program)
    data, indices = gl.create_cube((5.,5.,5.,), st=True)
    cube_flat_data = pipelineA.format(data[indices])
    cube_vbo = gl.VertexBuffer(data=cube_flat_data)
    cube_vbo.set_data(cube_flat_data)
    cube = gl.Mesh(pipelineA, **cube_vbo.pointers)

    fbprogram = gl.Program(shaders=list(shader2()))
    pipelineB = gl.Pipeline(fbprogram)
    data, indices = gl.create_quad((2.,2.,), st=True)
    quad_flat_data = pipelineB.format(data[indices])
    quad_vbo = gl.VertexBuffer(data=quad_flat_data)
    quad = gl.Mesh(pipelineB, **quad_vbo.pointers)

    data = np.random.random_sample((512,512,4))
    data = data.astype(np.float32)
    tb = gl.TextureBuffer(data)
    angle = 0.0
    fbo = gl.FrameBufferTexture(dimensions=window.size)

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

        with fbo:
            GL.glClearColor(1.0, 0.2, 0.2, 1.0)
            GL.glEnable(GL.GL_DEPTH_TEST)
            GL.glEnable(GL.GL_CULL_FACE)
            GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT) # type: ignore
            GL.glViewport(0, 0, width, height)
            cube.draw(projection=projection, modelview=model_view, in_buffer=tb.texture)

        projection_fbo = rr.Matrix44.orthogonal_projection(-1., 1., -1., 1., -1., 1., np.float32)
        model_view_fbo = rr.Matrix44.identity(np.float32)
        GL.glClearColor(0.2, 0.2, 0.2, 1.0)
        GL.glDisable(GL.GL_DEPTH_TEST)
        GL.glDisable(GL.GL_CULL_FACE)
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)
        GL.glViewport(0, 0, width*2, height*2)
        quad.draw(projection=projection_fbo, modelview=model_view_fbo, in_buffer=fbo.texture)
