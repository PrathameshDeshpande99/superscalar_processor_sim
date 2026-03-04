from utils import bit32

class Registers:
    def __init__(self):
        self.registers = [bit32(0) for _ in range(32)]  # Initialize 32 registers with zeros
    
    def read(self, index: bit5) -> bit32:
        return self.registers[index]
    
    def write(self, index: bit5, value: bit32):
        self.registers[index] = value