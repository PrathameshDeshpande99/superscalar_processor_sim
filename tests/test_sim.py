import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from cpu import CPU
from utils import bit32, bit8, bit5

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

def test_ld1():
    cpu = CPU()
    cpu.registers.write(2, bit32(2048))
    cpu.memory.write(bit32(2048), bit8("01010101"))
    cpu.memory.write(bit32(2049), bit8("01010101"))
    cpu.memory.write(bit32(2050), bit8("01010101"))
    cpu.memory.write(bit32(2051), bit8("01010101"))

    cpu.run_program([bit32("00000000000000010000000110000011"), nop, nop, nop, nop]) # ld x3, 0(x2) -> load value at memory[2048] to x3
    
    assert cpu.registers.read(bit5(3)) == bit32("01010101010101010101010101010101")
    assert cpu.registers.read(bit5(2)) == bit32(2048)

def test_st1():
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