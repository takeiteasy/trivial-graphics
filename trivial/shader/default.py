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