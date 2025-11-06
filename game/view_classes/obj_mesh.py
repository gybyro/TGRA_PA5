from OpenGL.GL import *
from OpenGL.GLU import *

import os
from typing import Dict, List, Optional
import numpy as np

from PIL import Image    # pip install pillow

# Vertex layout: x,y,z, s,t, nx,ny,nz  -> 8 floats (32 bytes)

def load_mtl(mtl_path: str) -> Dict[str, str]:
    """Return map: material_name -> texture_filename (map_Kd).
       Returns relative path as given in mtl.
    """
    mats = {}
    if not os.path.isfile(mtl_path):
        return mats
    current = None
    with open(mtl_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split(None, 1)
            if not parts:
                continue
            key = parts[0]
            rest = parts[1].strip() if len(parts) > 1 else ""
            if key == "newmtl":
                current = rest
            elif key == "map_Kd" and current:
                # map_Kd may contain spaces (rare) — keep as is
                mats[current] = rest
    return mats

def load_obj_split(obj_path: str) -> Dict[str, dict]:
    """
    Load an OBJ and split into sub-objects keyed by 'o' or generated name.
    Returns dict: name -> {"vertices": flattened list, "material": material_name}
    """
    v: List[List[float]] = []
    vt: List[List[float]] = []
    vn: List[List[float]] = []

    objects = {}
    current_name = "default"
    current_material: Optional[str] = None
    vertices: List[float] = []

    def flush_current():
        nonlocal vertices, current_name, current_material
        if vertices:
            objects[current_name] = {"vertices": vertices, "material": current_material}
            vertices = []

    with open(obj_path, "r", encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split()
            token = parts[0]
            if token == "o":
                flush_current()
                current_name = parts[1] if len(parts) > 1 else "unnamed"
                current_material = None
            elif token == "g":
                # group, treat like 'o' if you want
                flush_current()
                current_name = parts[1] if len(parts) > 1 else "group"
                current_material = None
            elif token == "usemtl":
                current_material = parts[1] if len(parts) > 1 else current_material
            elif token == "v":
                v.append([float(x) for x in parts[1:4]])
            elif token == "vt":
                vt.append([float(x) for x in parts[1:3]])
            elif token == "vn":
                vn.append([float(x) for x in parts[1:4]])
            elif token == "f":
                # triangulate polygon (fan)
                # face fields can be: v, v/vt, v//vn, v/vt/vn
                face = parts[1:]
                # for each triangle in fan
                for i in range(1, len(face) - 1):
                    tri = [face[0], face[i], face[i+1]]
                    for corner in tri:
                        # split indices
                        idx_parts = corner.split("/")
                        vi = int(idx_parts[0]) - 1 if idx_parts[0] != "" else None
                        vti = int(idx_parts[1]) - 1 if len(idx_parts) > 1 and idx_parts[1] != "" else None
                        vni = int(idx_parts[2]) - 1 if len(idx_parts) > 2 and idx_parts[2] != "" else None

                        # append position
                        if vi is None or vi < 0 or vi >= len(v):
                            raise ValueError(f"Invalid vertex index {idx_parts[0]} in {obj_path}")
                        vertices.extend(v[vi])

                        # append texcoord (use 0,0 if missing)
                        if vti is not None and 0 <= vti < len(vt):
                            vertices.extend(vt[vti])
                        else:
                            vertices.extend([0.0, 0.0])

                        # append normal (use 0,0,1 if missing)
                        if vni is not None and 0 <= vni < len(vn):
                            vertices.extend(vn[vni])
                        else:
                            vertices.extend([0.0, 0.0, 1.0])

    flush_current()
    return objects

def create_texture_from_file(path: str) -> int:
    """Simple texture loader (returns GL texture id). Uses PIL."""
    if not os.path.isfile(path):
        raise FileNotFoundError(path)
    img = Image.open(path).convert("RGBA")
    img_data = img.tobytes("raw", "RGBA", 0, -1)
    w, h = img.size

    tex = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, tex)
    glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, w, h, 0, GL_RGBA, GL_UNSIGNED_BYTE, img_data)
    glGenerateMipmap(GL_TEXTURE_2D)

    # reasonable defaults
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)

    glBindTexture(GL_TEXTURE_2D, 0)
    return tex

class CoolObjMesh:
    """Multi-submesh OBJ loader. Each submesh has its own VAO/VBO/texture."""
    def __init__(self, obj_path: str, mtl_path: Optional[str] = None, base_dir: Optional[str] = None):
        """
        obj_path: full path to .obj
        mtl_path: full path to .mtl (optional; if None tries to find .mtl next to obj)
        base_dir: optional base directory to resolve texture file paths (defaults to obj dir)
        """
        self.submeshes = []  # list of dicts: {"vao", "vbo", "vertex_count", "tex_id" or None}
        if base_dir is None:
            base_dir = os.path.dirname(obj_path)

        if mtl_path is None:
            # try to find mtllib inside obj to determine .mtl, but simpler: look for same basename
            guess = os.path.splitext(obj_path)[0] + ".mtl"
            mtl_path = guess if os.path.isfile(guess) else None

        materials = load_mtl(mtl_path) if mtl_path else {}

        obj_data = load_obj_split(obj_path)
        for name, info in obj_data.items():
            arr = np.array(info["vertices"], dtype=np.float32)
            vertex_count = arr.size // 8
            # create VAO + VBO
            vao = glGenVertexArrays(1)
            vbo = glGenBuffers(1)
            glBindVertexArray(vao)
            glBindBuffer(GL_ARRAY_BUFFER, vbo)
            glBufferData(GL_ARRAY_BUFFER, arr.nbytes, arr, GL_STATIC_DRAW)

            # attribute pointers (match Mesh layout)
            # position (location 0) 3 floats, offset 0
            glEnableVertexAttribArray(0)
            glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 8 * 4, ctypes.c_void_p(0))
            # texcoord (location 1) 2 floats, offset 12
            glEnableVertexAttribArray(1)
            glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 8 * 4, ctypes.c_void_p(3 * 4))
            # normal (location 2) 3 floats, offset 20
            glEnableVertexAttribArray(2)
            glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, 8 * 4, ctypes.c_void_p(5 * 4))

            glBindVertexArray(0)
            glBindBuffer(GL_ARRAY_BUFFER, 0)

            # texture: lookup from materials map by the 'material' stored
            tex_id = None
            mat_name = info.get("material")
            if mat_name and materials.get(mat_name):
                tex_file = materials[mat_name]
                tex_path = tex_file
                # If the map_Kd in mtl is relative, join with base_dir
                if not os.path.isabs(tex_file):
                    tex_path = os.path.join(base_dir, tex_file)
                try:
                    tex_id = create_texture_from_file(tex_path)
                except Exception as e:
                    print(f"[CoolObjMesh] failed to load texture '{tex_path}': {e}")
                    tex_id = None

            self.submeshes.append({
                "name": name,
                "vao": vao,
                "vbo": vbo,
                "vertex_count": vertex_count,
                "tex_id": tex_id,
                "mat_name": mat_name
            })

    def arm_for_drawing(self):
        # nothing global to bind (each submesh has own VAO)
        pass

    def draw(self):
        # draw each submesh
        for sm in self.submeshes:
            glBindVertexArray(sm["vao"])
            if sm["tex_id"]:
                glActiveTexture(GL_TEXTURE0)
                glBindTexture(GL_TEXTURE_2D, sm["tex_id"])
            glDrawArrays(GL_TRIANGLES, 0, sm["vertex_count"])
        glBindVertexArray(0)
        glBindTexture(GL_TEXTURE_2D, 0)

    def destroy(self):
        for sm in self.submeshes:
            glDeleteVertexArrays(1, (sm["vao"],))
            glDeleteBuffers(1, (sm["vbo"],))
            if sm["tex_id"]:
                glDeleteTextures([sm["tex_id"]])



######################## old

# def load_obj(filename: str) -> list[float]:

#     v, vt, vn = [], [], []

#     objects = {}
#     current_object = "default"
#     current_material = None
#     vertices = []

#     with open(filename) as f:
#         for line in f:
#             line = line.strip()
#             if not line or line.startswith("#"):
#                 continue
#             words = line.split()
#             match words[0]:
#                 case "o":
#                     # save previous object
#                     if vertices:
#                         objects[current_object] = {"vertices": vertices, "material": current_material}
#                         vertices = []
#                     current_object = words[1]
#                 case "usemtl":
#                     current_material = words[1]
#                 case "v":
#                     v.append([float(x) for x in words[1:4]])
#                 case "vt":
#                     vt.append([float(x) for x in words[1:3]])
#                 case "vn":
#                     vn.append([float(x) for x in words[1:4]])
#                 case "f":
#                     for i in range(1, len(words)-2):
#                         for corner in [words[1], words[i+1], words[i+2]]:
#                             indices = [int(idx) if idx else 0 for idx in corner.split("/")]
#                             vi = indices[0]-1
#                             vti = indices[1]-1
#                             vni = indices[2]-1
#                             vertices.extend(v[vi])
#                             vertices.extend(vt[vti])
#                             vertices.extend(vn[vni])
#     if vertices:
#         objects[current_object] = {"vertices": vertices, "material": current_material}
    
#     return objects

# def load_mtl(filename: str) -> dict[str, str]:
#     """
#     Load MTL file to map material names to texture filenames.
#     Returns:
#         dict: material_name -> texture_file
#     """
#     materials = {}
#     current_mat = None
#     with open(filename) as f:
#         for line in f:
#             line = line.strip()
#             if not line or line.startswith("#"):
#                 continue
#             words = line.split()
#             match words[0]:
#                 case "newmtl":
#                     current_mat = words[1]
#                 case "map_Kd":
#                     if current_mat:
#                         materials[current_mat] = words[1]
#     return materials


# class CoolObjMesh(Mesh):
#     """Support multiple objects in one OBJ with separate materials."""

#     def __init__(self, rout: str, file_name: str):
#         super().__init__()
#         self.submeshes = []  # each submesh: (vertices array, material texture)
        
#         obj_file = rout + file_name + ".obj"
#         mtl_file = rout + file_name + ".mtl"

#         obj_data = load_obj(obj_file)
#         materials = load_mtl(mtl_file)
        
#         for obj_name, data in obj_data.items():
#             vertices = np.array(data["vertices"], dtype=np.float32)
#             texture_file = materials.get(data["material"], None)
#             self.submeshes.append({
#                 "vertices": vertices,
#                 "vertex_count": len(vertices)//8,
#                 "texture": rout + texture_file
#             })
