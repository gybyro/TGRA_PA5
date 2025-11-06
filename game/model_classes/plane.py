import numpy as np
import pyrr
import config as GLOBAL
from game.model_classes.entity import Entity


class Plane(Entity):
    """The ground plane, uses rectangle mesh"""
    __slots__ = ("position", "scale", "texture")

    def __init__(self, 
                 position: list[float], 
                 rotation: list[float], 
                 scale: list[float], 
                 texture = ""):
        super().__init__(position, rotation, scale)

        self.texture = texture
        self.id = "WALL"


    def get_aabb(self):

        # half extents
        # hx, hy, hz = 0, self.scale[1] * 2, self.scale[2] * 2
        hx, hy, hz = (GLOBAL.GROUND_W / GLOBAL.GRID_SIZE) /2, GLOBAL.WALL_D /2, GLOBAL.WALL_H /2

        # world position
        cx, cy, cz = self.position

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



    
    
