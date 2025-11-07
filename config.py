import numpy as np

################### Debug menu
DEBUG_COLLISION = True
DEBUG_SHOW_HITBOX = False
DEBUG_FLY = False
DEBUG_FLAT_WALLS = False
DEBUG_GENERATE_MAZE = False
DEBUG_NORMAL = False

RES = WIDTH, HEIGHT = 1400, 800
FPS = 60

TEST_VIEWS = [
    
]

############################## Constants ######################################

X = np.array([1,0,0], dtype=np.float32)
Y = np.array([0,1,0], dtype=np.float32)
Z = np.array([0,0,1], dtype=np.float32)

GROUND_W = 50 # world units I think
GROUND_H = 50
GRID_SIZE = 10 # 10x10
WALL_H = 5
WALL_D = 1

PLAYER_W = 1
PLAYER_H = 2

COLLIDERS = []
PLAYER_RADIUS = 1.5

ENTITY_TYPE = {
    "CUBE": 0,
    "POINTLIGHT": 1,
    "GROUND": 2,
    "3D_WALL": 4,
    "MAXWELL": 5,
    "WHISK": 6,
    "MAXLIGHT": 7,
    "BILLBOARD": 8,
}

UNIFORM_TYPE = {
    "MODEL": 0,
    "VIEW": 1,
    "PROJECTION": 2,
    "CAMERA_POS": 3,
    "LIGHT_COLOR": 4,
    "LIGHT_POS": 5,
    "LIGHT_STRENGTH": 6,
}