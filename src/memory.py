"""
Memory module for the superscalar processor simulator.

Implements addressable memory with word (32-bit) and byte (8-bit) access operations.
Uses big-endian byte ordering. Memory is initialized with all zeros.
"""

from utils import bit8, bit32


class Memory:
    """Byte-addressed memory with word-oriented access for the processor simulator."""

    def __init__(self, size: int = 4096):
        """
        Initialize memory with specified size.
        
        Args:
            size: Total memory size in bytes (default: 4096)
        """
        self.size = size
        self.data = [bit8(0) for _ in range(size)]

    def read(self, address: bit32) -> bit8:
        """
        Read a single byte from memory.
        
        Args:
            address: Memory address to read from
        
        Returns:
            bit8: Byte value at the specified address
        
        Raises:
            AssertionError: If address is out of bounds
        """
        assert bit32(0) <= address < bit32(self.size), "Memory read out of bounds"
        return self.data[address]

    def write(self, address: bit32, value: bit8) -> None:
        """
        Write a single byte to memory.
        
        Args:
            address: Memory address to write to
            value: Byte value to write
        
        Raises:
            AssertionError: If address is out of bounds
        """
        assert bit32(0) <= address < bit32(self.size), "Memory write out of bounds"
        self.data[address] = value

    def read_word(self, address: bit32) -> bit32:
        """
        Read a 32-bit word from memory using big-endian byte ordering.
        
        Reads four consecutive bytes starting at the specified address and combines
        them into a 32-bit word: byte0 << 24 | byte1 << 16 | byte2 << 8 | byte3
        
        Args:
            address: Memory address (must be aligned; reads 4 bytes)
        
        Returns:
            bit32: 32-bit word value
        
        Raises:
            AssertionError: If address range is out of bounds
        """
        assert bit32(0) <= address and (address + bit32(3)) < bit32(self.size), \
            "Memory read out of bounds"
        
        byte1 = self.read(address)
        byte2 = self.read(address + bit32(1))
        byte3 = self.read(address + bit32(2))
        byte4 = self.read(address + bit32(3))

        return bit32(byte1.value << 24 | byte2.value << 16 | byte3.value << 8 | byte4.value)

    def write_word(self, address: bit32, value: bit32) -> None:
        """
        Write a 32-bit word to memory using big-endian byte ordering.
        
        Decomposes the 32-bit word into four bytes and writes them consecutively:
        byte0 = value >> 24, byte1 = value >> 16, byte2 = value >> 8, byte3 = value
        
        Args:
            address: Memory address (must be aligned; writes 4 bytes)
            value: 32-bit word value to write
        
        Raises:
            AssertionError: If address range is out of bounds
        """
        assert bit32(0) <= address and (address + bit32(3)) < bit32(self.size), \
            "Memory write out of bounds"
        
        self.write(address, bit8(value.value >> 24))
        self.write(address + bit32(1), bit8(value.value >> 16))
        self.write(address + bit32(2), bit8(value.value >> 8))
        self.write(address + bit32(3), bit8(value.value))

    def debug_print_range(self, start_addr: int, num_words: int) -> None:
        """
        Print memory contents for debugging purposes.
        
        Args:
            start_addr: Starting address for printing
            num_words: Number of 32-bit words to print
        """
        for i in range(start_addr, start_addr + num_words * 4, 4):
            print(f"Address {i}: {self.read_word(bit32(i)).value}")
