import numpy as np
import pyrr
import config as GLOBAL


class Entity:
    """A basic object in the world, with a position and rotation.
    """
    __slots__ = ("position", "rotation", "scale", "id")

    def __init__(self, 
                 position: list[float] = [0,0,0],
                 rotation: list[float] = [0,0,0], 
                    scale: list[float] = [1,1,1]
                    ):

        # the position of the entity.
        self.position = np.array(position, dtype=np.float32)

        # the rotation of the entity about each axis.
        self.rotation = np.array(rotation, dtype=np.float32)

        # the scale of the entity.
        self.scale = np.array(scale, dtype=np.float32)

        self.id = ""

    def update(self, dt: float) -> None:
        """For child classes
            dt: framerate correction factor.
        """
        pass

    def _get_rotations(self, model_transform):

        # rotations:::::
        model_transform = pyrr.matrix44.multiply(         # X-axis  
            m1=model_transform,
            m2=pyrr.matrix44.create_from_axis_rotation(
                axis = GLOBAL.X,
                theta = np.radians(self.rotation[0]),
                dtype = np.float32
            )
        )
        model_transform = pyrr.matrix44.multiply(         # Y-axis  
            m1=model_transform,
            m2=pyrr.matrix44.create_from_axis_rotation(
                axis = GLOBAL.Y,
                theta = np.radians(self.rotation[1]),
                dtype = np.float32
            )
        )
        model_transform = pyrr.matrix44.multiply(         # Z-axis  
            m1=model_transform,
            m2=pyrr.matrix44.create_from_axis_rotation(
                axis = GLOBAL.Z,
                theta = np.radians(self.rotation[2]),
                dtype = np.float32
            )
        )
        return model_transform


    def get_model_transform(self) -> np.ndarray:
        """Returns the entity's model to world transformation matrix."""
        
        model_transform = pyrr.matrix44.create_identity(dtype=np.float32)

        model_transform = self._get_rotations(model_transform)

        # Scale transformation :::
        model_transform = pyrr.matrix44.multiply(
            m1=model_transform, 
            m2=pyrr.matrix44.create_from_scale(
                self.scale
            )
        )

        return pyrr.matrix44.multiply(
            m1=model_transform, 
            m2=pyrr.matrix44.create_from_translation(
                vec=np.array(self.position),dtype=np.float32
            )
        )
    
    def get_normal_matrix(self) -> np.ndarray:
        """ Returns a 3x3 normal matrix (inverse-transpose of the upper-left 3x3 of model matrix)
        for transforming normals from local to world space.
        """
        # model_transform = pyrr.matrix44.create_identity(dtype=np.float32)
        # normal_matrix = self._get_rotations(model_transform)

        # # normal_matrix = np.linalg.inv(model[:3,:3]).T
        # return normal_matrix.astype(np.float32)

        model = self.get_model_transform()       # 4x4 model matrix
        normal_matrix = np.linalg.inv(model[:3,:3]).T
        return normal_matrix.astype(np.float32)
    
