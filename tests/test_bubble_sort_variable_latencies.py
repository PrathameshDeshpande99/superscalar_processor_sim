"""
Tests for bubble sort with variable memory latencies.
Tests specifically focus on MEM_LATENCY = 2 with all other latencies = 1.
"""

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from cpu import CPU
from utils import bit32
from instruction_loader import load_instructions
import processor_config


# def test_bubble_sort_mem_latency_2():
def bubble_sort_mem_latency_2():
    """
    Test bubble sort with MEM_LATENCY = 2 and all other latencies = 1.
    """
    # Save original config
    original_if = processor_config.IF_LATENCY
    original_id = processor_config.ID_LATENCY
    original_ex = processor_config.EX_LATENCY
    original_mem = processor_config.MEM_LATENCY
    original_wb = processor_config.WB_LATENCY
    
    try:
        # Set test configuration
        processor_config.IF_LATENCY = 1
        processor_config.ID_LATENCY = 1
        processor_config.EX_LATENCY = 1
        processor_config.MEM_LATENCY = 2
        processor_config.WB_LATENCY = 1
        
        # Load the bubble sort assembly program
        instructions = load_instructions("bubble_sort", add_nops=4)
        
        # Create CPU and run the program with increased drain cycles for bubble sort complexity
        cpu = CPU()
        cpu.run_program(instructions, max_drain=5000)
        
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
        
        print("✓ Bubble sort test (MEM_LATENCY=2) passed: array is correctly sorted")
        
    except Exception as e:
        print(f"✗ Bubble sort test (MEM_LATENCY=2) failed: {e}")
        raise
    finally:
        # Restore original config
        processor_config.IF_LATENCY = original_if
        processor_config.ID_LATENCY = original_id
        processor_config.EX_LATENCY = original_ex
        processor_config.MEM_LATENCY = original_mem
        processor_config.WB_LATENCY = original_wb
