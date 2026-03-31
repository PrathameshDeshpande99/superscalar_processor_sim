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

    def run_program(self, instructions: list[bit32]) -> tuple[int, int]:
        """
        Execute a program from memory.
        
        Runs instructions in a 5-stage pipeline with hazard resolution and
        branch handling. Executes until program counter reaches end of instruction list.
        
        Args:
            instructions: List of 32-bit instruction words to execute
        
        Returns:
            tuple[int, int]: (number of instructions executed, total clock cycles)
        """
        pc = 0
        instructions_executed = 0
        clock_cycles = 0

        while 0 <= pc < len(instructions):
            old_pc = pc

            # Resolve hazards and update PC if needed
            pc = self.pipeline.hazard_resolution(pc)
            
            # Execute pipeline stages in reverse order (WB -> IF) to maintain
            # correct data dependencies within a single cycle
            self._execute_pipeline_cycle(instructions, pc)

            # Increment PC if we didn't stall
            if pc == old_pc:
                pc += 1

            # Update statistics
            if pc != old_pc:
                instructions_executed += 1

            clock_cycles += 1

        return instructions_executed, clock_cycles

    def _execute_pipeline_cycle(self, instructions: list[bit32], pc: int) -> None:
        """
        Execute one complete pipeline cycle through all stages.
        
        Stages are executed in reverse order to ensure that data produced by
        earlier stages is available to later stages within the same cycle.
        
        Execution order: WB -> MEM -> EX -> RF -> IF
        
        Args:
            instructions: List of instructions in memory
            pc: Current program counter
        """
        # Write-Back stage: Update register file
        self.pipeline.wb_stage(self.registers)
        
        # Memory stage: Load/Store operations
        self.pipeline.mem_stage(self.memory)
        
        # Execute stage: ALU operations
        self.pipeline.ex_stage(self.alu)
        
        # Register Fetch stage: Decode and read registers
        self.pipeline.rf_stage(self.registers)
        
        # Instruction Fetch stage: Load next instruction
        self.pipeline.if_stage(instructions, pc)

    def debug_print_registers(self, reg_indices: list[int] = None) -> None:
        """
        Print selected register values for debugging.
        
        Args:
            reg_indices: List of register indices to print. If None, prints x1-x8, x28-x30.
        """
        if reg_indices is None:
            reg_indices = list(range(1, 9)) + list(range(28, 31))
        
        print("Registers:")
        for idx in reg_indices:
            print(f"x{idx}: {self.registers.registers[idx].value}")

    def debug_print_memory(self, start_addr: int, num_words: int) -> None:
        """
        Print memory contents for debugging.
        
        Args:
            start_addr: Starting address for printing
            num_words: Number of 32-bit words to print
        """
        self.memory.debug_print_range(start_addr, num_words)

    def debug_print_pipeline_state(self) -> None:
        """Print the state of all pipeline buffers for debugging."""
        print("IF_RF_Buffer:", self.pipeline.IF_RF_Buffer)
        print("RF_EX_Buffer:", self.pipeline.RF_EX_Buffer)
        print("EX_MEM_Buffer:", self.pipeline.EX_MEM_Buffer)
        print("MEM_WB_Buffer:", self.pipeline.MEM_WB_Buffer)
