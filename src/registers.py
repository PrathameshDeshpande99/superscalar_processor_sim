"""
Register file module for the superscalar processor simulator.

Implements a RISC-V compatible register file with 32 registers (x0-x31).
Register x0 is hardwired to zero and always returns 0 regardless of write operations.
"""

from utils import bit32, bit5


class Registers:
    """Register file holding 32 general-purpose 32-bit registers."""

    def __init__(self):
        """Initialize all 32 registers with zero values."""
        self.registers = [bit32(0) for _ in range(32)]
    
    def read(self, index: bit5) -> bit32:
        """
        Read a register value.
        
        Args:
            index: Register index (0-31, where 0 is x0)
        
        Returns:
            bit32: Value of the specified register
        """
        return self.registers[index]
    
    def write(self, index: bit5, value: bit32) -> None:
        """
        Write a value to a register.
        
        Note: Writing to x0 (register 0) has no effect; x0 always reads as 0.
        
        Args:
            index: Register index (0-31, where 0 is x0)
            value: Value to write (ignored if index is 0)
        """
        if index != bit5(0):  # x0 is hardwired to zero
            self.registers[index] = value
