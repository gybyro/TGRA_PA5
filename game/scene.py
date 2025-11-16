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

        # CURRRRRRRRRRRRVEYYY
        # Define control points for the billboard’s path
        self.bb_path_points = [
            np.array([40.0, 1.0, 30.0]),  # start
            np.array([40.0, 1.0, 60.0]),    # curve up left
            # np.array([2.0, 2.0, -3.0]),   # curve down
            np.array([40.0, 1.0, 30.0]),   # curve further away
            np.array([40.0, 1.0, -60.0])    # end
        ]

        self.bb_time = 0.0
        self.bb_speed = 0.2  # smaller = slower, bigger = faster



        ground = Plane(position=[0,-2,0], rotation=[0,0,0], scale=[1,1,1])

        # self.maze = Maze(ground)
        # self.maze.generate_walls()
        # walls = self.maze.wall_entities

        # # put max in the correct cell
        max = Cube(position = [6,-1,6], rotation = [0,0,0], scale = [0.1, 0.1, 0.1])
        # cx, cy = self.maze.get_player_cell(max.position)
        # self.maze.cells[cy * GLOBAL.GRID_SIZE + cx].entities.append(max)

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


        self.entities: dict[int, list[Entity]] = {

            GLOBAL.ENTITY_TYPE["GROUND"]: [
                ground,
            ],

            # GLOBAL.ENTITY_TYPE["3D_WALL"]: walls,

            GLOBAL.ENTITY_TYPE["CUBE"]: [
                Cube(position = [5,0,5], rotation = [0,0,0], scale = [1, 1, 1]),
            ],
            GLOBAL.ENTITY_TYPE["MAXWELL"]: [ max,
            ],

            GLOBAL.ENTITY_TYPE["MAXLIGHT"]: [ 
                Light(
                    position= [16,3,16],
                    color= [0.9,1,1],
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

        # if not GLOBAL.DEBUG_FLAT_WALLS:
        #     self.entities[GLOBAL.ENTITY_TYPE["3D_WALL"]] = walls
        # else:
        #     self.entities[GLOBAL.ENTITY_TYPE["WALL"]] = walls

        self.player = Camera(
            position = [0, 1, 0],
            rotation = [0, 0, 0]
        )

        self.set_music()

        # self.frames = [
        #     [16,16,-1],
        #     [16,15,-1],
        #     [16,14,-1],
        #     [16,13,-1],
        #     [16,12,-1],
        #     [16,11,-1],
        #     [16,10,-1],
        #     [16,9,-1],
        #     [16,8,-1],
        #     [16,7,-1],
        # ]


    def set_music(self):
        # Update OpenAL listener position/orientation to match player
        listener = Listener()
        listener.set_position(tuple(self.player.position))
        listener.set_orientation(tuple(self.player.forwards) + tuple(self.player.up))


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

        if delta_time > 0.0:
            # Animate billboards
            for entity in self.entities.get(GLOBAL.ENTITY_TYPE["BILLBOARD"], []):
                if isinstance(entity, AnimatedBillboard):
                    entity.advance(delta_time)

                    # Move along Bezier path
                    self.bb_time += delta_time * self.bb_speed
                    t = (np.sin(self.bb_time) * 0.5) + 0.5  # oscillate back and forth 0→1→0
                    entity.position = bezier_point(
                        *self.bb_path_points, t
                    )

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