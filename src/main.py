from cpu import CPU
from utils import bit32, bit8, bit5

nop = bit32("00000000000000000000000000010011")

if __name__ == "__main__":
    # print("Testing for addition")
    # cpu = CPU()
    # cpu.registers.write(2, bit32(10))
    # cpu.registers.write(3, bit32(5))
    # cpu.run_program([bit32("00000000001100010000000010110011"), nop, nop, nop]) # add x1, x2, x3
    # for i in cpu.registers.registers:
    #     print(i)

    # print("Testing for subtraction")
    # cpu = CPU()
    # cpu.registers.write(2, bit32(10))
    # cpu.registers.write(3, bit32(5))
    # cpu.run_program([bit32("01000000001100010000000010110011"), nop, nop, nop]) # sub x1, x2, x3
    # for i in cpu.registers.registers:
    #     print(i)

    # print("Testing for immediate addition")
    # cpu = CPU()
    # cpu.registers.write(2, bit32(10))
    # cpu.run_program([bit32("00000000010100010000000010010011"), nop, nop, nop]) # addi x1, x2, 5
    # for i in cpu.registers.registers:
    #     print(i)

    # print("Testing for load")
    # cpu = CPU()
    # cpu.registers.write(2, bit32(2048))
    # cpu.memory.write(bit32(2048), bit8("01010101"))
    # cpu.memory.write(bit32(2049), bit8("01010101"))
    # cpu.memory.write(bit32(2050), bit8("01010101"))
    # cpu.memory.write(bit32(2051), bit8("01010101"))

    # cpu.run_program([bit32("00000000000000010000000110000011"), nop, nop, nop]) # ld x3, 0(x2) -> load value at memory[2048] to x3
    # for i in cpu.registers.registers:
    #     print(i)

    # if cpu.registers.read(bit5(3)) == bit32("01010101010101010101010101010101"):
    #     print("Load test passed")
    # else:
    #     print("Load test failed")

    print("Testing for store")
    cpu = CPU()
    cpu.registers.write(2, bit32(2048))
    cpu.registers.write(4, bit32("01010101010101010101010101010101"))
    cpu.run_program([bit32("00000000010000010010000000100011"), nop, nop, nop]) # st x4, 0(x2) -> store value of x4 to memory[2048]
    for i in cpu.registers.registers:
        print(i)

    if cpu.memory.read(bit32(2048)) == bit8("01010101") and cpu.memory.read(bit32(2049)) == bit8("01010101") and cpu.memory.read(bit32(2050)) == bit8("01010101") and cpu.memory.read(bit32(2051)) == bit8("01010101"):
        print("Store test passed")
    else:
        print("Store test failed")