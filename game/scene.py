import numpy as np
import time
import config as GLOBAL
from game.model_classes.entity import Entity
from game.model_classes.camera import Camera
from game.model_classes.plane import Plane
from game.model_classes.cube import Cube
from game.model_classes.light import Light
from game.model_classes.billboard import AnimatedBillboard

from game.controller import Collision
from openal import oalInit, oalQuit, oalOpen, Listener
from game.sound_manager import *




def bezier_point(p0, p1, p2, p3, t):
    """Compute a 3D point on a cubic Bézier curve."""
    return (
        (1 - t)**3 * p0
        + 3 * (1 - t)**2 * t * p1
        + 3 * (1 - t) * t**2 * p2
        + t**3 * p3
    )



class Scene:
    """Manages all objects and coordinates their interactions."""
    # __slots__ = ("entities", "player", "maze")

    
    def __init__(self):

        self.view_index = 0
        self._animation_setup()


        billboard_sequence = (
            "res/images/animation_test/fleeting_1.png",
            "res/images/animation_test/fleeting_2.png",
            "res/images/animation_test/fleeting_3.png",
            "res/images/animation_test/fleeting_4.png",
            "res/images/animation_test/fleeting_5.png",
            "res/images/animation_test/fleeting_6.png",
            "res/images/animation_test/fleeting_7.png",
            "res/images/animation_test/fleeting_8.png",
            "res/images/animation_test/fleeting_9.png",
        )
        billboard_frame_rate = 9.0

        self.animation_sequences: dict[int, dict[str, object]] = {
            GLOBAL.ENTITY_TYPE["BILLBOARD"]: {
                "paths": billboard_sequence,
                "frame_rate": billboard_frame_rate,
            }
        }


        truck = Cube(position = [-100,60, -120], rotation = [-90,0,0], scale = [0.05, 0.05, 0.05])
        truck.id = "AIRPLANE"


        self.entities: dict[int, list[Entity]] = {

            GLOBAL.ENTITY_TYPE["GROUND"]: [
                Plane(position=[0,-2,0], rotation=[0,0,0], scale=[1,1,1]),
            ],
            GLOBAL.ENTITY_TYPE["CUBE"]: [
                Cube(position = [5,0,5], rotation = [0,0,0], scale = [1, 1, 1]),
            ],
            GLOBAL.ENTITY_TYPE["MAXWELL"]: [
                Cube(position = [7,-1, 0], rotation = [0,0,0], scale = [0.1, 0.1, 0.1]),
            ],
            GLOBAL.ENTITY_TYPE["AIRPLANE"]: [
                truck,
            ],

            GLOBAL.ENTITY_TYPE["MAXLIGHT"]: [ 
                Light(
                    position= [0,0,0],
                    color= [0.5,0.3,0.8],
                    strength = 80
                )
            ],
            
            GLOBAL.ENTITY_TYPE["POINTLIGHT"]: [
                Light(
                    position = [
                        np.random.uniform(low=-20.0, high=20.0), 
                        np.random.uniform(low=-20.0, high=20.0), 
                        np.random.uniform(low=-1.0, high=4.0)],
                    color = [
                        np.random.uniform(low=0.1, high=1.0), 
                        np.random.uniform(low=0.1, high=1.0), 
                        np.random.uniform(low=0.1, high=1.0)],
                    strength = 20)
                for _ in range(8)
            ],
            GLOBAL.ENTITY_TYPE["BILLBOARD"]: [
                AnimatedBillboard(
                    position=[10, 1, 10],
                    scale=[1.0, 4.0, 4.0],
                    texture_paths=billboard_sequence,
                    frame_rate=billboard_frame_rate,
                )
            ],
        }


        self.player = Camera(
            position = [0, 1, 0],
            rotation = [0, 0, 0]
        )

        self.set_music()

        


    def _animation_setup(self):

        # CURRRRRRRRRRRRVEYYY
        # Define control points for the billboard’s path
        self.pos_path_points = [
            np.array([-100,60.0,-140]),
            np.array([-200,50.0,-140]),
            np.array([-100,60.0,-140]),
            np.array([-10.0,50.0,-140])
        ]
        self.rot_path_points = [
            np.array([-90.5,  0.0,   0.0]),
            np.array([-90, -40.0, 0.0]),
            np.array([-89.5,  0.0,   0.0]),
            np.array([-90, 30.0,  0.0]),
        ]

        self.bb_time = 0.0
        self.bb_speed = 0.2          # smaller = slower, bigger = faster

        self.bb_angle = 0.5          # current orbit angle in radians
        self.bb_orbit_speed = 0.8    # radians per second
        self.bb_orbit_radius = 20.0  # how far from the player
        self.bb_height = 2.0         # height above player

    def set_music(self):
        # Update OpenAL listener position/orientation to match player
        listener = Listener()
        listener.set_position(tuple(self.player.position))
        listener.set_orientation(tuple(self.player.forwards) + tuple(self.player.up))

    def cycle_camera_view(self):
        """Switch camera to the next angle in GLOBAL.TEST_VIEWS """
        self.view_index = (self.view_index + 1) % len(GLOBAL.TEST_VIEWS)
        view = GLOBAL.TEST_VIEWS[self.view_index]

        # update rotation (roll, yaw, pitch)
        self.player.rotation = np.array(view["rot"], dtype=np.float32)
        # update position
        self.player.position = np.array(view["pos"], dtype=np.float32)
        # update camera internal vectors
        self.player.update()



    def update(self, frame_no: int, delta_time: float) -> None:
        """Takes in a number representing what frame it is on"""
        # for entitt in self.entities:
        #     if entitt == GLOBAL.ENTITY_TYPE["MAXWELL"]:
        #         if len(self.frames) > frame_no:
        #             self.entities[entitt][0].update([self.frames[frame_no]])

        for entities in self.entities.values():
            for entity in entities:
                if entity.id == "MAXWELL":
                    entity.update(delta_time)
                else:
                    pass


        # gently rotate the camera each frame so the skybox is visible
        # self.player.spin(np.array([0.0, 1.0, 0.0], dtype=np.float32))


        self.player.update()

        # Bezier animtion
        if delta_time > 0.0:
            # Animate billboards
            for entity in self.entities.get(GLOBAL.ENTITY_TYPE["AIRPLANE"], []):

                # Move along Bezier path (pos)
                self.bb_time += delta_time * self.bb_speed
                t = (np.sin(self.bb_time) * 0.5) + 0.5  # oscillate back and forth 0→1→0
                
                entity.position = bezier_point(
                    *self.pos_path_points, t
                )
                entity.rotation = bezier_point(
                    *self.rot_path_points, t
                ) % 360
                

        # --- Billboard world-centered orbit animation ---
        for entity in self.entities.get(GLOBAL.ENTITY_TYPE["BILLBOARD"], []):
            if isinstance(entity, AnimatedBillboard):
                # animation frames
                entity.advance(delta_time)

                # update orbital angle
                self.bb_angle += delta_time * self.bb_orbit_speed
                if self.bb_angle > np.pi * 2:
                    self.bb_angle -= np.pi * 2

                # orbit center = world origin (0,0,0)
                center = np.array([0.0, 0.0, 0.0], dtype=np.float32)

                # compute orbit position
                x = center[0] + self.bb_orbit_radius * np.cos(self.bb_angle)
                y = self.bb_height
                z = center[2] + self.bb_orbit_radius * np.sin(self.bb_angle)
                

                # assign position
                entity.position = np.array([x, y, z], dtype=np.float32)

                # make billboard face the player
                entity.update(self.player.position)



    def move_player(self, d_pos: list[float]) -> None:
        """Move the player by the given amount in the (right, up, forwards) vectors.
        """

        # get list of collidable objects close to the player
        collidables: list[Entity] = []

        # proposed new position
        new_pos = self.player.position + (
            d_pos[0] * self.player.right +
            d_pos[1] * self.player.up +
            d_pos[2] * self.player.forwards
        )
        # cell_x, cell_y = self.maze.get_player_cell(new_pos) # Find which maze cell the player is in

        # for print vvv which cell you in
        # ol_x, ol_y = self.maze.get_player_cell(self.player.position) # earlier player cell
        # if cell_x != ol_x or cell_y != ol_y:
        #     print(f"Cell: {cell_x}, {cell_y}")

        # Get nearby cells (1 cell radius is fine)
        # cells = self.maze.get_nearby_cells(cell_x, cell_y)
        # for cel in cells:
        #     collidables.extend(cel.walls)
            # collidables.extend(cel.entities) # add the things that are in that cell

        # collidables.append(self.entities[GLOBAL.ENTITY_TYPE["MAXWELL"]][0])

        if GLOBAL.DEBUG_COLLISION:
            # for coll in collidables:
            #     if coll.id != "WALL":
            #         print(f"{coll.id}")

            # for spherical players ..
            pos = self.player.position.copy()  # start from current
            new_pos = Collision.get_player_move(pos, new_pos, collidables)

        
        self.player.move(new_pos)

    def spin_player(self, d_eulers: list[float]) -> None:
        """Spin the player by the given amount"""
        self.player.spin(d_eulers)