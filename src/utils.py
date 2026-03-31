class bit32:
    """Represents a 32-bit unsigned integer with fixed-width semantics for word operations."""
    
    def __init__(self, value: int | str | 'bit8' | 'bit5'):
        """
        Initialize a 32-bit value.
        
        Args:
            value: Can be an int, binary string, bit8, or bit5. Values are masked to 32 bits.
        """
        _mask = 0xFFFFFFFF
        if isinstance(value, str):
            self.value = int(value, 2) & _mask
        elif isinstance(value, (bit8, bit5)):
            self.value = value.value & _mask
        else:
            self.value = int(value) & _mask

    def __add__(self, other: 'bit32') -> 'bit32':
        """Add two 32-bit values with overflow wrapping."""
        return bit32(self.value + other.value)

    def __sub__(self, other: 'bit32') -> 'bit32':
        """Subtract two 32-bit values with underflow wrapping."""
        return bit32(self.value - other.value)

    def __and__(self, other: 'bit32') -> 'bit32':
        """Bitwise AND operation."""
        return bit32(self.value & other.value)

    def __or__(self, other: 'bit32') -> 'bit32':
        """Bitwise OR operation."""
        return bit32(self.value | other.value)  

    def __xor__(self, other: 'bit32') -> 'bit32':
        """Bitwise XOR operation."""
        return bit32(self.value ^ other.value)

    def __lshift__(self, shift: int) -> 'bit32':
        """Left shift operation."""
        return bit32(self.value << shift)

    def __rshift__(self, shift: int) -> 'bit32':
        """Right shift operation."""
        return bit32(self.value >> shift)

    def __repr__(self) -> str:
        """Return hexadecimal representation."""
        return f"bit32({self.value:#010x})"

    def __index__(self) -> int:
        """Allow use as list index."""
        return self.value

    def __lt__(self, other: 'bit32') -> bool:
        """Less-than comparison."""
        return self.value < other.value
    
    def __le__(self, other: 'bit32') -> bool:
        """Less-than-or-equal comparison."""
        return self.value <= other.value

    def __eq__(self, other: 'bit32') -> bool:
        """Equality comparison."""
        return self.value == other.value

    def __str__(self) -> str:
        """Return 32-bit binary string representation."""
        return format(self.value, '032b')

class bit8:
    """Represents an 8-bit unsigned integer with fixed-width semantics for byte operations."""
    
    def __init__(self, value: int | str | 'bit32' | 'bit5'):
        """
        Initialize an 8-bit value.
        
        Args:
            value: Can be an int, binary string, bit32, or bit5. Values are masked to 8 bits.
        """
        _mask = 0xFF
        if isinstance(value, str):
            self.value = int(value, 2) & _mask
        elif isinstance(value, (bit32, bit5)):
            self.value = value.value & _mask
        else:
            self.value = int(value) & _mask

    def __add__(self, other: 'bit8') -> 'bit8':
        """Add two 8-bit values with overflow wrapping."""
        return bit8(self.value + other.value)

    def __sub__(self, other: 'bit8') -> 'bit8':
        """Subtract two 8-bit values with underflow wrapping."""
        return bit8(self.value - other.value)

    def __and__(self, other: 'bit8') -> 'bit8':
        """Bitwise AND operation."""
        return bit8(self.value & other.value)

    def __or__(self, other: 'bit8') -> 'bit8':
        """Bitwise OR operation."""
        return bit8(self.value | other.value)

    def __xor__(self, other: 'bit8') -> 'bit8':
        """Bitwise XOR operation."""
        return bit8(self.value ^ other.value)

    def __lshift__(self, shift: int) -> 'bit8':
        """Left shift operation."""
        return bit8(self.value << shift)

    def __rshift__(self, shift: int) -> 'bit8':
        """Right shift operation."""
        return bit8(self.value >> shift)

    def __repr__(self) -> str:
        """Return hexadecimal representation."""
        return f"bit8({self.value:#04x})"

    def __index__(self) -> int:
        """Allow use as list index."""
        return self.value

    def __eq__(self, other: 'bit8') -> bool:
        """Equality comparison."""
        return self.value == other.value


class bit5:
    """Represents a 5-bit unsigned integer used for register indexing in RISC-V."""
    
    def __init__(self, value: int | str | 'bit32' | 'bit8'):
        """
        Initialize a 5-bit value.
        
        Args:
            value: Can be an int, binary string, bit32, or bit8. Values are masked to 5 bits (0-31).
        """
        _mask = 0x1F
        if isinstance(value, str):
            self.value = int(value, 2) & _mask
        elif isinstance(value, (bit32, bit8)):
            self.value = value.value & _mask
        else:
            self.value = int(value) & _mask

    def __add__(self, other: 'bit5') -> 'bit5':
        """Add two 5-bit values with overflow wrapping."""
        return bit5(self.value + other.value)

    def __sub__(self, other: 'bit5') -> 'bit5':
        """Subtract two 5-bit values with underflow wrapping."""
        return bit5(self.value - other.value)

    def __and__(self, other: 'bit5') -> 'bit5':
        """Bitwise AND operation."""
        return bit5(self.value & other.value)

    def __or__(self, other: 'bit5') -> 'bit5':
        """Bitwise OR operation."""
        return bit5(self.value | other.value)

    def __xor__(self, other: 'bit5') -> 'bit5':
        """Bitwise XOR operation."""
        return bit5(self.value ^ other.value)

    def __lshift__(self, shift: int) -> 'bit5':
        """Left shift operation."""
        return bit5(self.value << shift)

    def __rshift__(self, shift: int) -> 'bit5':
        """Right shift operation."""
        return bit5(self.value >> shift)

    def __repr__(self) -> str:
        """Return hexadecimal representation."""
        return f"bit5({self.value:#06x})"

    def __index__(self) -> int:
        """Allow use as list index."""
        return self.value
    
    def __eq__(self, other: 'bit5') -> bool:
        """Equality comparison."""
        return self.value == other.value
    
    def __ne__(self, other: 'bit5') -> bool:
        """Inequality comparison."""
        return self.value != other.value

    def __str__(self) -> str:
        """Return 5-bit binary string representation."""
        return format(self.value, '05b')


# Type definitions for CPU pipeline buffer stages

from typing import TypedDict


class IF_RF_Buffer_Class(TypedDict):
    """Buffer between Instruction Fetch (IF) and Register Fetch (RF) stages."""
    instruction: bit32


class RF_EX_Buffer_Class(TypedDict):
    """Buffer between Register Fetch (RF) and Execute (EX) stages."""
    instruction: bit32
    A: bit32  # First operand from register rs1
    B: bit32  # Second operand from register rs2
    rs1: bit5  # Source register 1 index
    rs2: bit5  # Source register 2 index
    rd: bit5  # Destination register index
    funct7: int  # Function code for ALU operation selection
    isAdd: bool  # Indicates ADD or ADDI operation
    isSub: bool  # Indicates SUB operation
    isLd: bool  # Indicates LOAD operation
    isSt: bool  # Indicates STORE operation
    isImm: bool  # Indicates immediate operand
    doWB: bool  # Indicates if result should be written back
    isBranchTaken: bool  # Indicates if branch condition is met
    branch_offset: int  # Branch target offset


class EX_MEM_Buffer_Class(TypedDict):
    """Buffer between Execute (EX) and Memory (MEM) stages."""
    alu_result: bit32  # Result from ALU operation
    rs2_value: bit32  # Value of source register 2 for store operations
    rd: bit5  # Destination register index
    isLd: bool  # Indicates LOAD operation
    isSt: bool  # Indicates STORE operation
    doWB: bool  # Indicates if result should be written back


class MEM_WB_Buffer_Class(TypedDict):
    """Buffer between Memory (MEM) and Write-Back (WB) stages."""
    writeback_value: bit32  # Value to write back to register
    rs2_value: bit32  # Value of source register 2
    rd: bit5  # Destination register index
    isLd: bool  # Indicates LOAD operation
    doWB: bool  # Indicates if result should be written back


# Pipeline buffer constructors

def create_if_rf_buffer() -> IF_RF_Buffer_Class:
    """
    Create and initialize the IF/RF pipeline buffer with a NOP instruction.
    
    Returns:
        IF_RF_Buffer_Class: Initialized buffer with NOP instruction.
    """
    return {
        "instruction": bit32("00000000000000000000000000010011"),
    }


def create_rf_ex_buffer() -> RF_EX_Buffer_Class:
    """
    Create and initialize the RF/EX pipeline buffer with default NOP state.
    
    Returns:
        RF_EX_Buffer_Class: Initialized buffer representing a NOP in decode stage.
    """
    return {
        "instruction": bit32("00000000000000000000000000010011"),
        "A": bit32(0),
        "B": bit32(0),
        "rs1": bit5(0),
        "rs2": bit5(0),
        "rd": bit5(0),
        "funct7": 0,
        "isAdd": True,
        "isSub": False,
        "isLd": False,
        "isSt": False,
        "isImm": True,
        "doWB": True,
        "isBranchTaken": False,
        "branch_offset": 0,
    }


def create_ex_mem_buffer() -> EX_MEM_Buffer_Class:
    """
    Create and initialize the EX/MEM pipeline buffer.
    
    Returns:
        EX_MEM_Buffer_Class: Initialized buffer with default NOP state.
    """
    return {
        "alu_result": bit32(0),
        "rs2_value": bit32(0),
        "rd": bit5(0),
        "isLd": False,
        "isSt": False,
        "doWB": True,
    }


def create_mem_wb_buffer() -> MEM_WB_Buffer_Class:
    """
    Create and initialize the MEM/WB pipeline buffer.
    
    Returns:
        MEM_WB_Buffer_Class: Initialized buffer with default NOP state.
    """
    return {
        "writeback_value": bit32(0),
        "rs2_value": bit32(0),
        "rd": bit5(0),
        "isLd": False,
        "doWB": True,
    }


# Utility functions

def bin_to_signed(bin_str: str) -> int:
    """
    Convert a binary string to its signed integer value using two's complement.
    
    This function interprets the most significant bit as a sign bit and computes
    the equivalent signed integer value.
    
    Args:
        bin_str: Binary string (e.g., "1111" for -1 in 4-bit two's complement)
    
    Returns:
        int: The signed integer value represented by the binary string.
    """
    value = int(bin_str, 2)
    bits = len(bin_str)
    sign_bit_mask = 1 << (bits - 1)
    return (value ^ sign_bit_mask) - sign_bit_mask
