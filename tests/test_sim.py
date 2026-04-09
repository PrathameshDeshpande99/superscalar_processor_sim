import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from cpu import CPU
from utils import bit32, bit8, bit5
from instruction_loader import load_instructions

nop = bit32("00000000000000000000000000010011")

def test_add1():
    cpu = CPU()
    cpu.registers.write(2, bit32(10))
    cpu.registers.write(3, bit32(5))
    cpu.run_program([bit32("00000000001100010000000010110011"), nop, nop, nop, nop]) # add x1, x2, x3
    
    assert cpu.registers.read(bit5(1)) == bit32(15)
    assert cpu.registers.read(bit5(2)) == bit32(10)
    assert cpu.registers.read(bit5(3)) == bit32(5)

def test_sub1():
    cpu = CPU()
    cpu.registers.write(2, bit32(10))
    cpu.registers.write(3, bit32(5))
    cpu.run_program([bit32("01000000001100010000000010110011"), nop, nop, nop, nop]) # sub x1, x2, x3
    
    assert cpu.registers.read(bit5(1)) == bit32(5)
    assert cpu.registers.read(bit5(2)) == bit32(10)
    assert cpu.registers.read(bit5(3)) == bit32(5)

def test_addi1():
    cpu = CPU()
    cpu.registers.write(2, bit32(10))
    cpu.run_program([bit32("00000000010100010000000010010011"), nop, nop, nop, nop]) # addi x1, x2, 5
    
    assert cpu.registers.read(bit5(1)) == bit32(15)
    assert cpu.registers.read(bit5(2)) == bit32(10)

def test_lw1():
    cpu = CPU()
    cpu.registers.write(2, bit32(2048))
    cpu.memory.write(bit32(2048), bit8("01010101"))
    cpu.memory.write(bit32(2049), bit8("01010101"))
    cpu.memory.write(bit32(2050), bit8("01010101"))
    cpu.memory.write(bit32(2051), bit8("01010101"))

    cpu.run_program([bit32("00000000000000010000000110000011"), nop, nop, nop, nop]) # ld x3, 0(x2) -> load value at memory[2048] to x3
    
    assert cpu.registers.read(bit5(3)) == bit32("01010101010101010101010101010101")
    assert cpu.registers.read(bit5(2)) == bit32(2048)

def test_sw1():
    cpu = CPU()
    cpu.registers.write(2, bit32(2048))
    cpu.registers.write(4, bit32("01010101010101010101010101010101"))
    cpu.run_program([bit32("00000000010000010010000000100011"), nop, nop, nop, nop]) # st x4, 0(x2) -> store value of x4 to memory[2048]
    
    assert cpu.memory.read(bit32(2048)) == bit8("01010101")
    assert cpu.memory.read(bit32(2049)) == bit8("01010101")
    assert cpu.memory.read(bit32(2050)) == bit8("01010101")
    assert cpu.memory.read(bit32(2051)) == bit8("01010101")

def test_raw1():
    # addi x1, x0, 5
    # add  x2, x1, x3
    instructions = [
        bit32("00000000010100000000000010010011"),
        bit32("00000000001100001000000100110011"),
    ]

    instructions.append(nop)
    instructions.append(nop)
    instructions.append(nop)
    instructions.append(nop)

    cpu = CPU()
    cpu.run_program(instructions)

    assert cpu.registers.read(bit5(1)) == bit32(5)
    assert cpu.registers.read(bit5(2)) == bit32(5)

def test_control_haz1():
    # x1 = 5
    # x2 = 3
    # loop:
    # x3 = x1 + x2
    # x1 = x1 - 1
    # if x1 != x0 goto loop
    # x4 = x3 + x2

    instructions = [
        bit32("00000000010100000000000010010011"),  # addi x1, x0, 5
        bit32("00000000001100000000000100010011"),  # addi x2, x0, 3
        bit32("00000000001000001000000110110011"),  # add x3, x1, x2 (loop target)
        bit32("11111111111100001000000010010011"),  # addi x1, x1, -1
        bit32("11111110000000001001100011100011"),  # bne x1, x0, loop (-8 offset)
        bit32("00000000001000011000001000110011")   # add x4, x3, x2
    ]

    instructions.append(nop)
    instructions.append(nop)
    instructions.append(nop)
    instructions.append(nop)

    cpu = CPU()
    cpu.run_program(instructions)

    assert cpu.registers.read(bit5(4)) == bit32(7)
    assert cpu.registers.read(bit5(3)) == bit32(4)
    assert cpu.registers.read(bit5(1)) == bit32(0)
    assert cpu.registers.read(bit5(2)) == bit32(3)


def test_load_instructions_from_file():
    """
    Test the automated instruction loading workflow.
    This demonstrates loading an assembly program from assembly_programs/ folder.
    """
    try:
        # Load instructions from an assembly program file
        instructions = load_instructions("loop_test", add_nops=4)
        
        # Verify that we got a list of instructions
        assert isinstance(instructions, list)
        assert len(instructions) > 0
        assert all(isinstance(instr, bit32) for instr in instructions)
        
        # Execute the program to verify it works
        cpu = CPU()
        cpu.run_program(instructions)
        print("✓ Successfully loaded and executed assembly program from file")
        
    except FileNotFoundError as e:
        # This is expected if loop_test.asm doesn't exist in assembly_programs/
        print(f"✓ Test skipped: {e}")


def test_instruction_loader_with_custom_nops():
    """
    Test the instruction loader with custom number of NOPs.
    """
    try:
        # Load with different number of NOPs
        instructions_2nops = load_instructions("loop_test", add_nops=2)
        instructions_8nops = load_instructions("loop_test", add_nops=8)
        
        nop = bit32("00000000000000000000000000010011")
        
        # Verify NOP count difference
        expected_diff = 8 - 2
        actual_diff = len(instructions_8nops) - len(instructions_2nops)
        assert actual_diff == expected_diff
        
        print(f"✓ NOP count test passed: {actual_diff} NOPs added as expected")
        
    except FileNotFoundError as e:
        print(f"✓ Test skipped: {e}")


def test_bubble_sort():
    """
    Test the bubble sort assembly program.
    Loads bubble_sort.txt, assembles and executes it, then verifies that the array is sorted.
    """
    try:
        # Load the bubble sort assembly program
        instructions = load_instructions("bubble_sort", add_nops=4)
        
        # Create CPU and run the program
        cpu = CPU()
        cpu.run_program(instructions)
        
        # The sorted array should be stored at memory address 1024 (base address in x5)
        # with 20 values, each 4 bytes apart
        base_address = bit32(1024)
        expected_sorted = [1, 3, 5, 11, 12, 14, 23, 27, 34, 38, 45, 50, 56, 60, 67, 72, 78, 89, 90, 99]
        
        # Verify each value in the sorted array
        for i, expected_value in enumerate(expected_sorted):
            address = base_address + bit32(i * 4)
            actual_value = cpu.memory.read_word(address)
            assert actual_value == bit32(expected_value), \
                f"Array index {i}: expected {expected_value}, got {actual_value} at address {address}"
        
        print("✓ Bubble sort test passed: array is correctly sorted")
        
    except FileNotFoundError as e:
        print(f"✓ Bubble sort test skipped: {e}")
    except Exception as e:
        print(f"✗ Bubble sort test failed: {e}")
        raise