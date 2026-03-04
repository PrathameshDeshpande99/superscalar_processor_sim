from registers import Registers
from memory import Memory
from pipeline import Pipeline
from alu import ALU
from utils import bit32, create_mem_wb_buffer

class CPU:
    def __init__(self):
        self.registers = Registers()
        self.memory = Memory()
        self.pipeline = Pipeline()
        self.alu = ALU()

    def run_program(self, instructions: list[bit32]):
        for instruction in instructions:
            self.pipeline.IF_RF_Buffer["instruction"] = instruction

            self.pipeline.wb_stage(self.registers)
            self.pipeline.mem_stage(self.memory)
            self.pipeline.ex_stage(self.alu)
            self.pipeline.rf_stage(self.registers)