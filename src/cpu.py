from registers import Registers
from memory import Memory
from pipeline import Pipeline
from alu import ALU
from utils import bit32, create_mem_wb_buffer
from cache.cache_structure import Cache
import processor_config as config

import time

class CPU:
    def __init__(self):
        self.registers = Registers()
        self.memory = Memory()
        self.pipeline = Pipeline()
        self.alu = ALU()

        # Instantiate Caches
        self.l1i = Cache("L1I", config.L1_SIZE, config.BLOCK_SIZE, config.L1_ASSOCIATIVITY, config.L1_LATENCY, config.REPLACEMENT_POLICY)
        self.l1d = Cache("L1D", config.L1_SIZE, config.BLOCK_SIZE, config.L1_ASSOCIATIVITY, config.L1_LATENCY, config.REPLACEMENT_POLICY)
        self.l2 = Cache("L2", config.L2_SIZE, config.BLOCK_SIZE, config.L2_ASSOCIATIVITY, config.L2_LATENCY, config.REPLACEMENT_POLICY)

    def run_program(self, instructions: list[bit32]):
        pc = 0
        old_pc = pc
        instructions_executed = 0
        clock_cycles = 0
        total_stalls = 0

        while 0 <= pc < len(instructions):
            old_pc = pc
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