from utils import IF_RF_Buffer_Class, RF_EX_Buffer_Class, EX_MEM_Buffer_Class, MEM_WB_Buffer_Class, create_if_rf_buffer, create_rf_ex_buffer, create_ex_mem_buffer, create_mem_wb_buffer, bit32, bit8, bit5, bin_to_signed
from alu import ALU

class Pipeline:
    # objects in the pipeline:
    # IF_RF_Buffer
    # RF_EX_Buffer
    # EX_MEM_Buffer
    # MEM_WB_Buffer

    def __init__(self):
        self.IF_RF_Buffer = create_if_rf_buffer()
        self.RF_EX_Buffer = create_rf_ex_buffer()
        self.EX_MEM_Buffer = create_ex_mem_buffer()
        self.MEM_WB_Buffer = create_mem_wb_buffer()

    def if_stage(self, instructions: list[bit32], pc: int) -> int:
        self.IF_RF_Buffer["instruction"] = instructions[pc]
        pc += 1
        return pc

    def rf_stage(self, registers):

        instruction = self.IF_RF_Buffer["instruction"]

        def get_opcode(inst: bit32) -> int:
            return inst.value & 0x7F

        def get_funct3(inst: bit32) -> int:
            return (inst.value >> 12) & 0x7

        def get_funct7(inst: bit32) -> int:
            return (inst.value >> 25) & 0x7F

        def get_rs1_index(inst: bit32) -> int:
            return (inst.value >> 15) & 0x1F

        def get_rs2_index(inst: bit32) -> int:
            return (inst.value >> 20) & 0x1F

        def get_rd_index(inst: bit32) -> int:
            return (inst.value >> 7) & 0x1F

        rs1_index = get_rs1_index(instruction)
        rs2_index = get_rs2_index(instruction)

        A = registers.read(rs1_index)
        B = registers.read(rs2_index)

        self.RF_EX_Buffer["instruction"] = instruction
        self.RF_EX_Buffer["A"] = A
        self.RF_EX_Buffer["B"] = B
        self.RF_EX_Buffer["rs1"] = bit5(rs1_index)
        self.RF_EX_Buffer["rs2"] = bit5(rs2_index)
        self.RF_EX_Buffer["rd"] = bit5(get_rd_index(instruction))

        opcode = get_opcode(instruction)
        funct3 = get_funct3(instruction)
        funct7 = get_funct7(instruction)

        # if branch instructions
        if opcode == 0b1100011:
            instruction_str = format(instruction.value, '032b')
            immediate_str = instruction_str[0] + instruction_str[24] + instruction_str[1:7] + instruction_str[20:24]
            immediate = bin_to_signed(immediate_str)

            print("Immediate value: ", immediate)

            branch_taken = False
            if funct3 == 0b000:     # beq case
                if A == B:
                    branch_taken = True
            elif funct3 == 0b001:   # bne case
                if A != B:
                    branch_taken = True
            elif funct3 == 0b100:   # blt case
                if A < B:
                    branch_taken = True
            elif funct3 == 0b101:   # bge case
                if A >= B:
                    branch_taken = True

            if not branch_taken:
                self.RF_EX_Buffer["isBranchTaken"] = False
                print("Branch not taken")
            else:       # branch taken
                self.RF_EX_Buffer["isBranchTaken"] = True
                self.RF_EX_Buffer["branch_offset"] = (immediate >> 2)  # divide by 4 because each instruction is 4 bytes
            
        else:
            isAdd = (opcode == 0b0110011 and funct3 == 0b000 and funct7 == 0b0000000)
            isSub = (opcode == 0b0110011 and funct3 == 0b000 and funct7 == 0b0100000)

            isLd = (opcode == 0b0000011)
            isSt = (opcode == 0b0100011)

            isAddi = (opcode == 0b0010011 and funct3 == 0b000)

            doWB = isAdd or isSub or isLd or isAddi

            isAdd = isAdd or isAddi
            isImm = isAddi or isLd

            self.RF_EX_Buffer["funct7"] = funct7
            self.RF_EX_Buffer["isAdd"] = isAdd
            self.RF_EX_Buffer["isSub"] = isSub
            self.RF_EX_Buffer["isImm"] = isImm
            self.RF_EX_Buffer["isLd"] = isLd
            self.RF_EX_Buffer["isSt"] = isSt
            self.RF_EX_Buffer["doWB"] = doWB
            self.RF_EX_Buffer["isBranchTaken"] = False

    def ex_stage(self, alu: ALU):
        def input_resolve() -> tuple[bit32, bit32]:
            A = self.RF_EX_Buffer["A"]

            # these cases are for immediate values in load and store instructions
            if self.RF_EX_Buffer["isImm"]:
                # convert to binary string first then call bin_to_signed 
                immediate_str = format(self.RF_EX_Buffer["funct7"], '07b') + str(self.RF_EX_Buffer["rs2"])
                B = bit32(bin_to_signed(immediate_str))
            elif self.RF_EX_Buffer["isSt"]:
                immediate_str = format(self.RF_EX_Buffer["funct7"], '07b') + str(self.RF_EX_Buffer["rd"])
                B = bit32(bin_to_signed(immediate_str))
            else:
                B = self.RF_EX_Buffer["B"]

            return A, B
        
        A, B = input_resolve()
    
        self.EX_MEM_Buffer["rd"] = self.RF_EX_Buffer["rd"]

        self.EX_MEM_Buffer["isLd"] = self.RF_EX_Buffer["isLd"]
        self.EX_MEM_Buffer["isSt"] = self.RF_EX_Buffer["isSt"]

        self.EX_MEM_Buffer["alu_result"] = alu.Adder(A, B, self.RF_EX_Buffer["isAdd"], self.RF_EX_Buffer["isSub"], self.RF_EX_Buffer["isLd"], self.RF_EX_Buffer["isSt"])

        self.EX_MEM_Buffer["doWB"] = self.RF_EX_Buffer["doWB"]

        # for store instruction, we need to pass the value of rs2 to memory access stage, so storing it in EX_MEM_Buffer
        self.EX_MEM_Buffer["rs2_value"] = self.RF_EX_Buffer["B"]

    """
        Note: Machine is Big Endian
    """

    def mem_stage(self, memory):
        if self.EX_MEM_Buffer["isLd"]:
            return_value = bit32(0)

            return_value += bit32(memory.read(self.EX_MEM_Buffer["alu_result"])) << 24
            return_value += bit32(memory.read(self.EX_MEM_Buffer["alu_result"] + bit32(1))) << 16
            return_value += bit32(memory.read(self.EX_MEM_Buffer["alu_result"] + bit32(2))) << 8
            return_value += bit32(memory.read(self.EX_MEM_Buffer["alu_result"] + bit32(3)))

            self.MEM_WB_Buffer["writeback_value"] = return_value

        elif self.EX_MEM_Buffer["isSt"]:
            memory.write(self.EX_MEM_Buffer["alu_result"], bit8(self.EX_MEM_Buffer["rs2_value"] >> 24))
            memory.write(self.EX_MEM_Buffer["alu_result"] + bit32(1), bit8(self.EX_MEM_Buffer["rs2_value"] >> 16))
            memory.write(self.EX_MEM_Buffer["alu_result"] + bit32(2), bit8(self.EX_MEM_Buffer["rs2_value"] >> 8))
            memory.write(self.EX_MEM_Buffer["alu_result"] + bit32(3), bit8(self.EX_MEM_Buffer["rs2_value"]))

        else:
            self.MEM_WB_Buffer["writeback_value"] = self.EX_MEM_Buffer["alu_result"]

        self.MEM_WB_Buffer["doWB"] = self.EX_MEM_Buffer["doWB"]
        self.MEM_WB_Buffer["rd"] = self.EX_MEM_Buffer["rd"]
        self.MEM_WB_Buffer["isLd"] = self.EX_MEM_Buffer["isLd"]
        self.MEM_WB_Buffer["rs2_value"] = self.EX_MEM_Buffer["rs2_value"]

    def wb_stage(self, registers):
        if self.MEM_WB_Buffer["doWB"]:
            registers.write(self.MEM_WB_Buffer["rd"], self.MEM_WB_Buffer["writeback_value"])

    # NOTE: First Data hazards need to be checked, then control hazards
    def hazard_resolution(self, pc: int) -> int:
        # DATA HAZARDS:

        # 1. Check for hazard from the instruction currently in the EX/MEM stage
        ex_mem_hazard = (
            self.EX_MEM_Buffer["doWB"] and 
            self.EX_MEM_Buffer["rd"] != bit5(0) and 
            (self.EX_MEM_Buffer["rd"] == self.RF_EX_Buffer["rs1"] or 
             self.EX_MEM_Buffer["rd"] == self.RF_EX_Buffer["rs2"])
        )

        # 2. Check for hazard from the instruction currently in the MEM/WB stage
        mem_wb_hazard = (
            self.MEM_WB_Buffer["doWB"] and 
            self.MEM_WB_Buffer["rd"] != bit5(0) and 
            (self.MEM_WB_Buffer["rd"] == self.RF_EX_Buffer["rs1"] or 
             self.MEM_WB_Buffer["rd"] == self.RF_EX_Buffer["rs2"])
        )

        if ex_mem_hazard or mem_wb_hazard:
            # send nop / bubble into the pipeline
            print("Stall due to data hazard")
            self.IF_RF_Buffer["instruction"] = self.RF_EX_Buffer["instruction"]     # instruction is sent again to starting of RF stage
            self.RF_EX_Buffer = create_rf_ex_buffer()
            return pc - 1    # refetch the last instruction

        
        # CONTROL HAZARDS:
        if self.RF_EX_Buffer["isBranchTaken"]:
            print("Stall due to control hazard")

            # flush the currently fetched function in IF_RF Buffer
            self.IF_RF_Buffer = create_if_rf_buffer()   # nop
            print("New pc:", pc + self.RF_EX_Buffer["branch_offset"] - 2)
            return pc + self.RF_EX_Buffer["branch_offset"] - 2      # -2 because pipeline had next 2 instructions lined up: one in IF stage, other pointed by pc

        return pc   # if no hazard, continue normal execution
