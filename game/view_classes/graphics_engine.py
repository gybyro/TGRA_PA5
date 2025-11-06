
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
import pyrr

import config as GLOBAL
from game.model_classes.entity import Entity
from game.model_classes.camera import Camera
from game.view_classes.material import Material, RepeatingMaterial
from game.model_classes.light import Light
from game.view_classes.mesh import Mesh, RectMesh, CubeMesh
from game.view_classes.obj_mesh import CoolObjMesh
from game.scene import Scene
from OpenGL.GL.shaders import compileProgram,compileShader

from game.view_classes.skybox import Skybox

#####
from game.model_classes.plane import Plane

def create_shader(vertex_filepath: str, fragment_filepath: str) -> int:
    """Compile and link shader modules to make a shader program.
        Parameters:
            vertex_filepath: path to the text file storing the vertex source code
            fragment_filepath: path to the text file storing the fragment source code
        Returns:
            A handle to the created shader programs
    """
    with open(vertex_filepath,'r') as f:
        vertex_src = f.readlines()

    with open(fragment_filepath,'r') as f:
        fragment_src = f.readlines()
    
    shader = compileProgram(
        compileShader(vertex_src, GL_VERTEX_SHADER),
        compileShader(fragment_src, GL_FRAGMENT_SHADER)
    )
    return shader


class GraphicsEngine:

    def __init__(self, scene: Scene):
        self.scene = scene
        
        ### initiate OpenGL

        # glClearColor(0.1, 0.2, 0.2, 1.0) # change screen background
        glClearColor(0.6, 0.8, 1.0, 1.0) # #99CCFF - skyblue

        glEnable(GL_DEPTH_TEST)
        # glEnable(GL_CULL_FACE)
        # glCullFace(GL_BACK)
        glEnable(GL_BLEND) # enable alpha transperancy 
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA) # enable alpha transperancy 

        self._create_assets()
        
        ### Some shader data only needs to be set once.
        if GLOBAL.DEBUG_NORMAL:
            self.shader = self.shader_normals
        else:
            self.shader = self.shader_light

        glUseProgram(self.shader)
        glUniform1i(glGetUniformLocation(self.shader, "imageTexture"), 0)

        

        # set up the projection transform
        self.current_fov = 45.0
        self.projection_transform = pyrr.matrix44.create_perspective_projection(
            fovy = self.current_fov,
            aspect = GLOBAL.WIDTH/GLOBAL.HEIGHT,
            near = 0.1, 
            far = 100, 
            dtype=np.float32
        )
        # then send that over to the shader
        glUniformMatrix4fv(
            glGetUniformLocation(self.shader,"projection"),
            1, GL_FALSE, self.projection_transform
        )
        
        
        self._get_uniform_locations()
    
    def _create_assets(self) -> None:

        # this is a dict containing all the obj meshes, (each one has its own folder plz)
        self.objects = [
            CoolObjMesh(
                "res/3D_models/maxwell/maxwell.54d410c0.obj", 
                "res/3D_models/maxwell/maxwell.54d410c0.mtl"),
        ]

        # meshes that dont use objs
        self.meshes: dict[int, Mesh] = {
            GLOBAL.ENTITY_TYPE["GROUND"]: RectMesh(w = GLOBAL.GROUND_W, h = GLOBAL.GROUND_H),
            GLOBAL.ENTITY_TYPE["WALL"]: RectMesh(w = GLOBAL.GROUND_W / GLOBAL.GRID_SIZE, h = GLOBAL.WALL_H),
            GLOBAL.ENTITY_TYPE["3D_WALL"]: CubeMesh(w= GLOBAL.GROUND_W / GLOBAL.GRID_SIZE, d= GLOBAL.WALL_D, h= GLOBAL.WALL_H),
            GLOBAL.ENTITY_TYPE["POINTLIGHT"]: CubeMesh(w= 0.2, d= 0.2, h= 0.2),
            GLOBAL.ENTITY_TYPE["MAXLIGHT"]: CubeMesh(w= 0.2, d= 0.2, h= 0.2),
        }
        # non obj meshes need to be bound to textures
        self.materials: dict[int, Material] = {
            GLOBAL.ENTITY_TYPE["GROUND"]: RepeatingMaterial("res/images/tile.png", texture_repeat=(GLOBAL.GRID_SIZE, GLOBAL.GRID_SIZE)),
            GLOBAL.ENTITY_TYPE["WALL"]: Material("res/images/gojji_snek.png"),
            GLOBAL.ENTITY_TYPE["3D_WALL"]: Material("res/images/wood_albedo.png"),
            GLOBAL.ENTITY_TYPE["POINTLIGHT"]: Material("res/images/white.png"),
            GLOBAL.ENTITY_TYPE["MAXLIGHT"]: Material("res/images/skybox.png"),
        }

        self.shader_light = create_shader("res/shaders/vertex.vert", "res/shaders/fragment.frag")
        self.shader_normals = create_shader("res/shaders/vertex.vert", "res/shaders/normal_frag.frag")
        
        # Skybox
        self.skybox_shader = create_shader("res/shaders/skybox.vert", "res/shaders/skybox.frag")
        skybox_faces = [
            "res/images/skybox_top.png",
            "res/images/skybox_top.png",
            "res/images/skybox_top.png",
            "res/images/skybox_top.png",
            "res/images/skybox_top.png",
            "res/images/skybox_top.png",
        ]
        self.skybox = Skybox(self.skybox_shader, skybox_faces)
        

    def _get_uniform_locations(self) -> None:
        """Query and store the locations of shader uniforms"""

        # glUseProgram(self.shader)
        
        self.uniform_locations: dict[int, int] = {
            GLOBAL.UNIFORM_TYPE["CAMERA_POS"]: glGetUniformLocation(
                self.shader, "cameraPosition"),
            GLOBAL.UNIFORM_TYPE["MODEL"]: glGetUniformLocation(self.shader, "model"),
            GLOBAL.UNIFORM_TYPE["VIEW"]: glGetUniformLocation(self.shader, "view"),
        }

        self.light_locations: dict[int, list[int]] = {
            GLOBAL.UNIFORM_TYPE["LIGHT_COLOR"]: [
                glGetUniformLocation(self.shader, f"Lights[{i}].color")
                for i in range(8)
            ],
            GLOBAL.UNIFORM_TYPE["LIGHT_POS"]: [
                glGetUniformLocation(self.shader, f"Lights[{i}].position")
                for i in range(8)
            ],
            GLOBAL.UNIFORM_TYPE["LIGHT_STRENGTH"]: [
                glGetUniformLocation(self.shader, f"Lights[{i}].strength")
                for i in range(8)
            ],
        }



    def render(self, camera: Camera, renderables: dict[int, list[Entity]]) -> None:

        #refresh screen
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        if GLOBAL.DEBUG_NORMAL:
            glUseProgram(self.shader_normals)
            self.shader = self.shader_normals
        else:
            glUseProgram(self.shader_light)
            self.shader = self.shader_light


        # set camera uniforms
        glUniformMatrix4fv(
            self.uniform_locations[GLOBAL.UNIFORM_TYPE["VIEW"]], 
            1, GL_FALSE, camera.get_view_transform()
        )
        glUniform3fv(
            self.uniform_locations[GLOBAL.UNIFORM_TYPE["CAMERA_POS"]],
            1, camera.position
        )
 

        # draw all the entities
        for entity_type, entities in renderables.items():
            if entity_type not in self.meshes:
                continue

            mesh = self.meshes[entity_type]
            material = self.materials[entity_type]
            mesh.arm_for_drawing()
            material.use() # bind material and texture

            # set texture repeat for this material type
            tex_repeat_loc = glGetUniformLocation(self.shader, "uTexRepeat")
            if isinstance(material, RepeatingMaterial):
                glUniform2f(tex_repeat_loc, *material.texture_repeat)
            else:
                glUniform2f(tex_repeat_loc, 1.0, 1.0)

            for entity in entities:
                glUniformMatrix4fv(
                    self.uniform_locations[GLOBAL.UNIFORM_TYPE["MODEL"]],
                    1, GL_FALSE, entity.get_model_transform()
                )
                if entity.id != "MAXWELL":
                    normal_matrix_loc = glGetUniformLocation(self.shader, "normalMatrix")
                    glUniformMatrix3fv(normal_matrix_loc, 1, GL_TRUE, entity.get_normal_matrix())
               
                
                mesh.draw()

        ######### draw obj meshes
        for object in self.objects:

            glUniformMatrix4fv(
                self.uniform_locations[GLOBAL.UNIFORM_TYPE["MODEL"]],
                1, GL_FALSE, renderables[GLOBAL.ENTITY_TYPE["MAXWELL"]][0].get_model_transform()
            )
            object.draw()


        ######### lighting
        for i in range(len(renderables[GLOBAL.ENTITY_TYPE["POINTLIGHT"]])):
            if i == 0:
                light: Light = renderables[GLOBAL.ENTITY_TYPE["MAXLIGHT"]][0]
            else:
                light: Light = renderables[GLOBAL.ENTITY_TYPE["POINTLIGHT"]][i]

            glUniform3fv(
                self.light_locations[GLOBAL.UNIFORM_TYPE["LIGHT_POS"]][i], 
                1, light.position
            )
            glUniform3fv(
                self.light_locations[GLOBAL.UNIFORM_TYPE["LIGHT_COLOR"]][i], 
                1, light.color
            )
            glUniform1f(
                self.light_locations[GLOBAL.UNIFORM_TYPE["LIGHT_STRENGTH"]][i], 
                light.strength
            )


        glFlush()

    def destroy(self) -> None:
        for mesh in self.meshes.values():
            mesh.destroy()
        for material in self.materials.values():
            material.destroy()
        glDeleteProgram(self.shader)

    
