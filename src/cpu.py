"""
Module defining the main CPU class and execution logic.
"""

from registers import Registers
from memory import Memory
from pipeline import Pipeline
from alu import ALU
from utils import bit32, create_mem_wb_buffer
from cache import CacheHierarchy
from processor_config import L1D_CONFIG, L1I_CONFIG, L2_CONFIG, MAIN_MEMORY_CONFIG
import time

class CPU:
    """
    Central Processing Unit (CPU) encapsulating components like registers, memory, pipeline and ALU.
    """
    def __init__(self):
        """Initialize the CPU with all its internal components and state."""
        self.registers = Registers()
        self.memory = Memory()
        self.cache_hierarchy = CacheHierarchy(self.memory, L1D_CONFIG, L1I_CONFIG, L2_CONFIG, MAIN_MEMORY_CONFIG)
        self.pipeline = Pipeline()
        self.alu = ALU()
        self.pc = 0  # Track current program counter
    
    def _load_instructions_to_memory(self, instructions: list[bit32]):
        """Helper to load instructions into main memory."""
        for i, instr in enumerate(instructions):
            self.memory.write_word(bit32(i * 4), instr)
    
    def run_program(self, instructions: list[bit32], quiet: bool = True):
        """
        Execute a program from a list of instructions.
        
        Args:
            instructions: List of bit32 instruction objects
            quiet: If True, suppress debug output. If False, print debug info each cycle.
        
        Returns:
            Tuple of (instructions_executed, clock_cycles)
        """
        self._load_instructions_to_memory(instructions)
        pc = 0
        old_pc = pc
        instructions_executed = 0
        clock_cycles = 0

        is_pipeline_empty = False

        while 0 <= pc < len(instructions) or not is_pipeline_empty:
            old_pc = pc
            
            if not quiet:
                print(f"PC: {pc}")
            
            if pc >= len(instructions):
                pc = len(instructions) - 1  # Prevent out-of-bounds access
            pc, is_pipeline_empty, instruction_executed = self.pipeline.hazard_resolution(
                pc, self.registers, self.memory, self.alu, instructions, cache_hierarchy=self.cache_hierarchy
            )

            if not quiet:
                print("Buffers:")
                print(f"IF_RF_Buffer: {self.pipeline.IF_RF_Buffer}")
                print(f"RF_EX_Buffer: {self.pipeline.RF_EX_Buffer}")
                print(f"EX_MEM_Buffer: {self.pipeline.EX_MEM_Buffer}")
                print(f"MEM_WB_Buffer: {self.pipeline.MEM_WB_Buffer}")
                print("Registers:")
                print(f"x1: {self.registers.registers[1].value}")
                print(f"x2: {self.registers.registers[2].value}")
                print(f"x3: {self.registers.registers[3].value}")
                print(f"x4: {self.registers.registers[4].value}")
                print(f"x5: {self.registers.registers[5].value}")
                print(f"x6: {self.registers.registers[6].value}")
                print(f"x7: {self.registers.registers[7].value}")
                print(f"x8: {self.registers.registers[8].value}")
                print(f"x28: {self.registers.registers[28].value}")
                print(f"x29: {self.registers.registers[29].value}")
                print(f"x30: {self.registers.registers[30].value}")

            if instruction_executed:
                instructions_executed += 1

            clock_cycles += 1

        # Flush all dirty cache lines to main memory after program execution completes
        self.cache_hierarchy.flush_all_caches()

        return instructions_executed, clock_cycles
    
    def execute_program_live(self, instructions: list[bit32]):
        """
        Execute a program cycle-by-cycle as a generator for live UI updates.
        
        Args:
            instructions: List of bit32 instruction objects
            
        Yields:
            Tuple of (instructions_executed, clock_cycles)
        """
        self._load_instructions_to_memory(instructions)
        self.pc = 0
        old_pc = 0
        instructions_executed = 0
        clock_cycles = 0

        is_pipeline_empty = False

        while 0 <= self.pc < len(instructions) or not is_pipeline_empty:
            old_pc = self.pc
            
            if self.pc >= len(instructions):
                self.pc = len(instructions) - 1  # Prevent out-of-bounds access
            # Execute one pipeline stage cycle
            self.pc, is_pipeline_empty, instruction_executed = self.pipeline.hazard_resolution(
                self.pc, self.registers, self.memory, self.alu, instructions, cache_hierarchy=self.cache_hierarchy
            )
            
            if instruction_executed:
                instructions_executed += 1
            
            clock_cycles += 1
            
            # Yield state for UI update
            yield instructions_executed, clock_cycles
        
        # Flush all dirty cache lines to main memory after program execution completes
        self.cache_hierarchy.flush_all_caches()