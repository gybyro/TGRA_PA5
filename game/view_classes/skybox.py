from __future__ import annotations

import ctypes
from typing import Sequence, Tuple, Union

import numpy as np
from OpenGL.GL import *
from PIL import Image


class Skybox:
    """Simple cube-map backed skybox renderer."""

    __slots__ = ("shader", "texture", "vao", "vbo", "vertex_count")

    def __init__(self, shader: int, face_paths: Union[str, Sequence[str]]):
        self.shader = shader
        self.vertex_count = 36
        self._create_buffers(1.0, 1.0, 1.0)
        self._load_cubemap(face_paths)

    def _create_buffers(self, w, d, h) -> None:

        # position: x, y, z,      normal: x, y, z,
        vertices = (
             # Front face (+Y)
            -w/2,  d/2, -h/2,     0, -1, 0,
             w/2,  d/2, -h/2,     0, -1, 0,
             w/2,  d/2,  h/2,     0, -1, 0,
             w/2,  d/2,  h/2,     0, -1, 0,
            -w/2,  d/2,  h/2,     0, -1, 0,
            -w/2,  d/2, -h/2,     0, -1, 0,

            # Back face (-Y)
            -w/2, -d/2,  h/2,     0, 1, 0,
             w/2, -d/2,  h/2,     0, 1, 0,
             w/2, -d/2, -h/2,     0, 1, 0,
             w/2, -d/2, -h/2,     0, 1, 0,
            -w/2, -d/2, -h/2,     0, 1, 0,
            -w/2, -d/2,  h/2,     0, 1, 0,

            # Left face (-X)
            -w/2, -d/2, -h/2,     1, 0, 0,
            -w/2, -d/2,  h/2,     1, 0, 0,
            -w/2,  d/2,  h/2,     1, 0, 0,
            -w/2,  d/2,  h/2,     1, 0, 0,
            -w/2,  d/2, -h/2,     1, 0, 0,
            -w/2, -d/2, -h/2,     1, 0, 0,

            # Right face (+X)
             w/2, -d/2,  h/2,     -1, 0, 0,
             w/2, -d/2, -h/2,     -1, 0, 0,
             w/2,  d/2, -h/2,     -1, 0, 0,
             w/2,  d/2, -h/2,     -1, 0, 0,
             w/2,  d/2,  h/2,     -1, 0, 0,
             w/2, -d/2,  h/2,     -1, 0, 0,

            # Top face (+Z)
            -w/2, -d/2,  h/2,     0, 0, -1,
             w/2, -d/2,  h/2,     0, 0, -1,
             w/2,  d/2,  h/2,     0, 0, -1,
             w/2,  d/2,  h/2,     0, 0, -1,
            -w/2,  d/2,  h/2,     0, 0, -1,
            -w/2, -d/2,  h/2,     0, 0, -1,

            # Bottom face (-Z)
            -w/2,  d/2, -h/2,      0, 0, 1,
             w/2,  d/2, -h/2,      0, 0, 1,
             w/2, -d/2, -h/2,      0, 0, 1,
             w/2, -d/2, -h/2,      0, 0, 1,
            -w/2, -d/2, -h/2,      0, 0, 1,
            -w/2,  d/2, -h/2,      0, 0, 1,
        )
        vertices = np.array(vertices, dtype=np.float32)


        self.vao = glGenVertexArrays(1)
        self.vbo = glGenBuffers(1)

        glBindVertexArray(self.vao)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

        #position
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(0))
        #normal
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(12))

        glBindVertexArray(0)

    def _load_cubemap(self, face_paths: Union[str, Sequence[str]]) -> None:
        if isinstance(face_paths, (str, bytes)):
            cubemap_faces = self._load_cross_image(str(face_paths))
        else:
            cubemap_faces = self._load_face_images(face_paths)

        self.texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_CUBE_MAP, self.texture)

        for index, face in enumerate(cubemap_faces):
            width, height = face.size
            img_data = face.tobytes()
            glTexImage2D(
                GL_TEXTURE_CUBE_MAP_POSITIVE_X + index,
                0,
                GL_RGBA,
                width,
                height,
                0,
                GL_RGBA,
                GL_UNSIGNED_BYTE,
                img_data,
            )

        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_R, GL_CLAMP_TO_EDGE)


    def _load_face_images(self, face_paths: Sequence[str]) -> Tuple[Image.Image, ...]:
        if len(face_paths) != 6:
            raise ValueError("Skybox requires exactly six texture paths")

        loaded_faces = []
        for path in face_paths:
            with Image.open(path) as image:
                loaded_faces.append(image.convert("RGBA").copy())
        return tuple(loaded_faces)

    def _load_cross_image(self, path: str) -> Tuple[Image.Image, ...]:
        with Image.open(path) as source_image:
            image = source_image.convert("RGBA")

        width, height = image.size
        face_size = width // 4
        if face_size * 4 != width or face_size * 3 != height:
            raise ValueError(
                "Skybox cross image must be laid out as a 4x3 grid of faces"
            )

        def crop_face(grid_x: int, grid_y: int) -> Image.Image:
            left = grid_x * face_size
            upper = grid_y * face_size
            right = left + face_size
            lower = upper + face_size
            return image.crop((left, upper, right, lower)).copy()

        # Layout (grid coordinates):
        #       [ ] [T] [ ] [ ]
        #       [L] [F] [R] [B]
        #       [ ] [D] [ ] [ ]
        # where the faces map to the OpenGL cubemap order of
        # positive X, negative X, positive Y, negative Y, positive Z, negative Z.


        # Convert the cross layout into the OpenGL cubemap order of
        # +X, -X, +Y, -Y, +Z, -Z.  Each face in the source image is oriented as
        faces = {
            "left": crop_face(0, 1),
            "front": crop_face(1, 1),
            "right": crop_face(2, 1),
            "back": crop_face(3, 1),

            "top": crop_face(1, 0),
            "bottom": crop_face(1, 2),
        }




    def draw(self, view: np.ndarray, projection: np.ndarray) -> None:
        glUseProgram(self.shader)
        glUniformMatrix4fv(glGetUniformLocation(self.shader, "view"), 1, GL_FALSE, view)
        glUniformMatrix4fv(
            glGetUniformLocation(self.shader, "projection"),
            1,
            GL_FALSE,
            projection,
        )
        glUniform1i(glGetUniformLocation(self.shader, "skybox"), 0)

        glDepthFunc(GL_LEQUAL)
        glBindVertexArray(self.vao)
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_CUBE_MAP, self.texture)
        glDrawArrays(GL_TRIANGLES, 0, self.vertex_count)
        glBindVertexArray(0)
        glDepthFunc(GL_LESS)

    # def draw(self) -> None:
    #     """Draw the triangle"""
    #     glDrawArrays(GL_TRIANGLES, 0, self.vertex_count)

    def destroy(self) -> None:
        """Free any allocated memory"""
        glDeleteVertexArrays(1, (self.vao,))
        glDeleteBuffers(1, (self.vbo,))
        glDeleteTextures(1, (self.texture,))
