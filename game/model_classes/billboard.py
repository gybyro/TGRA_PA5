
from OpenGL.GL import *
from OpenGL.GLU import *

import numpy as np
import pyrr

from game.model_classes.entity import Entity

class Billboard(Entity):
    """An object which always faces towards the camera"""
    __slots__ = tuple()


    def __init__(self, position: list[float]):
        super().__init__(position, rotation=[0,0,0])
        self.id = "bill"
    
    def update(self, dt: float, camera_pos: np.ndarray) -> None:
        self_to_camera = camera_pos - self.position
        self.rotation[2] = -np.degrees(np.arctan2(-self_to_camera[1], self_to_camera[0]))
        dist2d = pyrr.vector.length(self_to_camera)
        self.rotation[1] = -np.degrees(np.arctan2(self_to_camera[2], dist2d))