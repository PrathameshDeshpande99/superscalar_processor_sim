"""
Module defining the memory representation for the superscalar processor.
"""

from utils import bit8, bit32

class Memory:
    """
    Main memory representing byte-addressable storage for the processor.
    """
    def __init__(self, size=4096):
        """
        Initialize the memory with a specific size.

        Args:
            size (int): The total number of bytes in memory (default 4096).
        """
        self.size = size
        self.data = [bit8(0) for _ in range(size)]  # Initialize memory with zeros

    def read(self, address: bit32) -> bit8:
        """
        Read a single byte from memory.

        Args:
            address (bit32): The 32-bit address to read from.

        Returns:
            bit8: The 8-bit value at the given address.
        """
        assert bit32(0) <= address < bit32(self.size), "Memory read out of bounds"
            
        return self.data[address]

    def write(self, address: bit32, value: bit8):
        """
        Write a single byte to memory.

        Args:
            address (bit32): The 32-bit address to write to.
            value (bit8): The 8-bit value to store at the address.
        """
        assert bit32(0) <= address < bit32(self.size), "Memory write out of bounds"

        self.data[address] = value

    def read_word(self, address: bit32) -> bit32:
        """
        Read a 32-bit word (4 bytes) from memory. Assumes Big Endian format.

        Args:
            address (bit32): The starting 32-bit address.

        Returns:
            bit32: The 32-bit word read from memory.
        """
        assert bit32(0) <= address and (address + bit32(3)) < bit32(self.size), "Memory read out of bounds"
        
        byte1 = self.read(address)
        byte2 = self.read(address + bit32(1))
        byte3 = self.read(address + bit32(2))
        byte4 = self.read(address + bit32(3))

        return bit32(byte1.value << 24 | byte2.value << 16 | byte3.value << 8 | byte4.value)

    def write_word(self, address: bit32, value: bit32):
        """
        Write a 32-bit word (4 bytes) to memory. Assumes Big Endian format.

        Args:
            address (bit32): The starting 32-bit address.
            value (bit32): The 32-bit word to write to memory.
        """
        assert bit32(0) <= address and (address + bit32(3)) < bit32(self.size), "Memory read out of bounds"
        self.write(address, bit8(value.value >> 24))
        self.write(address + bit32(1), bit8(value.value >> 16))
        self.write(address + bit32(2), bit8(value.value >> 8))
        self.write(address + bit32(3), bit8(value.value))

    def print_memory(self):
        """
        Print the contents of a specific memory segment (base 1024).
        """
        # base address = 1024
        # print 20 words after 1024
        def print_memory(self, base=1024):
            for i in range(base, base + 20 * 4, 4):
                print(f"Address {i}: {self.read_word(bit32(i)).value}")