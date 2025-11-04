from OpenGL.GL import *
from OpenGL.GLU import *

import numpy as np


def loadMesh(filename: str) -> list[float]:
    """Load a mesh from an obj file.
        Parameters:
            filename: the filename.
        Returns:
            The loaded data, in a flattened format.
    """
    v, vt, vn = [], [], []
    vertices = []

    with open(filename, "r") as file:
        line = file.readline()
        while line:

            words = line.split(" ")
            match words[0]:
                case "v":
                    v.append(read_vertex_data(words))
                case "vt":
                    vt.append(read_texcoord_data(words))
                case "vn":
                    vn.append(read_normal_data(words))
                case "f":
                    read_face_data(words, v, vt, vn, vertices)
            line = file.readline()

    return vertices


def read_vertex_data(words: list[str]) -> list[float]:
    """Returns a vertex description"""

    return [
        float(words[1]),
        float(words[2]),
        float(words[3])
    ]
    
def read_texcoord_data(words: list[str]) -> list[float]:
    """Returns a texture coordinate description"""

    return [
        float(words[1]),
        float(words[2])
    ]
    
def read_normal_data(words: list[str]) -> list[float]:
    """Returns a normal vector description"""

    return [
        float(words[1]),
        float(words[2]),
        float(words[3])
    ]

def read_face_data(
    words: list[str], 
    v: list[list[float]], vt: list[list[float]], 
    vn: list[list[float]], vertices: list[float]) -> None:

    triangleCount = len(words) - 3

    for i in range(triangleCount):

        make_corner(words[1], v, vt, vn, vertices)
        make_corner(words[2 + i], v, vt, vn, vertices)
        make_corner(words[3 + i], v, vt, vn, vertices)

def make_corner(corner_description: str, 
    v: list[list[float]], vt: list[list[float]], 
    vn: list[list[float]], vertices: list[float]) -> None:

    v_vt_vn = corner_description.split("/")
    
    for element in v[int(v_vt_vn[0]) - 1]:
        vertices.append(element)
    for element in vt[int(v_vt_vn[1]) - 1]:
        vertices.append(element)
    for element in vn[int(v_vt_vn[2]) - 1]:
        vertices.append(element)


    
class Mesh:
    """A basic mesh which can hold data and be drawn"""

    __slots__ = ("vbo", "vao", "vertex_count")


    def __init__(self):
        
        # x, y, z, s, t, nx, ny, nz
        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)

        #Vertices
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
       
        #position
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(0))
        #texture
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(12))
        #normal
        glEnableVertexAttribArray(2)
        glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(20))

    def arm_for_drawing(self) -> None:
        """Arm the triangle for drawing"""
        glBindVertexArray(self.vao)
    
    def draw(self) -> None:
        """Draw the triangle"""
        glDrawArrays(GL_TRIANGLES, 0, self.vertex_count)

    def destroy(self) -> None:
        """Free any allocated memory"""
        glDeleteVertexArrays(1,(self.vao,))
        glDeleteBuffers(1,(self.vbo,))


class ObjMesh(Mesh):
    """A mesh which is initialized from an obj file"""
    __slots__ = tuple()


    def __init__(self, filename: str):
        super().__init__()

        # x, y, z, s, t, nx, ny, nz
        vertices = loadMesh(filename)
        self.vertex_count = len(vertices)//8
        vertices = np.array(vertices, dtype=np.float32)

        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)


class RectMesh(Mesh):
    """A mesh which constructs its vertices to represent a rectangle"""
    __slots__ = tuple()


    def __init__(self, w: float, h: float):
        """Initialize the rectangle mesh to the given
            width and height.
        """
        super().__init__()

        # position: x, y, z,    texture: s(0:L, 1:R), t(0:T, 1:B)   normal: x, y, z,
        vertices = (
            0, -w/2,  h/2, 0, 0, 1, 0, 0,
            0, -w/2, -h/2, 0, 1, 1, 0, 0,
            0,  w/2, -h/2, 1, 1, 1, 0, 0,

            0, -w/2,  h/2, 0, 0, 1, 0, 0,
            0,  w/2, -h/2, 1, 1, 1, 0, 0,
            0,  w/2,  h/2, 1, 0, 1, 0, 0
        )
        vertices = np.array(vertices, dtype=np.float32)
        self.vertex_count = 6
        
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

class CubeMesh(Mesh):

    def __init__(self, w: float, d: float, h: float):
        super().__init__()

        # position: x, y, z,    texture: s(0:L, 1:R), t(0:T, 1:B)   normal: x, y, z,
        vertices = (
             # Front face (+Y)
            -w/2,  d/2, -h/2,  0, 0,   0, 1, 0,
             w/2,  d/2, -h/2,  1, 0,   0, 1, 0,
             w/2,  d/2,  h/2,  1, 1,   0, 1, 0,
             w/2,  d/2,  h/2,  1, 1,   0, 1, 0,
            -w/2,  d/2,  h/2,  0, 1,   0, 1, 0,
            -w/2,  d/2, -h/2,  0, 0,   0, 1, 0,

            # Back face (-Y)
            -w/2, -d/2,  h/2,  0, 0,   0, -1, 0,
             w/2, -d/2,  h/2,  1, 0,   0, -1, 0,
             w/2, -d/2, -h/2,  1, 1,   0, -1, 0,
             w/2, -d/2, -h/2,  1, 1,   0, -1, 0,
            -w/2, -d/2, -h/2,  0, 1,   0, -1, 0,
            -w/2, -d/2,  h/2,  0, 0,   0, -1, 0,

            # Left face (-X)
            -w/2, -d/2, -h/2,  0, 0,  -1, 0, 0,
            -w/2, -d/2,  h/2,  1, 0,  -1, 0, 0,
            -w/2,  d/2,  h/2,  1, 1,  -1, 0, 0,
            -w/2,  d/2,  h/2,  1, 1,  -1, 0, 0,
            -w/2,  d/2, -h/2,  0, 1,  -1, 0, 0,
            -w/2, -d/2, -h/2,  0, 0,  -1, 0, 0,

            # Right face (+X)
             w/2, -d/2,  h/2,  0, 0,   1, 0, 0,
             w/2, -d/2, -h/2,  1, 0,   1, 0, 0,
             w/2,  d/2, -h/2,  1, 1,   1, 0, 0,
             w/2,  d/2, -h/2,  1, 1,   1, 0, 0,
             w/2,  d/2,  h/2,  0, 1,   1, 0, 0,
             w/2, -d/2,  h/2,  0, 0,   1, 0, 0,

            # Top face (+Z)
            -w/2, -d/2,  h/2,  0, 0,   0, 0, 1,
             w/2, -d/2,  h/2,  1, 0,   0, 0, 1,
             w/2,  d/2,  h/2,  1, 1,   0, 0, 1,
             w/2,  d/2,  h/2,  1, 1,   0, 0, 1,
            -w/2,  d/2,  h/2,  0, 1,   0, 0, 1,
            -w/2, -d/2,  h/2,  0, 0,   0, 0, 1,

            # Bottom face (-Z)
            -w/2,  d/2, -h/2,  0, 0,   0, 0, -1,
             w/2,  d/2, -h/2,  1, 0,   0, 0, -1,
             w/2, -d/2, -h/2,  1, 1,   0, 0, -1,
             w/2, -d/2, -h/2,  1, 1,   0, 0, -1,
            -w/2, -d/2, -h/2,  0, 1,   0, 0, -1,
            -w/2,  d/2, -h/2,  0, 0,   0, 0, -1,
        )
        vertices = np.array(vertices, dtype=np.float32)
        self.vertex_count = 36
        
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

