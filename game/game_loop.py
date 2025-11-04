import glfw
import glfw.GLFW as GLFW_CONSTANTS
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
import pyrr

import config as GLOBAL
from game.scene import Scene
from game.view_classes.graphics_engine import GraphicsEngine


class GameLoop:
    def __init__(self):
        self._set_up_glfw()
        self._set_up_timer()
        self._set_up_input_systems()

        self.scene = Scene()
        self.graph = GraphicsEngine(self.scene)

        self.pressed_key1 = False
        self.pressed_key2 = False
        self.pressed_key3 = False
        self.pressed_key4 = False
        self.pressed_key5 = False

        
        
    def _set_up_glfw(self) -> None:
        glfw.init()
        glfw.window_hint(GLFW_CONSTANTS.GLFW_CONTEXT_VERSION_MAJOR,3)
        glfw.window_hint(GLFW_CONSTANTS.GLFW_CONTEXT_VERSION_MINOR,3)
        glfw.window_hint(
            GLFW_CONSTANTS.GLFW_OPENGL_PROFILE, 
            GLFW_CONSTANTS.GLFW_OPENGL_CORE_PROFILE)
        glfw.window_hint(GLFW_CONSTANTS.GLFW_OPENGL_FORWARD_COMPAT, GLFW_CONSTANTS.GLFW_TRUE)
        #for uncapped framerate
        glfw.window_hint(GLFW_CONSTANTS.GLFW_DOUBLEBUFFER,GL_FALSE) 
        self.window = glfw.create_window(
            GLOBAL.WIDTH, GLOBAL.HEIGHT, "DUNGEON", None, None)
        glfw.make_context_current(self.window)
    
    def _set_up_timer(self) -> None:

        self.last_time = glfw.get_time()
        self.current_time = 0
        self.prev_curr_time = 0
        self.frames_rendered = 0
        self.frametime = 0.0

    def _set_up_input_systems(self) -> None:
        """Configure the mouse and keyboard"""

        glfw.set_input_mode(
            self.window, 
            GLFW_CONSTANTS.GLFW_CURSOR, 
            GLFW_CONSTANTS.GLFW_CURSOR_HIDDEN
        )

        self._keys = {}
        glfw.set_key_callback(self.window, self._key_callback)
    
    def _key_callback(self, window, key, scancode, action, mods) -> None:
        """Handle a key event:
        
            window: the window on which the keypress occurred.
            key: the key which was pressed
            scancode: scancode of the key
            action: action of the key event
            mods: modifiers applied to the event
        """

        state = False
        match action:
            case GLFW_CONSTANTS.GLFW_PRESS:
                state = True
            case GLFW_CONSTANTS.GLFW_RELEASE:
                state = False
            case _:
                return

        self._keys[key] = state
    
    ################################   RUN   ######################################

    def run(self) -> None:

        running = True
        while (running):
            #check pygame events()
            if glfw.window_should_close(self.window) or self._keys.get(GLFW_CONSTANTS.GLFW_KEY_ESCAPE, False):
                running = False

            self._handle_keys()
            self._handle_mouse()
            
            glfw.poll_events()

            self.scene.update(self.frametime / 16.67)
            self.graph.render(self.scene.player, self.scene.entities)

            # timing
            self._calculate_framerate()

    
    ################################   CONTROL   ######################################
    def _handle_keys(self) -> None:


        ############ Debug options ;;;
        # --- 1_KEY toggle  ---  reset player position
        pressed_key1 = self._keys.get(GLFW_CONSTANTS.GLFW_KEY_1, False)
        if pressed_key1 and not self.pressed_key1:
            print(f"player location reset at [5, 20, 2]")

            self.scene.player.position[0] = 5
            self.scene.player.position[1] = 20

            self.pressed_key1 = True
        elif not pressed_key1 and self.pressed_key1:
            self.pressed_key1 = False

        # --- 2_KEY toggle  ---  show hitboxes
        pressed_key2 = self._keys.get(GLFW_CONSTANTS.GLFW_KEY_2, False)
        if pressed_key2 and not self.pressed_key2:
            
            GLOBAL.DEBUG_SHOW_HITBOX = not GLOBAL.DEBUG_SHOW_HITBOX
            print(f"Show Hitboxes = {GLOBAL.DEBUG_SHOW_HITBOX}")

            self.pressed_key2 = True
        elif not pressed_key2 and self.pressed_key2:
            self.pressed_key2 = False

        # --- 3_KEY toggle  ---  enable/disable player hitbox
        pressed_key3 = self._keys.get(GLFW_CONSTANTS.GLFW_KEY_3, False)
        if pressed_key3 and not self.pressed_key3:
            
            GLOBAL.DEBUG_COLLISION = not GLOBAL.DEBUG_COLLISION
            print(f"Player Collision = {GLOBAL.DEBUG_COLLISION}")

            self.pressed_key3 = True
        elif not pressed_key3 and self.pressed_key3:
            self.pressed_key3 = False

        # --- 4_KEY toggle  ---  fly
        pressed_key4 = self._keys.get(GLFW_CONSTANTS.GLFW_KEY_4, False)
        if pressed_key4 and not self.pressed_key4:
            
            GLOBAL.DEBUG_FLY = not GLOBAL.DEBUG_FLY
            print(f"Fly mode = {GLOBAL.DEBUG_FLY}")

            self.pressed_key4 = True
        elif not pressed_key4 and self.pressed_key4:
            self.pressed_key4 = False

        # --- 5_KEY toggle  ---  normals
        # pressed_key5 = self._keys.get(GLFW_CONSTANTS.GLFW_KEY_5, False)
        # if pressed_key5 and not self.pressed_key5:
            
        #     GLOBAL.DEBUG_NORMAL = not GLOBAL.DEBUG_NORMAL
        #     print(f"Show Normals = {GLOBAL.DEBUG_NORMAL}")

        #     self.pressed_key5 = True
        # elif not pressed_key5 and self.pressed_key5:
        #     self.pressed_key5 = False


        ############ Move Player ;;;
        rate = 0.005*self.frametime
        d_pos = np.zeros(3, dtype=np.float32)

        if self._keys.get(GLFW_CONSTANTS.GLFW_KEY_W, False):
            d_pos += GLOBAL.X
        if self._keys.get(GLFW_CONSTANTS.GLFW_KEY_A, False):
            d_pos -= GLOBAL.Y
        if self._keys.get(GLFW_CONSTANTS.GLFW_KEY_S, False):
            d_pos -= GLOBAL.X
        if self._keys.get(GLFW_CONSTANTS.GLFW_KEY_D, False):
            d_pos += GLOBAL.Y

        length = pyrr.vector.length(d_pos)
        if abs(length) < 0.00001:
            return

        d_pos = rate * d_pos / length
        self.scene.move_player(d_pos)

        

                        

    def _handle_mouse(self) -> None:

        (x,y) = glfw.get_cursor_pos(self.window)
        d_eulers = 0.05 * ((GLOBAL.WIDTH / 2) - x) * GLOBAL.Z
        d_eulers += 0.05 * ((GLOBAL.HEIGHT / 2) - y) * GLOBAL.Y
        self.scene.spin_player(d_eulers)
        
        # Center the mouse
        glfw.set_cursor_pos(self.window, GLOBAL.WIDTH / 2, GLOBAL.HEIGHT / 2)

    ################################   COLLISION   ######################################

    def collides_sphere_aabb(self, center, radius, aabb_min, aabb_max):

        # clamp each coordinate of sphere center to AABB
        closest = np.maximum(aabb_min, np.minimum(center, aabb_max))
        # distance squared from sphere center to closest point
        dist_sq = np.sum((closest - center) ** 2)
        return dist_sq < radius ** 2


    def _calculate_framerate(self) -> None:
        """Calculate the framerate and frametime,
            and update the window title.
        """

        self.current_time = glfw.get_time()
        delta = self.current_time - self.last_time
        if (delta >= 1):
            framerate = max(1,int(self.frames_rendered/delta))
            glfw.set_window_title(self.window, f"Running at {framerate} fps.")
            self.last_time = self.current_time
            self.frames_rendered = -1
            self.frametime = float(1000.0 / max(1,framerate))
        self.frames_rendered += 1

        # for me - makes sure that buttons have times??
        if self.current_time -0.01 > self.prev_curr_time:
            self.prev_curr_time = self.current_time

    def quit(self) -> None:
        self.graph.destroy()
        quit()


if __name__ == "__main__":
    myGame = GameLoop()
    myGame.run()
    myGame.quit()