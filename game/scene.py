import numpy as np
import config as GLOBAL
from game.model_classes.entity import Entity
from game.model_classes.camera import Camera
from game.model_classes.plane import Plane
from game.model_classes.cube import Cube
from game.model_classes.light import Light

from game.controller import Collision

class Scene:
    """Manages all objects and coordinates their interactions."""
    # __slots__ = ("entities", "player", "maze")

    
    def __init__(self):

        ground = Plane(position=[0,0,-2], rotation=[0,-90,0], scale=[1,1,1])

        # self.maze = Maze(ground)
        # self.maze.generate_walls()
        # walls = self.maze.wall_entities

        # # put max in the correct cell
        max = Cube(position = [16,16,-1], rotation = [90,0,0], scale = [0.1, 0.1, 0.1])
        # cx, cy = self.maze.get_player_cell(max.position)
        # self.maze.cells[cy * GLOBAL.GRID_SIZE + cx].entities.append(max)



        self.entities: dict[int, list[Entity]] = {

            GLOBAL.ENTITY_TYPE["GROUND"]: [
                ground,
            ],

            # GLOBAL.ENTITY_TYPE["3D_WALL"]: walls,

            GLOBAL.ENTITY_TYPE["CUBE"]: [
                Cube(position = [5,5,0], rotation = [0,0,0], scale = [1, 1, 1]),
            ],
            GLOBAL.ENTITY_TYPE["MAXWELL"]: [ max,
            ],

            GLOBAL.ENTITY_TYPE["MAXLIGHT"]: [ 
                Light(
                    position= [16,16,3],
                    color= [0.9,0.8,1],
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
        }

        # if not GLOBAL.DEBUG_FLAT_WALLS:
        #     self.entities[GLOBAL.ENTITY_TYPE["3D_WALL"]] = walls
        # else:
        #     self.entities[GLOBAL.ENTITY_TYPE["WALL"]] = walls

        self.player = Camera(
            position = [-5, 0, 1],
            rotation = [0, 0, 0]
        )

        self.frames = [
            [16,16,-1],
            [16,15,-1],
            [16,14,-1],
            [16,13,-1],
            [16,12,-1],
            [16,11,-1],
            [16,10,-1],
            [16,9,-1],
            [16,8,-1],
            [16,7,-1],
        ]


    def update(self, frame_no) -> None:
        """Takes in a number representing what frame it is on"""
        for entitt in self.entities:
            if entitt == GLOBAL.ENTITY_TYPE["MAXWELL"]:
                if len(self.frames) > frame_no:
                    self.entities[entitt][0].update([self.frames[frame_no]])


        # gently rotate the camera each frame so the skybox is visible
        self.player.spin(np.array([0.0, 0.0, 1.0], dtype=np.float32))
        self.player.update()

    def move_player(self, d_pos: list[float]) -> None:
        """Move the player by the given amount in the (forwards, right, up) vectors.
        """

        # get list of collidable objects close to the player
        collidables: list[Entity] = []

        # proposed new position
        new_pos = self.player.position + (
            d_pos[0] * self.player.forwards +
            d_pos[1] * self.player.right +
            d_pos[2] * self.player.up
        )
        cell_x, cell_y = self.maze.get_player_cell(new_pos) # Find which maze cell the player is in

        # for print vvv which cell you in
        # ol_x, ol_y = self.maze.get_player_cell(self.player.position) # earlier player cell
        # if cell_x != ol_x or cell_y != ol_y:
        #     print(f"Cell: {cell_x}, {cell_y}")

        # Get nearby cells (1 cell radius is fine)
        cells = self.maze.get_nearby_cells(cell_x, cell_y)
        for cel in cells:
            collidables.extend(cel.walls)
            # collidables.extend(cel.entities) # add the things that are in that cell

        collidables.append(self.entities[GLOBAL.ENTITY_TYPE["MAXWELL"]][0])

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