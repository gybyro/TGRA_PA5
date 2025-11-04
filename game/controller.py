
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
import pyrr

import config as GLOBAL
from game.model_classes.camera import Camera
from game.model_classes.entity import Entity
# from game.view_classes.graphics_engine import GraphicsEngine



class Collision:

    @staticmethod
    def check_move(pos: list[float], new_pos: list[float], collidables: list[Entity]):

        for ob in collidables:
            aabb_min, aabb_max = ob.get_aabb()

            # clamp each coordinate of sphere center to AABB
            closest = np.maximum(aabb_min, np.minimum(new_pos, aabb_max))
            delta = new_pos - closest
            dist_sq = np.sum(delta ** 2)

            # check If player radius is inside collision
            if dist_sq < GLOBAL.PLAYER_RADIUS ** 2:
                return True
        return False
    
    @staticmethod
    def move_max(pos: list[float], new_pos: list[float], collidables: list[Entity]):
        for ob in collidables:
            aabb_min, aabb_max = ob.get_aabb()

                
    
    @staticmethod
    def get_player_move(pos: list[float], new_pos: list[float], collidables: list[Entity]):



        for ob in collidables:
            aabb_min, aabb_max = ob.get_aabb()

            # clamp each coordinate of sphere center to AABB
            closest = np.maximum(aabb_min, np.minimum(new_pos, aabb_max))
            delta = new_pos - closest
            dist_sq = np.sum(delta ** 2)

            # length
            delta_player = new_pos - pos
            if np.linalg.norm(delta_player) > 0:
                push_dir = delta_player / np.linalg.norm(delta_player)
            else:
                push_dir = np.array([0, 0, 0], dtype=np.float32)

            # If player radius is inside wall → block movement
            if dist_sq < GLOBAL.PLAYER_RADIUS ** 2:

                if ob.id == "MAXWELL":

                    floor = ob.position[2] + (push_dir[2] * 1)
                    if floor < -1.9: floor = -1.9 # make sure he dont clip through the floor

                    # push the object away
                    ob.position = [
                        ob.position[0] + (push_dir[0] * 1), 
                        ob.position[1] + (push_dir[1] * 1), 
                        floor
                    ]

                    # max_aabb_min, max_aabb_max = ob.get_aabb()
                    # for ob in collidables:
                    #     wall_aabb_min, wall_aabb_max = ob.get_aabb()
                    #     if Collision.aabb_collision(max_aabb_min, max_aabb_max, wall_aabb_min, wall_aabb_max):
                    #         ob.position = Collision.resolve_aabb_collision(max_aabb_min, max_aabb_max, wall_aabb_min, wall_aabb_max)


                 

                   
                
                else:
                    if np.all(delta == 0):
                        normal = np.array([0, 0, 1], dtype=np.float32)
                    else:
                        normal = delta / np.linalg.norm(delta)
                    
                    # slidey wall
                    move_vec = new_pos - pos
                    move_along_wall = move_vec - np.dot(move_vec, normal) * normal
                    
                    new_pos = pos + move_along_wall

        return new_pos
    
    @staticmethod
    def aabb_collision(min1, max1, min2, max2):
        return (
            min1[0] <= max2[0] and max1[0] >= min2[0] and
            min1[1] <= max2[1] and max1[1] >= min2[1] and
            min1[2] <= max2[2] and max1[2] >= min2[2]
        )
   

    def resolve_aabb_collision(player_min, player_max, obj_min, obj_max):
        """
        Resolves collision between two AABBs.
        Returns the vector to push the player (or object) so they no longer overlap.
        """

        # Compute penetration depth on each axis
        dx1 = obj_max[0] - player_min[0]  # penetration from left
        dx2 = player_max[0] - obj_min[0]  # penetration from right
        dy1 = obj_max[1] - player_min[1]  # bottom
        dy2 = player_max[1] - obj_min[1]  # top
        dz1 = obj_max[2] - player_min[2]  # back
        dz2 = player_max[2] - obj_min[2]  # front

        # penetration values (absolute)
        penetrations = np.array([dx1, dx2, dy1, dy2, dz1, dz2])
        min_pen = np.min(penetrations)
        axis_index = np.argmin(penetrations)

        # push vector initialization
        push = np.zeros(3, dtype=np.float32)

        # determine push direction based on minimum penetration axis
        if axis_index == 0:       # left
            push[0] = -dx1
        elif axis_index == 1:     # right
            push[0] = dx2
        elif axis_index == 2:     # bottom
            push[1] = -dy1
        elif axis_index == 3:     # top
            push[1] = dy2
        elif axis_index == 4:     # back
            push[2] = -dz1
        elif axis_index == 5:     # front
            push[2] = dz2

        return push

    @staticmethod
    def player_move(player: Camera, new_pos, collidables: list[Entity]):

        # if not Collision.check_move(player.position, new_pos, collidables):
        #     return new_pos

        
        player_min, player_max = player.get_hitbox()

        for ob in collidables:

            obj_min, obj_max = ob.get_aabb()

            if Collision.aabb_collision(player_min, player_max, obj_min, obj_max):
                push_vec = Collision.resolve_aabb_collision(player_min, player_max, obj_min, obj_max)

                if ob.id == "MAXWELL":
                    ob.position += push_vec
                else:
                    # collision normal
                    normal = push_vec / (np.linalg.norm(push_vec) + 1e-8)
                    # attempted movement
                    move_vec = new_pos - player.position
                    # project onto plane perpendicular to normal (slide along wall)
                    move_along_wall = move_vec - np.dot(move_vec, normal) * normal
                    new_pos = player.position + move_along_wall

        return new_pos