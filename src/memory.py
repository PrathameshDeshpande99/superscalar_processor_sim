from utils import bit8, bit32

class Memory:
    def __init__(self, size=4096):
        self.size = size
        self.data = [bit8(0) for _ in range(size)]  # Initialize memory with zeros

    def read(self, address: bit32) -> bit8:
        assert bit32(0) <= address < bit32(self.size), "Memory read out of bounds"
            
        return self.data[address]

    def write(self, address: bit32, value: bit8):
        assert bit32(0) <= address < bit32(self.size), "Memory write out of bounds"

        self.data[address] = value