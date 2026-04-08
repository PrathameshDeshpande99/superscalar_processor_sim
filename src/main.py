from cpu import CPU
from utils import bit32, bit8, bit5
from instruction_loader import load_instructions

if __name__ == "__main__":
    # Example 1: Using the automated workflow
    # Load an assembly program from assembly_programs/ folder
    try:
        instructions = load_instructions("loop_test")  # Reads from assembly_programs/loop_test.asm
        cpu = CPU()
        cpu.run_program(instructions)
        print("Program executed successfully using automated workflow")
    except (FileNotFoundError, ValueError) as e:
        print(f"Note: {e}")
        print("Falling back to hardcoded example...\n")
        
        # Example 2: Using hardcoded instructions (for testing/fallback)
        # This is equivalent to:
        # x1 = 5
        # x2 = 3
        # loop:
        # x3 = x1 + x2
        # x1 = x1 - 1
        # if x1 != x0 goto loop
        # x4 = x3 + x2

        nop = bit32("00000000000000000000000000010011")
        instructions = [
            bit32("00000000010100000000000010010011"),  # addi x1, x0, 5
            bit32("00000000001100000000000100010011"),  # addi x2, x0, 3
            bit32("00000000001000001000000110110011"),  # add x3, x1, x2 (loop target)
            bit32("11111111111100001000000010010011"),  # addi x1, x1, -1
            bit32("11111110000000001001100011100011"),  # bne x1, x0, loop (-8 offset)
            bit32("00000000001000011000001000110011"),  # add x4, x3, x2
            nop, nop, nop, nop
        ]

        cpu = CPU()
        cpu.run_program(instructions)

        assert cpu.registers.read(bit5(4)) == bit32(7)
        assert cpu.registers.read(bit5(3)) == bit32(4)
        assert cpu.registers.read(bit5(1)) == bit32(0)
        assert cpu.registers.read(bit5(2)) == bit32(3)
        print("Hardcoded example executed successfully")