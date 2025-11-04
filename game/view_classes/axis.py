from OpenGL.GL import *
import numpy as np
import pyrr

class AxisCross:
    def __init__(self, length=0.5):
        # 3 axes, each 2 vertices (start, end)
        vertices = np.array([
            # X axis (red)
            0.0, 0.0, 0.0,  1.0, 0.0, 0.0,
            length, 0.0, 0.0,  1.0, 0.0, 0.0,

            # Y axis (green)
            0.0, 0.0, 0.0,  0.0, 1.0, 0.0,
            0.0, length, 0.0,  0.0, 1.0, 0.0,

            # Z axis (blue)
            0.0, 0.0, 0.0,  0.0, 0.0, 1.0,
            0.0, 0.0, length,  0.0, 0.0, 1.0
        ], dtype=np.float32)

        # Setup VAO + VBO
        self.vao = glGenVertexArrays(1)
        self.vbo = glGenBuffers(1)

        glBindVertexArray(self.vao)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

        # position (3 floats) + color (3 floats)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 6 * 4, ctypes.c_void_p(0))
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 6 * 4, ctypes.c_void_p(12))
        glEnableVertexAttribArray(1)

        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindVertexArray(0)

    def draw(self, shader, position, forwards, right, up):
        glUseProgram(shader)

        # Build a rotation matrix from the camera's basis vectors
        rotation_matrix = np.array([
            [right[0],  up[0],  -forwards[0],  0.0],
            [right[1],  up[1],  -forwards[1],  0.0],
            [right[2],  up[2],  -forwards[2],  0.0],
            [0.0,       0.0,     0.0,          1.0]
        ], dtype=np.float32)

        translation_matrix = np.identity(4, dtype=np.float32)
        translation_matrix[3, :3] = position

        model_matrix = rotation_matrix @ translation_matrix

        glUniformMatrix4fv(glGetUniformLocation(shader, "model"), 1, GL_FALSE, model_matrix)

        glBindVertexArray(self.vao)
        glDrawArrays(GL_LINES, 0, 6)
        glBindVertexArray(0)

    # def draw(self, shader, position, forwards, right, up, distance=1.0):
    #     glUseProgram(shader)

    #     # Position the cross in front of the camera
    #     cross_pos = position + forwards * distance

    #     # We want world-aligned orientation — so identity rotation
    #     model_matrix = np.identity(4, dtype=np.float32)
    #     model_matrix[:3, 3] = cross_pos

    #     glUniformMatrix4fv(glGetUniformLocation(shader, "model"), 1, GL_FALSE, model_matrix)

    #     glBindVertexArray(self.vao)
    #     glDrawArrays(GL_LINES, 0, 6)
    #     glBindVertexArray(0)