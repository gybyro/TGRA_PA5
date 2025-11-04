from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
import pyrr

class Buffer:
    """Storage buffer, holds arbitrary homogenous data"""

    __slots__ = (
        "size", "binding", "element_count", 
        "dtype", "host_memory", "device_memory", 
        "elements_updated")
    

    def __init__(self, size: int, binding: int, element_count: int, dtype: np.dtype):
        """ Parameters:
                size: number of entries on the buffer.
                binding: binding index
                element_count: number of elements per entry
        """

        self.size = size
        self.binding = binding
        self.element_count = element_count
        self.dtype = dtype

        self.host_memory = np.zeros(element_count * size, dtype=dtype)

        self.device_memory = glGenBuffers(1)
        glBindBuffer(GL_SHADER_STORAGE_BUFFER, self.device_memory)
        glBufferStorage(
            GL_SHADER_STORAGE_BUFFER, self.host_memory.nbytes, 
            self.host_memory, GL_DYNAMIC_STORAGE_BIT)
        glBindBufferBase(GL_SHADER_STORAGE_BUFFER, binding, self.device_memory)
        self.elements_updated = 0
    
    def record_element(self, i: int, element: np.ndarray) -> None:
        """ Record the given element in position i, if this exceeds the buffer size,
            the buffer is resized.
        """

        if i >= self.size:
            self.resize()

        index = self.element_count * i
        self.host_memory[index : index + self.element_count] = element[:]

        self.elements_updated += 1
    
    def resize(self) -> None:
        """Resize the buffer, uses doubling strategy"""

        self.destroy()
        new_size = self.size * 2

        host_memory = np.zeros(self.element_count * new_size, dtype=self.dtype)
        host_memory[0:self.element_count * self.size] = self.host_memory[:]
        self.host_memory = host_memory
        self.size = new_size

        self.device_memory = glGenBuffers(1)
        glBindBuffer(GL_SHADER_STORAGE_BUFFER, self.device_memory)
        glBufferStorage(
            GL_SHADER_STORAGE_BUFFER, self.host_memory.nbytes, 
            self.host_memory, GL_DYNAMIC_STORAGE_BIT)

    def read_from(self) -> None:
        """Upload the CPU data to the buffer, then arm it for reading"""

        glBindBuffer(GL_SHADER_STORAGE_BUFFER, self.device_memory)
        glBufferSubData(GL_SHADER_STORAGE_BUFFER, 0, self.element_count * 4 * self.elements_updated, self.host_memory)
        glBindBufferBase(GL_SHADER_STORAGE_BUFFER, self.binding, self.device_memory)
        self.elements_updated = 0
    
    def destroy(self) -> None:
        glDeleteBuffers(1, (self.device_memory,))