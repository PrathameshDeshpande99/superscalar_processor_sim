"""
Module defining the main CPU class and execution logic.
"""

from registers import Registers
from memory import Memory
from pipeline import Pipeline
from alu import ALU
from utils import bit32, create_mem_wb_buffer
from cache.cache_structure import Cache
import processor_config as config

import time

class CPU:
    """
    Central Processing Unit (CPU) encapsulating components like registers, memory, pipeline and ALU.
    """
    def __init__(self):
        """Initialize the CPU with all its internal components and state."""
        self.registers = Registers()
        self.memory = Memory()
        self.pipeline = Pipeline()
        self.alu = ALU()
        self.pc = 0  # Track current program counter

    def execute_cycle(self, instructions: list[bit32], pc: int) -> tuple[int, int]:
        """
        Execute a single cycle of the pipeline.
        
        Args:
            instructions: List of bit32 instruction objects
            pc: Current program counter
        
        Returns:
            Tuple of (new_pc, instructions_executed_this_cycle)
        """
        old_pc = pc
        
        pc = self.pipeline.hazard_resolution(pc)
        self.pipeline.wb_stage(self.registers)
        self.pipeline.mem_stage(self.memory)
        self.pipeline.ex_stage(self.alu)
        self.pipeline.rf_stage(self.registers)
        self.pipeline.if_stage(instructions, pc)
        
        pc += 1
        instructions_executed = 1 if (pc != old_pc) else 0
        
        return pc, instructions_executed

        # Instantiate Caches
        self.l1i = Cache("L1I", config.L1_SIZE, config.BLOCK_SIZE, config.L1_ASSOCIATIVITY, config.L1_LATENCY, config.REPLACEMENT_POLICY)
        self.l1d = Cache("L1D", config.L1_SIZE, config.BLOCK_SIZE, config.L1_ASSOCIATIVITY, config.L1_LATENCY, config.REPLACEMENT_POLICY)
        self.l2 = Cache("L2", config.L2_SIZE, config.BLOCK_SIZE, config.L2_ASSOCIATIVITY, config.L2_LATENCY, config.REPLACEMENT_POLICY)

    
    def run_program(self, instructions: list[bit32], quiet: bool = True):
        """
        Execute a program from a list of instructions.
        
        Args:
            instructions: List of bit32 instruction objects
            quiet: If True, suppress debug output. If False, print debug info each cycle.
        
        Returns:
            Tuple of (instructions_executed, clock_cycles)
        """
        
        pc = 0
        old_pc = pc
        instructions_executed = 0
        clock_cycles = 0
        total_stalls = 0

        while 0 <= pc < len(instructions):
            old_pc = pc
            
            if not quiet:
                print(f"PC: {pc}")

            pc = self.pipeline.hazard_resolution(pc)
            self.pipeline.wb_stage(self.registers)

            # MEM stage with cache
            mem_latency = self.pipeline.mem_stage(self.memory, self.l1d, self.l2)

            self.pipeline.ex_stage(self.alu)
            self.pipeline.rf_stage(self.registers)

            # IF stage with cache
            if_latency = self.pipeline.if_stage(instructions, pc, self.l1i, self.l2)

            # Calculate stalls and cycles
            # Base cycle is 1. Any additional latency is a stall.
            # In a real pipeline, these could overlap, but here we sum additional latencies.
            added_cycles = max(0, if_latency - 1) + max(0, mem_latency - 1)
            total_stalls += added_cycles
            clock_cycles += 1 + added_cycles

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
            print("Buffers:")
            # ... (previous print statements)

            pc += 1

            if(pc != old_pc):
                instructions_executed += 1

        # Output Final Stats
        print("\n--- Simulation Results ---")
        print(f"Total Instructions Executed: {instructions_executed}")
        print(f"Total Clock Cycles: {clock_cycles}")
        print(f"Total Stalls: {total_stalls}")
        print(f"IPC (Instructions Per Cycle): {instructions_executed / clock_cycles if clock_cycles > 0 else 0:.4f}")
        print(f"L1I Cache Miss Rate: {self.l1i.get_miss_rate():.4f}")
        print(f"L1D Cache Miss Rate: {self.l1d.get_miss_rate():.4f}")
        print(f"L2 Cache Miss Rate: {self.l2.get_miss_rate():.4f}")

        return instructions_executed, clock_cycles
    
    def execute_program_live(self, instructions: list[bit32]):
        """
        Execute a program cycle-by-cycle as a generator for live UI updates.
        
        Args:
            instructions: List of bit32 instruction objects
            
        Yields:
            Tuple of (instructions_executed, clock_cycles)
        """
        self.pc = 0
        old_pc = 0
        instructions_executed = 0
        clock_cycles = 0

        while 0 <= self.pc < len(instructions):
            old_pc = self.pc
            
            # Execute one pipeline stage cycle
            self.pc = self.pipeline.hazard_resolution(self.pc)
            self.pipeline.wb_stage(self.registers)
            self.pipeline.mem_stage(self.memory)
            self.pipeline.ex_stage(self.alu)
            self.pipeline.rf_stage(self.registers)
            self.pipeline.if_stage(instructions, self.pc)
            
            self.pc += 1
            
            if self.pc != old_pc:
                instructions_executed += 1
            
            clock_cycles += 1
            
            # Yield state for UI update
            yield instructions_executed, clock_cycles