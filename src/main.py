from cpu import CPU
from utils import bit32, bit8, bit5
import json

nop = bit32("00000000000000000000000000010011")

if __name__ == "__main__":
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

    # bubble_sort_instructions = [

    #     # {
    #     #     "1": "00000001001100000000111100010011",
    #     #     "2": "00000000000000000000001010110011",
    #     #     "3": "00001001111000101000010001100011",
    #     #     "4": "00000000000000000000001100110011",
    #     #     "5": "00000111111000110000010001100011",
    #     #     "6": "01000000000000000000010000010011",
    #     #     "7": "00000000100001000000010000110011",
    #     #     "8": "00000000011000110000001110110011",
    #     #     "9": "00000000011100111000001110110011",
    #     #     "10": "00000000100000111000001110110011",
    #     #     "11": "00000000000000111010111000000011",
    #     #     "12": "00000000010000111010111010000011",
    #     #     "13": "00000001110011101101110001100011",
    #     #     "14": "00000001110100111010000000100011",
    #     #     "15": "00000001110000111010001000100011",
    #     #     "16": "00000000000100110000001100010011",
    #     #     "17": "000000000000000000000000001101111",
    #     #     "18": "00000000000100101000001010010011",
    #     #     "19": "000000000000000000000000001101111"
    #     # }

    #     # --- INITIALIZATION ---
    #     # 0: addi x30, x0, 19      (t5 = 19, loop limit)
    #     bit32("00000001001100000000111100010011"),
        
    #     # 1: add x5, x0, x0        (i = 0)
    #     bit32("00000000000000000000001010110011"),

    #     # --- OUTER LOOP ---
    #     # 2: beq x5, x30, 68       (if i == 19, jump to end_sort at inst 19)
    #     bit32("00001001111000101000010001100011"),
        
    #     # 3: add x6, x0, x0        (j = 0)
    #     bit32("00000000000000000000001100110011"),

    #     # --- INNER LOOP ---
    #     # 4: beq x6, x30, 52       (if j == 19, jump to end_inner at inst 17)
    #     bit32("00000111111000110000010001100011"),
    #     # above binary is correct

    #     # Calculate base_address (2048) and offset (j * 4)
    #     # Because 2048 requires 12 bits and can sign-extend unexpectedly in addi, 
    #     # we load 1024 and double it.
    #     # 5: addi x8, x0, 1024     (x8 = 1024)
    #     bit32("01000000000000000000010000010011"),
    #     # 6: add x8, x8, x8        (x8 = 2048)
    #     bit32("00000000100001000000010000110011"),
        
    #     # We do not have slli, so we add j to itself twice to multiply by 4
    #     # 7: add x7, x6, x6        (x7 = j * 2)
    #     bit32("00000000011000110000001110110011"),
    #     # 8: add x7, x7, x7        (x7 = j * 4)
    #     bit32("00000000011100111000001110110011"),
    #     # 9: add x7, x7, x8        (x7 = 2048 + (j * 4))
    #     bit32("00000000100000111000001110110011"),

    #     # Load elements
    #     # 10: lw x28, 0(x7)        (Load array[j])
    #     bit32("00000000000000111010111000000011"),
    #     # 11: lw x29, 4(x7)        (Load array[j+1])
    #     bit32("00000000010000111010111010000011"),

    #     # Compare and swap
    #     # 12: bge x29, x28, 12     (If array[j+1] >= array[j], skip to no_swap at inst 15)
    #     bit32("00000001110011101101110001100011"),
    #     # above binary is correct
        
    #     # 13: sw x29, 0(x7)        (Store array[j+1] into array[j])
    #     bit32("00000001110100111010000000100011"),
    #     # 14: sw x28, 4(x7)        (Store array[j] into array[j+1])
    #     bit32("00000001110000111010001000100011"),

    #     # --- NO_SWAP / INNER LOOP ITERATION ---
    #     # 15: addi x6, x6, 1       (j++)
    #     bit32("00000000000100110000001100010011"),
        
    #     # 16: jal x0, -48          (Jump back to inner_loop at inst 4)
    #     bit32("11111010000111111111000001101111"),
    #     # imm = 11111111111111010000    correct

    #     # --- END_INNER / OUTER LOOP ITERATION ---
    #     # 17: addi x5, x5, 1       (i++)
    #     bit32("00000000000100101000001010010011"),
        
    #     # 18: jal x0, -64          (Jump back to outer_loop at inst 2)
    #     bit32("11111000000111111111000001101111"),

    #     # --- END_SORT ---
    #     # 19: nop                  (Landing pad for program exit)
    #     nop, nop, nop, nop
    # ]

    # load as python list of bit32
    bubble_sort_instructions = [bit32(inst) for inst in list(json.load(open("binary_input.json")).values())]
    bubble_sort_instructions.append(nop)
    bubble_sort_instructions.append(nop)
    bubble_sort_instructions.append(nop)
    bubble_sort_instructions.append(nop)

    cpu.run_program(bubble_sort_instructions)

    # 3. Verification
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

    if passed:
        print("Bubble Sort test passed")
    else:
        print("Bubble Sort test failed")