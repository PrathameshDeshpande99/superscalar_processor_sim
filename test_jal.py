#!/usr/bin/env python3
"""Test to verify j instruction is properly assembled and recognized."""

import sys
sys.path.insert(0, '/home/khidki/superscalar_processor_sim/src')

from instruction_loader import load_instructions
from utils import bit32

# Load the bubble_sort program
instructions = load_instructions('bubble_sort.txt', add_nops=0)

# Print first 30 instructions to see what we have
print("First 30 instructions loaded:")
for i, instr in enumerate(instructions[:30]):
    print(f"[{i:2d}] {instr.value:032b} (0x{instr.value:08x})")
    
    # Check if this is a JAL instruction (opcode 1101111 = 0x6F)
    opcode = instr.value & 0x7F
    if opcode == 0b1101111:  # JAL
        print(f"      ^ JAL instruction detected")
        # Extract immediate
        imm_str = bin(instr.value)[2:].zfill(32)
        immediate_str = imm_str[0] + imm_str[12:20] + imm_str[11] + imm_str[1:11]
        print(f"      Immediate bits: {immediate_str}")

print(f"\nTotal instructions loaded: {len(instructions)}")

# Count JAL instructions
jal_count = sum(1 for instr in instructions if (instr.value & 0x7F) == 0b1101111)
print(f"JAL instructions found: {jal_count}")
