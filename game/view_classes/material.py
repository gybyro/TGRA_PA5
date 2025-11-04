
from OpenGL.GL import *
from OpenGL.GLU import *
from PIL import Image

class Material:

    __slots__ = ("texture",)


    def __init__(self, filepath):
        self.texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.texture)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        # glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST_MIPMAP_LINEAR)
        # glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        # S=0 : Left                 S=1 : Right
        # T=0 : Top                  T=1 : Bottom

        with Image.open(filepath, mode= "r") as image:
            image_width, image_height = image.size
            image = image.convert("RGBA")
            img_data = bytes(image.tobytes())
            glTexImage2D(GL_TEXTURE_2D,0,GL_RGBA,image_width,image_height,0,GL_RGBA,GL_UNSIGNED_BYTE,img_data)
        glGenerateMipmap(GL_TEXTURE_2D)

    def use(self) -> None:
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D,self.texture)

    def destroy(self) -> None:
        glDeleteTextures(1, (self.texture,))


class RepeatingMaterial(Material):
    """Material that allows texture coordinate scaling for repeating patterns"""
    __slots__ = ("texture_repeat",)

    def __init__(self, filepath, texture_repeat=(1.0, 1.0)):
        # Store how many times the texture repeats
        self.texture_repeat = texture_repeat

        super().__init__(filepath)