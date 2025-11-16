
from OpenGL.GL import *
from OpenGL.GLU import *
# from __future__ import annotations

import numpy as np
import pyrr

from game.model_classes.entity import Entity

class Billboard(Entity):
    """An object which always faces towards the camera"""
    __slots__ = tuple()


    def __init__(self, position: list[float], scale: list[float] | None = None):
        super().__init__(position, rotation=[0.0, 0.0, 0.0], scale=scale or [1.0, 1.0, 1.0])
        self.id = "bill"
    
    # def update(self, dt: float, camera_pos: np.ndarray) -> None:
    #     self_to_camera = camera_pos - self.position
    #     self.rotation[2] = -np.degrees(np.arctan2(-self_to_camera[1], self_to_camera[0]))
    #     dist2d = pyrr.vector.length(self_to_camera)
    #     self.rotation[1] = -np.degrees(np.arctan2(self_to_camera[2], dist2d))

    def update(self, camera_pos: np.ndarray) -> None:
        """Rotate so the billboard faces the active camera."""

        dir_vec = camera_pos - self.position
        dir_vec[1] = 0.0     # Remove vertical influence (true billboard)

        if np.allclose(dir_vec, 0.0):
            return
        
        dir_vec = pyrr.vector.normalize(dir_vec)
        
        # billboard mesh is facing +X by default, so we compute yaw from X/Z:
        yaw = np.degrees(np.arctan2(dir_vec[0], dir_vec[2]))

        # Lock pitch/roll so it only spins around Y
        self.rotation[:] = (0.0, yaw, 0.0)




class AnimatedBillboard(Billboard):
    """Billboard that cycles through an image sequence."""

    __slots__ = ("frame_rate", "frame_count", "current_frame", "_time_accumulator", "texture_paths")

    def __init__(
        self,
        position: list[float],
        scale: list[float] | None = None,
        texture_paths: list[str] | tuple[str, ...] | None = None,
        frame_rate: float = 1.0,
    ) -> None:
        super().__init__(position, scale=scale)
        self.texture_paths: tuple[str, ...] = tuple(texture_paths or ())
        self.frame_rate = frame_rate
        self.frame_count = len(self.texture_paths)
        self.current_frame = 0
        self._time_accumulator = 0.0

    def set_sequence(self, texture_paths: list[str] | tuple[str, ...], frame_rate: float) -> None:
        """Assign a new sequence for the billboard to play."""
        self.texture_paths = tuple(texture_paths)
        self.frame_rate = frame_rate
        self.frame_count = len(self.texture_paths)
        self.current_frame = 0
        self._time_accumulator = 0.0

    def advance(self, delta_time: float) -> None:
        """Advance the animation based on elapsed time."""
        if self.frame_count == 0 or self.frame_rate <= 0.0:
            return

        self._time_accumulator += delta_time
        frame_time = 1.0 / self.frame_rate
        while self._time_accumulator >= frame_time:
            self._time_accumulator -= frame_time
            self.current_frame = (self.current_frame + 1) % self.frame_count