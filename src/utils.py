"""
Utility classes and methods for the superscalar processor simulator.
Includes specific integer types for architectural representation.
"""

class bit32:
    """Class representing a 32-bit integer."""
    def __init__(self, value: int | str | bit8 | bit5):
        if isinstance(value, str):
            self.value = int(value, 2) & 0xFFFFFFFF  # Convert binary string to int and ensure it's 32 bits
        elif isinstance(value, bit8) or isinstance(value, bit5):
            self.value = value.value & 0xFFFFFFFF
        else:
            self.value = value & 0xFFFFFFFF  # Ensure it's always 32 bits

    def __add__(self, other):
        return bit32(self.value + other.value)

    def __sub__(self, other):
        return bit32(self.value - other.value)

    def __and__(self, other):
        return bit32(self.value & other.value)

    def __or__(self, other):
        return bit32(self.value | other.value)  

    def __xor__(self, other):
        return bit32(self.value ^ other.value)

    def __lshift__(self, shift):
        return bit32(self.value << shift)

    def __rshift__(self, shift):
        return bit32(self.value >> shift)

    def __repr__(self):
        return f"bit32({self.value:#010x})"

    def __index__(self):
        return self.value

    def __lt__(self, other):
        return self.value < other.value
    
    def __le__(self, other):
        return self.value <= other.value

    def __eq__(self, other):
        return self.value == other.value

    def __str__(self):
        return format(self.value, '032b')
    
class bit8:
    """Class representing an 8-bit integer."""
    def __init__(self, value: int | str | bit32 | bit5):
        if isinstance(value, str):
            self.value = int(value, 2) & 0xFF  # Convert binary string to int and ensure it's 8 bits
        elif isinstance(value, bit32) or isinstance(value, bit5):
            self.value = value.value & 0xFF
        else:
            self.value = value & 0xFF  # Ensure it's always 8 bits

    def __add__(self, other):
        return bit8(self.value + other.value)

    def __sub__(self, other):
        return bit8(self.value - other.value)

    def __and__(self, other):
        return bit8(self.value & other.value)

    def __or__(self, other):
        return bit8(self.value | other.value)

    def __xor__(self, other):
        return bit8(self.value ^ other.value)

    def __lshift__(self, shift):
        return bit8(self.value << shift)

    def __rshift__(self, shift):
        return bit8(self.value >> shift)

    def __repr__(self):
        return f"bit8({self.value:#04x})"

    def __index__(self):
        return self.value

    def __eq__(self, other):
        return self.value == other.value

class bit5:
    """Class representing a 5-bit integer, suitable for register indices."""
    def __init__(self, value: int | str | bit32 | bit8):
        if isinstance(value, str):
            self.value = int(value, 2) & 0x1F  # Convert binary string to int and ensure it's 5 bits
        elif isinstance(value, bit32) or isinstance(value, bit8):
            self.value = value.value & 0x1F
        else:
            self.value = value & 0x1F  # Ensure it's always 5 bits

    def __add__(self, other):
        return bit5(self.value + other.value)

    def __sub__(self, other):
        return bit5(self.value - other.value)

    def __and__(self, other):
        return bit5(self.value & other.value)

    def __or__(self, other):
        return bit5(self.value | other.value)

    def __xor__(self, other):
        return bit5(self.value ^ other.value)

    def __lshift__(self, shift):
        return bit5(self.value << shift)

    def __rshift__(self, shift):
        return bit5(self.value >> shift)

    def __repr__(self):
        return f"bit5({self.value:#06x})"

    def __index__(self):
        return self.value
    
    def __eq__(self, other):
        return self.value == other.value
    
    def __ne__(self, other):
        return self.value != other.value

    def __str__(self):
        return format(self.value, '05b')


# Type definitions for pipeline Buffers

from typing import TypedDict

class IF_RF_Buffer_Class(TypedDict):
    instruction: bit32

class RF_EX_Buffer_Class(TypedDict):
    instruction: bit32
    A: bit32
    B: bit32
    rs1: bit5
    rs2: bit5
    rd: bit5
    funct7: int     # RISK: this is int type
    isAdd: bool
    isSub: bool
    isLd: bool
    isSt: bool
    isImm: bool
    doWB: bool
    isBranchTaken: bool
    branch_offset: int

class EX_MEM_Buffer_Class(TypedDict):
    alu_result: bit32
    rs2_value: bit32
    rd: bit5
    isLd: bool
    isSt: bool
    doWB: bool

class MEM_WB_Buffer_Class(TypedDict):
    writeback_value: bit32
    rs2_value: bit32
    rd: bit5
    isLd: bool
    doWB: bool


# Constructors for pipeline buffers
# Initialization should be done using nop instructions

def create_if_rf_buffer() -> IF_RF_Buffer_Class:
    return {
        "instruction": bit32("00000000000000000000000000010011"),
    }

def create_rf_ex_buffer() -> RF_EX_Buffer_Class:
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
    return {
        "alu_result": bit32(0),
        "rs2_value": bit32(0),
        "rd": bit5(0),
        "isLd": False,
        "isSt": False,
        "doWB": True,
    }

def create_mem_wb_buffer() -> MEM_WB_Buffer_Class:
    return {
        "writeback_value": bit32(0),
        "rs2_value": bit32(0),
        "rd": bit5(0),
        "isLd": False,
        "doWB": True,
    }

# Utility functions

def bin_to_signed(bin_str: str) -> int:
    value = int(bin_str, 2)
    bits = len(bin_str)
    sign_bit = 1 << (bits - 1)
    return (value ^ sign_bit) - sign_bit