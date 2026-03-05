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
        pc = 0
        while 0 <= pc < len(instructions):
            print(f"PC: {pc}")
            print("Buffers:")
            print(f"IF_RF_Buffer: {self.pipeline.IF_RF_Buffer}")
            print(f"RF_EX_Buffer: {self.pipeline.RF_EX_Buffer}")
            print(f"EX_MEM_Buffer: {self.pipeline.EX_MEM_Buffer}")
            print(f"MEM_WB_Buffer: {self.pipeline.MEM_WB_Buffer}")
            print("Registers:")
            print(f"x1: {self.registers.registers[1]}")
            print(f"x2: {self.registers.registers[2]}")
            print(f"x3: {self.registers.registers[3]}")

            pc = self.pipeline.hazard_resolution(pc)
            self.pipeline.wb_stage(self.registers)
            self.pipeline.mem_stage(self.memory)
            self.pipeline.ex_stage(self.alu)
            self.pipeline.rf_stage(self.registers)
            self.pipeline.if_stage(instructions, pc)

            pc += 1