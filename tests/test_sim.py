import sys
import os
import json
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from cpu import CPU
from utils import bit32, bit8, bit5
from assembly_pipeline import assemble_program

nop = bit32("00000000000000000000000000010011")

def test_add1():
    cpu = CPU()
    cpu.registers.write(bit5(2), bit32(10))
    cpu.registers.write(bit5(3), bit32(5))
    instructions = assemble_program("test_add")
    cpu.run_program(instructions)
    
    assert cpu.registers.read(bit5(1)) == bit32(15)
    assert cpu.registers.read(bit5(2)) == bit32(10)
    assert cpu.registers.read(bit5(3)) == bit32(5)

def test_sub1():
    cpu = CPU()
    cpu.registers.write(bit5(2), bit32(10))
    cpu.registers.write(bit5(3), bit32(5))
    instructions = assemble_program("test_sub")
    cpu.run_program(instructions)
    
    assert cpu.registers.read(bit5(1)) == bit32(5)
    assert cpu.registers.read(bit5(2)) == bit32(10)
    assert cpu.registers.read(bit5(3)) == bit32(5)

def test_addi1():
    cpu = CPU()
    cpu.registers.write(bit5(2), bit32(10))
    instructions = assemble_program("test_addi")
    cpu.run_program(instructions)
    
    assert cpu.registers.read(bit5(1)) == bit32(15)
    assert cpu.registers.read(bit5(2)) == bit32(10)

def test_ld1():
    cpu = CPU()
    cpu.registers.write(bit5(2), bit32(2048))
    cpu.memory.write(bit32(2048), bit8("01010101"))
    cpu.memory.write(bit32(2049), bit8("01010101"))
    cpu.memory.write(bit32(2050), bit8("01010101"))
    cpu.memory.write(bit32(2051), bit8("01010101"))

    instructions = assemble_program("test_load")
    cpu.run_program(instructions)
    
    assert cpu.registers.read(bit5(3)) == bit32("01010101010101010101010101010101")
    assert cpu.registers.read(bit5(2)) == bit32(2048)

def test_st1():
    cpu = CPU()
    cpu.registers.write(bit5(2), bit32(2048))
    cpu.registers.write(bit5(4), bit32("01010101010101010101010101010101"))
    instructions = assemble_program("test_store")
    cpu.run_program(instructions)
    
    assert cpu.memory.read(bit32(2048)) == bit8("01010101")
    assert cpu.memory.read(bit32(2049)) == bit8("01010101")
    assert cpu.memory.read(bit32(2050)) == bit8("01010101")
    assert cpu.memory.read(bit32(2051)) == bit8("01010101")

def test_raw1():
    instructions = assemble_program("test_raw")
    cpu = CPU()
    cpu.run_program(instructions)

    assert cpu.registers.read(bit5(1)) == bit32(5)
    assert cpu.registers.read(bit5(2)) == bit32(5)

def test_control_haz1():
    instructions = assemble_program("test_loop")
    cpu = CPU()
    cpu.run_program(instructions)

    assert cpu.registers.read(bit5(4)) == bit32(7)
    assert cpu.registers.read(bit5(3)) == bit32(4)
    assert cpu.registers.read(bit5(1)) == bit32(0)
    assert cpu.registers.read(bit5(2)) == bit32(3)

def test_bubble_sort():
    print("Testing Bubble Sort (20 numbers)")
    cpu = CPU()

    # 1. Manual Memory Loading (Base Address 2048)
    numbers = [45, 12, 89, 3, 22, 78, 91, 15, 6, 33, 50, 67, 8, 99, 21, 10, 4, 60, 88, 1]
    base_addr = 2048

    # Load the numbers into the simulator's memory 
    # (Adjust this loop based on how your memory write function expects 32-bit integers)
    for idx, val in enumerate(numbers):
        # Assuming val fits in 32 bits, and memory.write takes an address and a 32-bit value
        # E.g., cpu.memory.write(base_addr + (idx * 4), bit32(format(val, '032b')))
        cpu.memory.write_word(bit32(base_addr + (idx * 4)), bit32(val))

    # print the state of memory before execution
    print("Memory before execution:")
    for i in range(base_addr, base_addr + 20 * 4, 4):
        print(f"Address {i}: {cpu.memory.read_word(bit32(i)).value}")

    bubble_sort_instructions = [bit32(inst) for inst in list(json.load(open("binary_input.json")).values())]
    bubble_sort_instructions.append(nop)
    bubble_sort_instructions.append(nop)
    bubble_sort_instructions.append(nop)
    bubble_sort_instructions.append(nop)

    instructions_completed, cycles_completed = cpu.run_program(bubble_sort_instructions)

    print("Verifying Memory...")
    sorted_numbers = sorted(numbers)
    passed = True

    for idx, expected_val in enumerate(sorted_numbers):
        addr = base_addr + (idx * 4)
        print("Currently read address: ", addr)
        memory_value = cpu.memory.read_word(bit32(addr))
        if memory_value != bit32(expected_val):
            passed = False
            print(f"Mismatch at index {idx}: Expected {expected_val}, Got {memory_value.value}")

    assert passed == True

    print("Instructions completed: ", instructions_completed)
    print("Cycles completed: ", cycles_completed)
    print("IPC: ", instructions_completed / cycles_completed)