import numpy as np
from game.model_classes.entity import Entity
from game.model_classes.billboard import Billboard

#class Light(Billboard):
class Light(Entity):
    """yagami???"""

    __slots__ = ("color", "strength")

    def __init__(self, 
                 position: list[float],
                 color: list[float] = [1,1,1],
                 strength: float = 10
                 ):
        super().__init__(position) # inherits from Entity
        self.color = np.array(color, dtype=np.float32)
        self.strength = strength
