import numpy as np
from OpenGL.GL import *
import pyrr

class Hitbox:
    def __init__(self, min_corner, max_corner):
        self.min = np.array(min_corner, dtype=np.float32)
        self.max = np.array(max_corner, dtype=np.float32)

        x0, y0, z0 = self.min
        x1, y1, z1 = self.max

        # 12 edges of the box
        self.vertices = np.array([
            # bottom
            x0, y0, z0,  x1, y0, z0,
            x1, y0, z0,  x1, y1, z0,
            x1, y1, z0,  x0, y1, z0,
            x0, y1, z0,  x0, y0, z0,
            # top
            x0, y0, z1,  x1, y0, z1,
            x1, y0, z1,  x1, y1, z1,
            x1, y1, z1,  x0, y1, z1,
            x0, y1, z1,  x0, y0, z1,
            # vertical edges
            x0, y0, z0,  x0, y0, z1,
            x1, y0, z0,  x1, y0, z1,
            x1, y1, z0,  x1, y1, z1,
            x0, y1, z0,  x0, y1, z1
        ], dtype=np.float32)

        # setup VAO/VBO
        self.vao = glGenVertexArrays(1)
        self.vbo = glGenBuffers(1)

        glBindVertexArray(self.vao)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)

        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, ctypes.c_void_p(0))
        glEnableVertexAttribArray(0)

        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindVertexArray(0)

    def draw(self, shader, view, projection, color=(1,0,0)):
        glUseProgram(shader)
        glUniformMatrix4fv(glGetUniformLocation(shader, "model"), 1, GL_FALSE, np.identity(4, dtype=np.float32))
        glUniformMatrix4fv(glGetUniformLocation(shader, "view"), 1, GL_FALSE, view)
        glUniformMatrix4fv(glGetUniformLocation(shader, "projection"), 1, GL_FALSE, projection)
        glUniform3f(glGetUniformLocation(shader, "color"), *color)

        glBindVertexArray(self.vao)
        glDrawArrays(GL_LINES, 0, len(self.vertices)//3)
        glBindVertexArray(0)


class CameraHitbox:
    def __init__(self, radius):
        self.radius = radius
        # Use a simple icosphere or UV sphere approximation
        self.segments = 12
        self.vertices = []
        for i in range(self.segments + 1):
            theta = np.pi * i / self.segments
            for j in range(self.segments + 1):
                phi = 2 * np.pi * j / self.segments
                x = radius * np.sin(theta) * np.cos(phi)
                y = radius * np.sin(theta) * np.sin(phi)
                z = radius * np.cos(theta)
                self.vertices.append([x, y, z])
        self.vertices = np.array(self.vertices, dtype=np.float32)
        # Setup VAO/VBO for rendering as GL_POINTS or GL_LINES

    def draw(self, shader, position, view, projection, color=(0,1,0)):
        # Apply translation to the camera position
        model = pyrr.matrix44.create_from_translation(position)
        glUseProgram(shader)
        glUniformMatrix4fv(glGetUniformLocation(shader, "model"), 1, GL_FALSE, model)
        glUniformMatrix4fv(glGetUniformLocation(shader, "view"), 1, GL_FALSE, view)
        glUniformMatrix4fv(glGetUniformLocation(shader, "projection"), 1, GL_FALSE, projection)
        glUniform3f(glGetUniformLocation(shader, "color"), *color)
        # Draw the sphere with GL_POINTS or lines


# class Hitbox:
#     def __init__(self, min_corner, max_corner):
#         """Hitbox defined in local space between min and max corners."""
#         self.min = np.array(min_corner, dtype=np.float32)
#         self.max = np.array(max_corner, dtype=np.float32)

#         # Center the hitbox around origin (0,0,0)
#         center = (self.min + self.max) / 2
#         self.vertices = self._build_vertices(self.min - center, self.max - center)

#         # Create GPU buffers
#         self.vao = glGenVertexArrays(1)
#         self.vbo = glGenBuffers(1)
#         glBindVertexArray(self.vao)
#         glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
#         glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)
#         glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, ctypes.c_void_p(0))
#         glEnableVertexAttribArray(0)
#         glBindBuffer(GL_ARRAY_BUFFER, 0)
#         glBindVertexArray(0)

#         # Store size and center for easy placement
#         self.size = self.max - self.min
#         self.center = center

#     def _build_vertices(self, min_corner, max_corner):
#         """Generate the 12 edges of a box."""
#         x0, y0, z0 = min_corner
#         x1, y1, z1 = max_corner
#         return np.array([
#             # bottom square
#             x0, y0, z0,  x1, y0, z0,
#             x1, y0, z0,  x1, y1, z0,
#             x1, y1, z0,  x0, y1, z0,
#             x0, y1, z0,  x0, y0, z0,
#             # top square
#             x0, y0, z1,  x1, y0, z1,
#             x1, y0, z1,  x1, y1, z1,
#             x1, y1, z1,  x0, y1, z1,
#             x0, y1, z1,  x0, y0, z1,
#             # vertical edges
#             x0, y0, z0,  x0, y0, z1,
#             x1, y0, z0,  x1, y0, z1,
#             x1, y1, z0,  x1, y1, z1,
#             x0, y1, z0,  x0, y1, z1,
#         ], dtype=np.float32)

#     def draw(self, shader, view, projection, model_matrix=None, color=(1, 0, 0)):
#         """Draw the hitbox with optional transform."""
#         glUseProgram(shader)

#         if model_matrix is None:
#             model_matrix = np.identity(4, dtype=np.float32)

#         glUniformMatrix4fv(glGetUniformLocation(shader, "model"), 1, GL_FALSE, model_matrix)
#         glUniformMatrix4fv(glGetUniformLocation(shader, "view"), 1, GL_FALSE, view)
#         glUniformMatrix4fv(glGetUniformLocation(shader, "projection"), 1, GL_FALSE, projection)
#         glUniform3f(glGetUniformLocation(shader, "color"), *color)

#         glBindVertexArray(self.vao)
#         glDrawArrays(GL_LINES, 0, len(self.vertices)//3)
#         glBindVertexArray(0)