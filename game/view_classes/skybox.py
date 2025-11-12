from __future__ import annotations

import ctypes
from typing import Sequence, Tuple, Union

import numpy as np
from OpenGL.GL import *
from PIL import Image


class Skybox:
    """Simple cube-map backed skybox renderer."""

    __slots__ = (
        "shader",
        "vao",
        "vbo",
        "vertex_count",
        "texture_a",
        "texture_b",
        "mix_value",
    )

    def __init__(self, shader: int, 
                cubemap_path_a: Union[str, Sequence[str]],
                cubemap_path_b: Union[str, Sequence[str]] | None = None,
    ):
        self.shader = shader
        self.vertex_count = 36
        self.mix_value = 0.0  # 0 = show A, 1 = show B

        self._create_buffers()
        self.texture_a = self._load_cubemap(cubemap_path_a)
        self.texture_b = (self._load_cubemap(cubemap_path_b) if cubemap_path_b else self.texture_a)


    def _create_buffers(self) -> None:
        """ daaamn geometry """
        w = h = d = 2

        # position: x, y, z,    texture: s(0:L, 1:R), t(0:T, 1:B)   normal: x, y, z,
        vertices = (
            # Right face (+X)
             w/2, -h/2,  d/2,  0, 0,   1, 0, 0,
             w/2, -h/2, -d/2,  1, 0,   1, 0, 0,
             w/2,  h/2, -d/2,  1, 1,   1, 0, 0,
             w/2,  h/2, -d/2,  1, 1,   1, 0, 0,
             w/2,  h/2,  d/2,  0, 1,   1, 0, 0,
             w/2, -h/2,  d/2,  0, 0,   1, 0, 0,

            # Left face (-X)
            -w/2, -h/2, -d/2,  0, 0,  -1, 0, 0,
            -w/2, -h/2,  d/2,  1, 0,  -1, 0, 0,
            -w/2,  h/2,  d/2,  1, 1,  -1, 0, 0,
            -w/2,  h/2,  d/2,  1, 1,  -1, 0, 0,
            -w/2,  h/2, -d/2,  0, 1,  -1, 0, 0,
            -w/2, -h/2, -d/2,  0, 0,  -1, 0, 0,

            # Top face (+Y)
            -w/2,  h/2, -d/2,  0, 0,   0, 1, 0,
             w/2,  h/2, -d/2,  1, 0,   0, 1, 0,
             w/2,  h/2,  d/2,  1, 1,   0, 1, 0,
             w/2,  h/2,  d/2,  1, 1,   0, 1, 0,
            -w/2,  h/2,  d/2,  0, 1,   0, 1, 0,
            -w/2,  h/2, -d/2,  0, 0,   0, 1, 0,

            # Bottom face (-Y)
            -w/2, -h/2,  d/2,  0, 0,   0, -1, 0,
             w/2, -h/2,  d/2,  1, 0,   0, -1, 0,
             w/2, -h/2, -d/2,  1, 1,   0, -1, 0,
             w/2, -h/2, -d/2,  1, 1,   0, -1, 0,
            -w/2, -h/2, -d/2,  0, 1,   0, -1, 0,
            -w/2, -h/2,  d/2,  0, 0,   0, -1, 0,
            
            # Front face (+Z)
            -w/2, -h/2,  d/2,  0, 0,   0, 0, 1,
             w/2, -h/2,  d/2,  1, 0,   0, 0, 1,
             w/2,  h/2,  d/2,  1, 1,   0, 0, 1,
             w/2,  h/2,  d/2,  1, 1,   0, 0, 1,
            -w/2,  h/2,  d/2,  0, 1,   0, 0, 1,
            -w/2, -h/2,  d/2,  0, 0,   0, 0, 1,

            # Back face (-Z)
            -w/2,  h/2, -d/2,  0, 0,   0, 0, -1,
             w/2,  h/2, -d/2,  1, 0,   0, 0, -1,
             w/2, -h/2, -d/2,  1, 1,   0, 0, -1,
             w/2, -h/2, -d/2,  1, 1,   0, 0, -1,
            -w/2, -h/2, -d/2,  0, 1,   0, 0, -1,
            -w/2,  h/2, -d/2,  0, 0,   0, 0, -1,
        )
        vertices = np.array(vertices, dtype=np.float32)


        # x, y, z, s, t, nx, ny, nz
        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)

        #Vertices
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

        #position
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(0))
        #texture / uv's
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(12))
        #normal
        glEnableVertexAttribArray(2)
        glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(20))


        glBindVertexArray(0)

        


    def _load_cubemap(self, face_paths: Union[str, Sequence[str]]) -> int:
        if isinstance(face_paths, (str, bytes)):
            cubemap_faces = self._load_cross_image(str(face_paths))
        else:
            cubemap_faces = self._load_face_images(face_paths)

        tex = glGenTextures(1)
        glBindTexture(GL_TEXTURE_CUBE_MAP, tex)

        for index, face in enumerate(cubemap_faces):
            width, height = face.size
            glTexImage2D(
                GL_TEXTURE_CUBE_MAP_POSITIVE_X + index,
                0,
                GL_RGBA,
                width,
                height,
                0,
                GL_RGBA,
                GL_UNSIGNED_BYTE,
                face.tobytes(),
            )

        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_R, GL_CLAMP_TO_EDGE)

        return tex


    def _load_face_images(self, face_paths: Sequence[str]) -> Tuple[Image.Image, ...]:
        if len(face_paths) != 6:
            raise ValueError("Skybox requires exactly six texture paths")
        return tuple(Image.open(p).convert("RGBA").copy() for p in face_paths)

        # loaded_faces = []
        # for path in face_paths:
        #     with Image.open(path) as image:
        #         loaded_faces.append(image.convert("RGBA").copy())

        # return tuple(loaded_faces)
    

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

        return (
            crop_face(2, 1),  # +X (right)
            crop_face(0, 1),  # -X (left)
            crop_face(1, 0),  # -Y (bottom)
            crop_face(1, 2),  # +Y (top)
            crop_face(1, 1),  # +Z (front)
            crop_face(3, 1),  # -Z (back)
        )


    def draw(self, view: np.ndarray, projection: np.ndarray) -> None:        
        glUseProgram(self.shader)        
        glUniformMatrix4fv(glGetUniformLocation(self.shader, "view"), 1, GL_FALSE, view)        
        glUniformMatrix4fv(glGetUniformLocation(self.shader, "projection"), 1, GL_FALSE, projection)
        glUniform1f(glGetUniformLocation(self.shader, "uMix"), self.mix_value)
        glUniform1i(glGetUniformLocation(self.shader, "uSkyboxA"), 0)
        glUniform1i(glGetUniformLocation(self.shader, "uSkyboxB"), 1)
       
        glDepthFunc(GL_LEQUAL)
        glBindVertexArray(self.vao)

        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_CUBE_MAP, self.texture_a)
        glActiveTexture(GL_TEXTURE1)
        glBindTexture(GL_TEXTURE_CUBE_MAP, self.texture_b)

        
        glDrawArrays(GL_TRIANGLES, 0, self.vertex_count)
        glBindVertexArray(0)
        glDepthFunc(GL_LESS)
        
    def destroy(self) -> None:
        glDeleteVertexArrays(1, (self.vao,))
        glDeleteBuffers(1, (self.vbo,))
        glDeleteTextures([self.texture_a, self.texture_b])
