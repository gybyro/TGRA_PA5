import glfw
import glfw.GLFW as GLFW_CONSTANTS
from openal import oalInit, oalQuit, oalOpen, Listener
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
import pyrr
import time

import config as GLOBAL
from game.scene import Scene
from game.view_classes.graphics_engine import GraphicsEngine


class GameLoop:
    def __init__(self):
        self._set_up_glfw()
        self._set_up_timeline()
        self._set_up_input_systems()

        self.scene = Scene()
        self.graph = GraphicsEngine(self.scene)

        self.pressed_key1 = False

        
        
    def _set_up_glfw(self) -> None:
        glfw.init()
        glfw.window_hint(GLFW_CONSTANTS.GLFW_CONTEXT_VERSION_MAJOR,3)
        glfw.window_hint(GLFW_CONSTANTS.GLFW_CONTEXT_VERSION_MINOR,3)
        glfw.window_hint(
            GLFW_CONSTANTS.GLFW_OPENGL_PROFILE, 
            GLFW_CONSTANTS.GLFW_OPENGL_CORE_PROFILE)
        glfw.window_hint(GLFW_CONSTANTS.GLFW_OPENGL_FORWARD_COMPAT, GLFW_CONSTANTS.GLFW_TRUE)

        glfw.window_hint(GLFW_CONSTANTS.GLFW_DOUBLEBUFFER,GL_FALSE) 
        self.window = glfw.create_window(
            GLOBAL.WIDTH, GLOBAL.HEIGHT, "DUNGEON", None, None)
        
        # antialiasing - not pixelated
        glfw.window_hint(glfw.SAMPLES, 4)  # Request 4x MSAA

        glfw.make_context_current(self.window)

    def _set_up_openAl(self) -> None:
        # Initialize OpenAL
        oalInit()
    
    def _set_up_timeline(self) -> None:

        self.fps = 24    # to be 24fps
        self.frame_durr = 1.0 / self.fps
        self.current_frame = 0
        self.start_time = time.time()

    def _set_up_input_systems(self) -> None:
        """Configure the mouse and keyboard"""

        glfw.set_input_mode(
            self.window, 
            GLFW_CONSTANTS.GLFW_CURSOR, 
            # GLFW_CONSTANTS.GLFW_CURSOR_NORMAL
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

            glfw.poll_events() # for event handling




            # Render new frame every 0.0417 or 24 frames per second
            elapsed = time.time() - self.start_time
            target_frame = int(elapsed * self.fps)
            glfw.set_window_title(self.window, f"frame: {self.current_frame}")

            if target_frame > self.current_frame:
                delta_frames = target_frame - self.current_frame
                self.current_frame = target_frame

                delta_time = delta_frames / self.fps if self.fps > 0 else 0.0

                self.scene.update(self.current_frame, delta_time)
                self.graph.render(self.scene.player, self.scene.entities)

    
    ################################   CONTROL   ######################################
    def _handle_keys(self) -> None:

        pressed_key1 = self._keys.get(GLFW_CONSTANTS.GLFW_KEY_SPACE, False)
        if pressed_key1 and not self.pressed_key1:

            self.scene.cycle_camera_view()

            self.pressed_key1 = True
        elif not pressed_key1 and self.pressed_key1:
            self.pressed_key1 = False

    
    def _handle_mouse(self) -> None:
        x, y = glfw.get_cursor_pos(self.window)

        # how far we moved from window center
        dx = (GLOBAL.WIDTH / 2)  - x
        dy = (GLOBAL.HEIGHT / 2) - y

        sensitivity = 0.1  # adjust to taste
        
        d_yaw   = dx * sensitivity # rotation[1]
        d_pitch = dy * sensitivity # rotation[2]

        # build Euler delta vector: (roll, yaw, pitch)
        d_eulers = np.array([0.0, -d_yaw, d_pitch], dtype=np.float32)

        # apply to camera
        self.scene.spin_player(d_eulers)

        # re-center cursor
        glfw.set_cursor_pos(self.window, GLOBAL.WIDTH / 2, GLOBAL.HEIGHT / 2)

    # def _handle_mouse(self) -> None:

    #     (x,y) = glfw.get_cursor_pos(self.window)
    #     d_eulers = 0.05 * ((GLOBAL.WIDTH / 2) - x) * GLOBAL.Z
    #     d_eulers += 0.05 * ((GLOBAL.HEIGHT / 2) - y) * GLOBAL.Y
    #     self.scene.spin_player(d_eulers)
        
    #     # Center the mouse
    #     glfw.set_cursor_pos(self.window, GLOBAL.WIDTH / 2, GLOBAL.HEIGHT / 2)

    ################################   COLLISION   ######################################

    # def collides_sphere_aabb(self, center, radius, aabb_min, aabb_max):

    #     # clamp each coordinate of sphere center to AABB
    #     closest = np.maximum(aabb_min, np.minimum(center, aabb_max))
    #     # distance squared from sphere center to closest point
    #     dist_sq = np.sum((closest - center) ** 2)
    #     return dist_sq < radius ** 2


    # def _calculate_framerate(self) -> None:
    #     """ Render new frame every 0.0417 or 24 frames per second
    #     """

        # self.current_time = glfw.get_time()
        # delta = self.current_time - self.last_time
        # if (delta >= 1):
        #     framerate = max(1,int(self.frames_rendered/delta))
        #     glfw.set_window_title(self.window, f"Running at {framerate} fps.")
        #     self.last_time = self.current_time
        #     self.frames_rendered = -1
        #     self.frametime = float(1000.0 / max(1,framerate))
        # self.frames_rendered += 1

    def quit(self) -> None:
        self.graph.destroy()
        oalQuit()
        quit()


if __name__ == "__main__":
    myGame = GameLoop()
    myGame.run()
    myGame.quit()