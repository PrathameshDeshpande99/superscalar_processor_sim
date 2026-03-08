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

    def read_word(self, address: bit32) -> bit32:
        assert bit32(0) <= address and (address + bit32(3)) < bit32(self.size), "Memory read out of bounds"
        
        byte1 = self.read(address)
        byte2 = self.read(address + bit32(1))
        byte3 = self.read(address + bit32(2))
        byte4 = self.read(address + bit32(3))

        return bit32(byte1.value << 24 | byte2.value << 16 | byte3.value << 8 | byte4.value)

    def write_word(self, address: bit32, value: bit32):
        assert bit32(0) <= address and (address + bit32(3)) < bit32(self.size), "Memory read out of bounds"

        self.write(address, bit8(value.value >> 24))
        self.write(address + bit32(1), bit8(value.value >> 16))
        self.write(address + bit32(2), bit8(value.value >> 8))
        self.write(address + bit32(3), bit8(value.value))