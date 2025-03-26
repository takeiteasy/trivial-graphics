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

from trivial.mesh import Mesh
from enum import Enum
from slimrr import Vector3, Quaternion, Matrix44
from OpenGL import GL
import numpy as np

#define IQM_MAGIC "INTERQUAKEMODEL"
#define IQM_VERSION 2

_MAGIC = b"INTERQUAKEMODEL\x00"
_VERSION = b"\x02\x00\x00\x00"

class IQMLoader:
    def __init__(self, f):
        for attr in self.__annotations__:
            setattr(self, attr, f.read(16 if attr == 'magic' else 4))

class IQMSetter:
    def __init__(self):
        for attr in self.__annotations__:
            setattr(self, attr, None)

# typedef struct iqmheader
# {
#     char magic[16];
#     unsigned int version;
#     unsigned int filesize;
#     unsigned int flags;
#     unsigned int num_text, ofs_text;
#     unsigned int num_meshes, ofs_meshes;
#     unsigned int num_vertexarrays, num_vertexes, ofs_vertexarrays;
#     unsigned int num_triangles, ofs_triangles, ofs_adjacency;
#     unsigned int num_joints, ofs_joints;
#     unsigned int num_poses, ofs_poses;
#     unsigned int num_anims, ofs_anims;
#     unsigned int num_frames, num_framechannels, ofs_frames, ofs_bounds;
#     unsigned int num_comment, ofs_comment;
#     unsigned int num_extensions, ofs_extensions;
# } iqmheader;

class IQMHeader(IQMLoader):
    magic: str
    version: int
    filesize: int
    flags: int
    num_text: int
    ofs_text: int
    num_meshes: int
    ofs_meshes: int
    num_vertexarrays: int
    num_vertexes: int
    ofs_vertexarrays: int
    num_triangles: int
    ofs_triangles: int
    ofs_adjacency: int
    num_joints: int
    ofs_joints: int
    num_poses: int
    ofs_poses: int
    num_anims: int
    ofs_anims: int
    num_frames: int
    num_framechannels: int
    ofs_frames: int
    ofs_bounds: int
    num_comment: int
    ofs_comment: int
    num_extensions: int
    ofs_extensions: int

    def __init__(self, f):
        super().__init__(f)
        if self.magic != _MAGIC:
            raise ValueError('Invalid IQM file')
        if self.version != _VERSION:
            raise ValueError('Unsupported IQM version')
        
        

# typedef struct iqmmesh
# {
#     unsigned int name;
#     unsigned int material;
#     unsigned int first_vertex, num_vertexes;
#     unsigned int first_triangle, num_triangles;
# } iqmmesh;

class IQMMesh(IQMLoader):
    name: int
    material: int
    first_vertex: int
    num_vertexes: int
    first_triangle: int
    num_triangles: int

# enum
# {
#     IQM_POSITION     = 0,
#     IQM_TEXCOORD     = 1,
#     IQM_NORMAL       = 2,
#     IQM_TANGENT      = 3,
#     IQM_BLENDINDEXES = 4,
#     IQM_BLENDWEIGHTS = 5,
#     IQM_COLOR        = 6,
#     IQM_CUSTOM       = 0x10
# };

class IQMVertexArrayType(Enum):
    IQM_POSITION = 0
    IQM_TEXCOORD = 1
    IQM_NORMAL = 2
    IQM_TANGENT = 3
    IQM_BLENDINDEXES = 4
    IQM_BLENDWEIGHTS = 5
    IQM_COLOR = 6
    IQM_CUSTOM = 0x10

# enum
# {
#     IQM_BYTE   = 0,
#     IQM_UBYTE  = 1,
#     IQM_SHORT  = 2,
#     IQM_USHORT = 3,
#     IQM_INT    = 4,
#     IQM_UINT   = 5,
#     IQM_HALF   = 6,
#     IQM_FLOAT  = 7,
#     IQM_DOUBLE = 8,
# };

class IQMVertexType(Enum):
    IQM_BYTE = 0
    IQM_UBYTE = 1
    IQM_SHORT = 2
    IQM_USHORT = 3
    IQM_INT = 4
    IQM_UINT = 5
    IQM_HALF = 6
    IQM_FLOAT = 7
    IQM_DOUBLE = 8

# typedef struct iqmtriangle
# {
#     unsigned int vertex[3];
# } iqmtriangle;

class IQMTriangle:
    vertex: list[int]

    def __init__(self, f):
        self.vertex = [f.read(4) for _ in range(3)]

# typedef struct iqmadjacency
# {
#     unsigned int triangle[3];
# } iqmadjacency;

class IQMAdjacency:
    triangle: list[int]

    def __init__(self, f):
        self.triangle = [f.read(4) for _ in range(3)]

# typedef struct iqmjoint
# {
#     unsigned int name;
#     int parent;
#     float translate[3], rotate[4], scale[3];
# } iqmjoint;

class IQMJoint(IQMSetter):
    name: int
    parent: int
    translate: list[float]
    rotate: list[float]
    scale: list[float]

# typedef struct iqmpose
# {
#     int parent;
#     unsigned int mask;
#     float channeloffset[10];
#     float channelscale[10];
# } iqmpose;

class IQMPose(IQMSetter):
    parent: int
    mask: int
    channeloffset: list[float]
    channelscale: list[float]

# typedef struct iqmanim
# {
#     unsigned int name;
#     unsigned int first_frame, num_frames;
#     float framerate;
#     unsigned int flags;
# } iqmanim;

class IQMAnim(IQMSetter):
    name: int
    first_frame: int
    num_frames: int
    framerate: float
    flags: int

# enum
# {
#     IQM_LOOP = 1<<0
# };

class IQMAnimFlags(Enum):
    IQM_LOOP = 1<<0

# typedef struct iqmvertexarray
# {
#     unsigned int type;
#     unsigned int flags;
#     unsigned int format;
#     unsigned int size;
#     unsigned int offset;
# } iqmvertexarray;

class IQMVertexArray(IQMLoader):
    type: int
    flags: int
    format: int
    size: int
    offset: int

# typedef struct iqmbounds
# {
#     float bbmin[3], bbmax[3];
#     float xyradius, radius;
# } iqmbounds;

class IQMBounds(IQMSetter):
    bbmin: list[float]
    bbmax: list[float]
    xyradius: float
    radius: float

class Model:
    def __init__(self, meshes: list[Mesh]):
        self.meshes = meshes

    def draw(self, **uniforms):
        for mesh in self.meshes:
            mesh.draw(**uniforms)

# typedef struct Joint
# {
#   char name[NAMELEN];
#   int parent;
# }  Joint;

class Joint(IQMSetter):
    name: str
    parent: int

# typedef struct Pose
# {
#   Vector3 t;
#   Quaternion r;
#   Vector3 s;
# } Pose;

class Pose(IQMSetter):
    t: Vector3
    r: Quaternion
    s: Vector3

# typedef struct AnimatedMesh
# {
#   char name[NAMELEN];
#   int vertexCount;
#   int triangleCount;
#   float *vertices;
#   float *normals;
#   float *texcoords;
#   unsigned short *triangles;
#   int *weightid;
#   float *weightbias;

#   float *avertices;
#   float *anormals;

#   unsigned int vaoId;
#   unsigned int vboId[7];
# } AnimatedMesh;

class AnimatedMesh(Mesh):
    def __init__(self, num_vertexes, num_triangles, pipeline, indices=None, primitive=GL.GL_TRIANGLES, **pointers):
        super().__init__(pipeline, indices, primitive, **pointers)
        self.vertices = np.array(num_vertexes * 3, dtype=np.float32)
        self.normals = np.array(num_vertexes * 3, dtype=np.float32)
        self.texcoords = np.array(num_vertexes * 2, dtype=np.float32)
        self.triangles = np.array(num_triangles * 3, dtype=np.uint16)
        self.weightid = np.array(num_vertexes * 4, dtype=np.uint8)
        self.weightbias = np.array(num_vertexes * 4, dtype=np.float32)
        self.triangles = np.array(num_triangles * 3, dtype=np.uint16)
        self.avertices = np.array(num_vertexes * 3, dtype=np.float32)
        self.anormals = np.array(num_vertexes * 3, dtype=np.float32)

    def draw(self, **uniforms):
        super().draw(**uniforms)

# typedef struct Animation
# {
#   int jointCount;
# // joints in anims do not have names
#   Joint *joints;
#   int frameCount;
#   float framerate;
#   Pose **framepose;
# } Animation;

class Animation:
    def __init__(self):
        self.joints = []
        self.frameCount = 0
        self.framerate = 0
        self.framepose = []

# typedef struct AnimatedModel
# {
#   int meshCount;
#   AnimatedMesh *mesh;
#   int materialCount;
#   int *meshMaterials;
#   Material *materials;
#   int jointCount;
#   Joint *joints;
#   Pose *basepose;

#   Matrix transform;
# } AnimatedModel;

class AnimatedModel:
    def __init__(self, pipeline, model=None, animation=None, indices=None, primitive=GL.GL_TRIANGLES, **pointers):
        self.meshes = None
        self.names = {}
        self.joints = None
        self.basepose = None
        self.transform = Matrix44.identity()
        if model is not None:
            self.load_model(model)
        if animation is not None:
            self.load_animation(animation)

    def load_model(self, path):
        with open(path, 'rb') as f:
            header = IQMHeader(f)
            f.seek(header.ofs_meshes)
            self.meshes = [IQMMesh(f) for _ in range(header.num_meshes)]
            for m in self.meshes:
                f.seek(header.ofs_text + m.name)
                self.names[m.name] = f.read(32).decode('utf-8').strip('\x00')
                
            f.seek(header.ofs_triangles)
            self.triangles = [IQMTriangle(f) for _ in range(header.num_triangles)]
            for m in range(header.num_meshes):
                mesh = self.meshes[m]
                tcounter = 0
                for i in range(mesh.first_triangle, mesh.first_triangle + mesh.num_triangles):
                    tri = self.triangles[i]
                    mesh.triangles[tcounter+2] = tri.vertex[0] - mesh.first_vertex
                    mesh.triangles[tcounter+1] = tri.vertex[1] - mesh.first_vertex
                    mesh.triangles[tcounter]   = tri.vertex[2] - mesh.first_vertex
                    tcounter += 3
            self.vertexarrays = [IQMVertexArray(f) for _ in range(header.num_vertexarrays)]
            for va in self.vertexarrays:
                match IQMVertexArrayType(va.type):
                    case IQMVertexArrayType.IQM_POSITION:
                        pass
            
test = AnimatedModel(None, 'assets/guy.iqm')