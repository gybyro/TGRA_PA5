
from OpenGL.GL import *
from OpenGL.GLU import *

import numpy as np

class Triangle:
    def __init__(self):

        # x, y, z, r, g, b
        vertices = (
            -0.5, -0.5, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0,
             0.5, -0.5, 0.0, 0.0, 1.0, 0.0, 1.0, 1.0,
             0.0,  0.5, 0.0, 0.0, 0.0, 1.0, 0.5, 0.0
        )
        vertices = np.array(vertices, dtype=np.float32)

        self.vertex_count = 3

        # vertex array object
        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)

        # vertex buffer object
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)
        # GL_STATIC_DRAW : setting the data once and reading many times
        # GL_DYNAMIC_DRAW : reads and writes multiple times


        glEnableVertexAttribArray(0) # position
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(0))
        
        glEnableVertexAttribArray(1) # colour
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(12))

        glEnableVertexAttribArray(2) # texture coords
        glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(24))
    
    def arm_for_drawing(self) -> None:
        """Arm the triangle for drawing."""
        glBindVertexArray(self.vao)
    
    def draw(self) -> None:
        """Draw the triangle."""
        glDrawArrays(GL_TRIANGLES, 0, self.vertex_count)

    def destroy(self) -> None:
        """Free any allocated memory."""
        glDeleteVertexArrays(1,(self.vao,))
        glDeleteBuffers(1,(self.vbo,))