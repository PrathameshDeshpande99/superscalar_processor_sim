#!/usr/bin/env python3
"""Test to verify JAL instructions are recognized as taken branches in pipeline."""

import sys
sys.path.insert(0, '/home/khidki/superscalar_processor_sim/src')

from utils import bit32

# Manual test: Create a JAL instruction
# JAL format: imm[20|10:1|11|19:12] rd opcode
# opcode = 1101111 (0x6F)
# For "jal x0, 100" (offset +100 words = 400 bytes):
# immediate = 400 in signed 21-bit = 0x190 = 0b000110010000
# Build the instruction (remember immediate is scrambled in encoding)

# Actually, let's just run a quick simulation with bubble_sort
from instruction_loader import load_instructions

print("Testing JAL instruction recognition in pipeline...")
print("=" * 60)

instructions = load_instructions('bubble_sort.txt', add_nops=0)

# Find the JAL instructions
jal_positions = []
for i, instr in enumerate(instructions):
    opcode = instr.value & 0x7F
    if opcode == 0b1101111:  # JAL
        jal_positions.append(i)
        print(f"JAL instruction found at position {i}")

print(f"\nTotal JAL instructions: {len(jal_positions)}")

# Now simulate and check if branches are taken
# We'll handle this by directly testing the rf_stage logic

from pipeline import Pipeline
from registers import Registers

pipeline = Pipeline()
registers = Registers()

# Test with one of the JAL instructions
if jal_positions:
    test_instr_pos = jal_positions[0]
    test_instr = instructions[test_instr_pos]
    
    print(f"\nTesting instruction at position {test_instr_pos}:")
    print(f"Instruction: 0x{test_instr.value:08x}")
    print(f"Binary: {bin(test_instr.value)[2:].zfill(32)}")
    
    # Set up the IF_RF buffer with this instruction
    pipeline.IF_RF_Buffer["instruction"] = test_instr
    
    # Run RF stage
    pipeline.rf_stage(registers)
    
    # Check if branch was marked as taken
    print(f"\nisBranchTaken: {pipeline.RF_EX_Buffer.get('isBranchTaken', False)}")
    if pipeline.RF_EX_Buffer.get('isBranchTaken'):
        print(f"branch_offset: {pipeline.RF_EX_Buffer.get('branch_offset', 'N/A')}")
        print("\n✓ SUCCESS: JAL instruction correctly recognized as taken branch!")
    else:
        print("\n✗ FAILED: JAL instruction NOT recognized as taken branch!")
        print(f"RF_EX_Buffer: {pipeline.RF_EX_Buffer}")
