
from OpenGL.GL import *
from OpenGL.GLU import *

import numpy as np
from game.model_classes.entity import Entity


class Cube(Entity):
    __slots__ = tuple([])

    def __init__(self, position: list[float], rotation: list[float], scale: list[float]):
        super().__init__(position, rotation, scale)
        self.id = "MAXWELL"
        

    def get_aabb(self):

        # half extents
        hx, hy, hz = 1, 1, 1

        # world position
        cx, cy, cz = self.position
        cz = cz + 0.9

        # 8 corners relative to center
        corners = np.array([
            [ hx,  hy,  hz],
            [ hx,  hy, -hz],
            [ hx, -hy,  hz],
            [ hx, -hy, -hz],
            [-hx,  hy,  hz],
            [-hx,  hy, -hz],
            [-hx, -hy,  hz],
            [-hx, -hy, -hz],
        ], dtype=np.float32)

        # create rotation matrix (e.g., around Z)
        rz = np.deg2rad(self.rotation[2])
        cosz, sinz = np.cos(rz), np.sin(rz)
        rot_matrix = np.array([
            [cosz, -sinz, 0],
            [sinz,  cosz, 0],
            [0,      0,   1]
        ], dtype=np.float32)

        rotated = (rot_matrix @ corners.T).T
        rotated += np.array([cx, cy, cz])

        min_corner = rotated.min(axis=0)
        max_corner = rotated.max(axis=0)
        return min_corner, max_corner
