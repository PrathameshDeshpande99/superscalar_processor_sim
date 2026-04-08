"""
Module defining the register file for the superscalar processor.
"""

from utils import bit32, bit5

class Registers:
    """
    Register file containing 32 32-bit registers.
    """
    def __init__(self):
        """Initialize all 32 registers with zeros."""
        self.registers = [bit32(0) for _ in range(32)]  # Initialize 32 registers with zeros
    
    def read(self, index: bit5) -> bit32:
        """
        Read the value of a register at the given index.

        Args:
            index (bit5): The index of the register to read (0-31).

        Returns:
            bit32: The value stored in the register.
        """
        return self.registers[index]
    
    def write(self, index: bit5, value: bit32):
        """
        Write a value to a register at the given index.

        Args:
            index (bit5): The index of the register to write to (0-31).
            value (bit32): The 32-bit value to store in the register.
        """
        self.registers[index] = value