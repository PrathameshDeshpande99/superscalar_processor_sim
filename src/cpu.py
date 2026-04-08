"""
CPU module for the superscalar processor simulator.

Orchestrates the 5-stage pipeline execution, coordinates all processor components
(registers, memory, pipeline), and executes a sequence of instructions.
"""

from registers import Registers
from memory import Memory
from pipeline import Pipeline
from alu import ALU
from utils import bit32


class CPU:
    """Central Processing Unit that orchestrates instruction execution."""

    def __init__(self):
        """Initialize CPU with empty registers, memory, pipeline, and ALU."""
        self.registers = Registers()
        self.memory = Memory()
        self.pipeline = Pipeline()
        self.alu = ALU()
        self.pc = 0  # Store PC at class level for easier UI access

    def run_program(self, instructions: list[bit32]) -> tuple[int, int]:
        """Original blocking execution method."""
        instructions_executed = 0
        clock_cycles = 0

        for exec_count, cycles in self.execute_program_live(instructions):
            instructions_executed = exec_count
            clock_cycles = cycles
            
        return instructions_executed, clock_cycles

    def execute_program_live(self, instructions: list[bit32]):
        """
        Generator that executes the program and yields state at each clock cycle.
        This allows a UI to update live without blocking.
        
        Yields:
            tuple[int, int]: (instructions_executed, clock_cycles)
        """
        self.pc = 0
        instructions_executed = 0
        clock_cycles = 0

        while 0 <= self.pc < len(instructions):
            old_pc = self.pc

            # Resolve hazards and update PC if needed
            self.pc = self.pipeline.hazard_resolution(self.pc)
            
            # Execute pipeline stages in reverse order (WB -> IF) to maintain
            # correct data dependencies within a single cycle
            self._execute_pipeline_cycle(instructions, self.pc)

            # Increment PC if we didn't stall
            if self.pc == old_pc:
                self.pc += 1
                instructions_executed += 1

            clock_cycles += 1
            
            # Yield control back to the UI at the end of the clock cycle
            yield instructions_executed, clock_cycles

    def _execute_pipeline_cycle(self, instructions: list[bit32], pc: int) -> None:
        """Execute one complete pipeline cycle through all stages."""
        self.pipeline.wb_stage(self.registers)
        self.pipeline.mem_stage(self.memory)
        self.pipeline.ex_stage(self.alu)
        self.pipeline.rf_stage(self.registers)
        self.pipeline.if_stage(instructions, pc)

    def debug_print_registers(self, reg_indices: list[int] = None) -> None:
        if reg_indices is None:
            reg_indices = list(range(1, 9)) + list(range(28, 31))
        print("Registers:")
        for idx in reg_indices:
            print(f"x{idx}: {self.registers.registers[idx].value}")

    def debug_print_memory(self, start_addr: int, num_words: int) -> None:
        self.memory.debug_print_range(start_addr, num_words)

    def debug_print_pipeline_state(self) -> None:
        print("IF_RF_Buffer:", self.pipeline.IF_RF_Buffer)
        print("RF_EX_Buffer:", self.pipeline.RF_EX_Buffer)
        print("EX_MEM_Buffer:", self.pipeline.EX_MEM_Buffer)
        print("MEM_WB_Buffer:", self.pipeline.MEM_WB_Buffer)