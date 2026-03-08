from registers import Registers
from memory import Memory
from pipeline import Pipeline
from alu import ALU
from utils import bit32, create_mem_wb_buffer

import time

class CPU:
    def __init__(self):
        self.registers = Registers()
        self.memory = Memory()
        self.pipeline = Pipeline()
        self.alu = ALU()

    def run_program(self, instructions: list[bit32]):
        pc = 0
        old_pc = pc
        instructions_executed = 0
        clock_cycles = 0

        while 0 <= pc < len(instructions):
            old_pc = pc
            print(f"PC: {pc}")

            pc = self.pipeline.hazard_resolution(pc)
            self.pipeline.wb_stage(self.registers)
            self.pipeline.mem_stage(self.memory)
            self.pipeline.ex_stage(self.alu)
            self.pipeline.rf_stage(self.registers)
            self.pipeline.if_stage(instructions, pc)

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

            pc += 1

            if(pc != old_pc):
                instructions_executed += 1

            clock_cycles += 1

            # time.sleep(0.1)

        return instructions_executed, clock_cycles