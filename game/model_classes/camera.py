import numpy as np
import pyrr

import config as GLOBAL
from game.model_classes.entity import Entity


class Camera(Entity):
    """First person camera -ish"""

    # __slots__ = ("forwards", "right", "up", "maze")


    def __init__(self, position: list[float], rotation):
        super().__init__(position, rotation) # inherits from Entity

        # re initialize the directionals in np.zeros
        self.forwards = np.zeros(3, dtype=np.float32)
        self.right = np.zeros(3, dtype=np.float32)
        self.up = np.zeros(3, dtype=np.float32)
        self.update(0)


    def update(self, timeline_data: dict | None = None) -> None:

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

        if timeline_data:
            self.apply_animation(timeline_data)

    def apply_animation(self, camera_state) -> None:
        """Takes in some stuffs"""
        position = camera_state.get("position", self.position)
        target = camera_state.get("target", self.position + self.forwards)
        up = camera_state.get("up", self.up)

        self.position = np.array(position, dtype=np.float32)


        



    def get_view_transform(self) -> np.ndarray:
        """Returns the camera's world to view transformation matrix.
        """
        return pyrr.matrix44.create_look_at(
            eye = self.position,
            target = self.position + self.forwards,
            up = self.up, dtype = np.float32)


    def spin(self, d_eulers) -> None:

        self.rotation += d_eulers

        self.rotation[0] %= 360
        self.rotation[1] = min(89, max(-89, self.rotation[1]))
        self.rotation[2] %= 360