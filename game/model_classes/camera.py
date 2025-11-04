import numpy as np
import pyrr

import config as GLOBAL
from game.model_classes.entity import Entity
from game.model_classes.maze import Maze

class Camera(Entity):
    """First person camera."""

    __slots__ = ("forwards", "right", "up", "maze")


    def __init__(self, position: list[float], rotation, maze: Maze):
        super().__init__(position, rotation) # inherits from Entity

        self.maze = maze
        self.update(0)


    def update(self, dt: float) -> None:

        # where we are looking in the horizontal plane (north, east, south, west)
        theta = self.rotation[2]
        # where we are looking vertically (up, down)
        phi = self.rotation[1]

        self.forwards = np.array(
            [
                np.cos(np.deg2rad(theta)) * np.cos(np.deg2rad(phi)),
                np.sin(np.deg2rad(theta)) * np.cos(np.deg2rad(phi)),
                np.sin(np.deg2rad(phi))
            ],
            dtype = np.float32
        )

        self.right = np.cross(self.forwards, GLOBAL.Z)
        self.up = np.cross(self.right, self.forwards)



    def get_view_transform(self) -> np.ndarray:
        """Returns the camera's world to view transformation matrix.
        """

        return pyrr.matrix44.create_look_at(
            eye = self.position,
            target = self.position + self.forwards,
            up = self.up, dtype = np.float32)

    def move(self, new_pos: list[float]) -> None:
        """Move by the given amount in the (forwards, right, up) vectors.
        """
        self.position = new_pos
        if not GLOBAL.DEBUG_FLY: self.position[2] = 1 # hard coding the z constraint


    def spin(self, d_eulers) -> None:

        self.rotation += d_eulers

        self.rotation[0] %= 360
        self.rotation[1] = min(89, max(-89, self.rotation[1]))
        self.rotation[2] %= 360


    def get_hitsphere(self):
        """Returns (center, radius) for collision detection"""
        center = self.position.copy()
        center[2] = center[2]/2
        radius = GLOBAL.PLAYER_RADIUS  # define in config
        return center, radius
        
    def get_hitbox(self):
        """Returns AABB for collision detection"""
        half_size = np.array([GLOBAL.PLAYER_W/2, GLOBAL.PLAYER_W/2, GLOBAL.PLAYER_H/2], dtype=np.float32)
        min_corner = self.position - half_size
        max_corner = self.position + half_size
        return min_corner, max_corner