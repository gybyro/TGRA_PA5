import numpy as np
import pyrr
import random
import config as GLOBAL
from game.model_classes.entity import Entity
from game.model_classes.plane import Plane
from game.view_classes.hitbox import Hitbox

class Cell():
    __slots__ = ("x", "y", "walls", "entities")


    def __init__(self, x: int =0, y: int =0):
        self.x = x
        self.y = y

        # order: top, bottom, left, right
        self.walls: list[Plane] = []

        self.entities: list[Entity] = []
        

class Maze():
    """The maze, returns a list of plane objects
    """

    def __init__(self, ground: Plane):

        # position=[0,0,-2], rotation=[0,90,0], scale=[1,1,1]

        self.gp = ground.position
        self.gr = ground.rotation
        self.gs = ground.scale

        self.cell_size = GLOBAL.GROUND_W/GLOBAL.GRID_SIZE

        # self.gtrans = ground.get_model_transform()

        # 2D grid of cells
        # self.cells = [[Cell(x, y) for x in range(GLOBAL.GRID_SIZE)] for y in range(GLOBAL.GRID_SIZE)]
        # Store wall entities
        self.cells = []
        self.wall_entities = []

        if GLOBAL.DEBUG_GENERATE_MAZE:
            self.map = self.generate_map(GLOBAL.GRID_SIZE, seed=123)
        else:
            self.map = self.test_map()

        
        
    def generate_walls(self):


        # offset in world coords, how far away from the center of the cell do you want the walls???
        # offset = cell_size/2 - 0.05
        offset = self.cell_size/2


        wc = GLOBAL.WALL_H / 2
        scale = [1, 1, 1]
        self.wall_hitboxes: list[Hitbox] = []

        for y in range(GLOBAL.GRID_SIZE):
            for x in range(GLOBAL.GRID_SIZE):
                # cell = self.cells[x][y]
                map_cell = self.map[y * GLOBAL.GRID_SIZE + x]
                cell = Cell(x, y)

                # compute cell center in world coordinates
                cx = self.gp[0] - GLOBAL.GROUND_W/2 + (x + 0.5) * self.cell_size
                cy = self.gp[1] - GLOBAL.GROUND_H/2 + (y + 0.5) * self.cell_size
                cz = self.gp[2]  # ground height


                # top wall
                if map_cell[0]:
                    pos = [cx, cy - offset, cz + wc]
                    # scale = [cell_size, GLOBAL.WALL_H, wall_thickness]
                    wall = Plane(position=pos, rotation=[0,0,0], scale=scale)
                    self.wall_entities.append(wall)
                    cell.walls.append(wall)
                    self.wall_hitboxes.append(Hitbox(*wall.get_aabb()))

                # bottom wall
                if map_cell[1]:
                    pos = [cx, cy + offset, cz + wc]
                    # scale = [cell_size, GLOBAL.WALL_H, wall_thickness]
                    wall = Plane(position=pos, rotation=[0,0,0], scale=scale)
                    self.wall_entities.append(wall)
                    cell.walls.append(wall)
                    self.wall_hitboxes.append(Hitbox(*wall.get_aabb()))

                # left wall
                if map_cell[2]:
                    pos = [cx - offset, cy, cz + wc]
                    # scale = [wall_thickness, GLOBAL.WALL_H, cell_size]
                    wall = Plane(position=pos, rotation=[0,0,90], scale=scale, )
                    self.wall_entities.append(wall)
                    cell.walls.append(wall)
                    self.wall_hitboxes.append(Hitbox(*wall.get_aabb()))

                # right wall
                if map_cell[3]:
                    pos = [cx + offset, cy, cz + wc]
                    # scale = [wall_thickness, GLOBAL.WALL_H, cell_size]
                    wall = Plane(position=pos, rotation=[0,0,90], scale=scale)
                    self.wall_entities.append(wall)
                    cell.walls.append(wall)
                    self.wall_hitboxes.append(Hitbox(*wall.get_aabb()))
        
                # self.cells[y][x] = cell
                self.cells.append(cell)

    def get_cell(self, x, y):
        cell_x = int(x // self.cell_size)
        cell_y = int(y // self.cell_size)
        cell_x = max(0, min(GLOBAL.GRID_SIZE - 1, cell_x))
        cell_y = max(0, min(GLOBAL.GRID_SIZE - 1, cell_y))
        return cell_x, cell_y

               
    def get_player_cell(self, player_pos):
        """Return (x, y) grid coordinates of the player's current cell"""

        # shift player position so ground center is (0, 0)
        local_x = player_pos[0] - (self.gp[0] - GLOBAL.GROUND_W / 2)
        local_y = player_pos[1] - (self.gp[1] - GLOBAL.GROUND_H / 2)
        cell_x = int(local_x // self.cell_size)
        cell_y = int(local_y // self.cell_size)

        # Clamp to maze bounds
        cell_x = max(0, min(GLOBAL.GRID_SIZE - 1, cell_x))
        cell_y = max(0, min(GLOBAL.GRID_SIZE - 1, cell_y))

        return cell_x, cell_y
    
    def get_nearby_walls(self, cell_x, cell_z, radius=1):
        """Return a small list of wall entities around a given cell."""

        walls: list[Plane] = []

        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                x = cell_x + dx
                y = cell_z + dy
                if 0 <= x < GLOBAL.GRID_SIZE and 0 <= y < GLOBAL.GRID_SIZE:
                    walls.extend(self.cells[y * GLOBAL.GRID_SIZE + x].walls)

        return walls
    
    def get_nearby_cells(self, cell_x, cell_z, radius=1):
        """Return the player cell and surrounding cells"""

        cells: list[Cell] = []

        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                x = cell_x + dx
                y = cell_z + dy
                if 0 <= x < GLOBAL.GRID_SIZE and 0 <= y < GLOBAL.GRID_SIZE:
                    # cells.append(self.cells[y][x])
                    cells.append(self.cells[y * GLOBAL.GRID_SIZE + x])

        return cells
    
    def generate_map(self, grid_size: int, seed: int = 42):
        random.seed(seed)

        # Each cell: [top, bottom, left, right]
        cells = [[[True, True, True, True] for _ in range(grid_size)] for _ in range(grid_size)]

        visited = [[False for _ in range(grid_size)] for _ in range(grid_size)]

        def in_bounds(x, y):
            return 0 <= x < grid_size and 0 <= y < grid_size

        def carve(x, y):
            visited[y][x] = True
            directions = [(0, -1, 0), (0, 1, 1), (-1, 0, 2), (1, 0, 3)]  # (dx, dy, wall_index)
            random.shuffle(directions)

            for dx, dy, wall in directions:
                nx, ny = x + dx, y + dy
                if in_bounds(nx, ny) and not visited[ny][nx]:
                    # knock down walls between current and next
                    cells[y][x][wall] = False
                    opposite = [1, 0, 3, 2][wall]
                    cells[ny][nx][opposite] = False
                    carve(nx, ny)

        # start from top-left
        carve(0, 0)

        # ensure entry and exit are open
        cells[0][0][2] = False        # open left side
        cells[grid_size - 1][grid_size - 1][3] = False  # open right side

        # flatten list like your self.map
        flat_map = []
        for row in cells:
            flat_map.extend(row)

        return flat_map
    
    def test_map(self):

        tl = [True, False, True, False] # top left corner
        tr = [True, False, False, True]
        bl = [False, True, True, False]
        br = [False, True, False, True]

        t = [True, False, False, False]
        b = [False, True, False, False]
        l = [False, False, True, False]
        r = [False, False, False, True]

        n = [False, False, False, False]

        mid_test = [False, False, True, True]

        map = []

        for y in range(GLOBAL.GRID_SIZE):
            for x in range(GLOBAL.GRID_SIZE):
                
                if y == 0:
                    if x == 0:
                        map.append(tl)
                    elif x == GLOBAL.GRID_SIZE - 1:
                        map.append(tr)
                    elif x == 5 or x == 4:
                        map.append(n)
                    else:
                        map.append(t)
                elif y == GLOBAL.GRID_SIZE - 1:
                    if x == 0:
                        map.append(bl)
                    elif x == GLOBAL.GRID_SIZE - 1:
                        map.append(br)
                    else:
                        map.append(b)

                elif x == 4 and y == 5:
                    map.append(mid_test)
                elif x == 5 and y == 5:
                    map.append(mid_test)

                else:
                    if x == 0:
                        map.append(l)
                    elif x == GLOBAL.GRID_SIZE - 1:
                        map.append(r)
                    else:
                        map.append(n)

        return map
    