from utils import RF_EX_Buffer_Class, EX_MEM_Buffer_Class, MEM_WB_Buffer_Class, create_ex_mem_buffer, create_mem_wb_buffer, create_ex_mem_buffer, create_rf_ex_buffer, bit32, bit8

class Pipeline:
    # objects in the pipeline:
    # IF_RF_Buffer
    # RF_EX_Buffer
    # EX_MEM_Buffer
    # MEM_WB_Buffer

    def __init__(self):
        self.IF_RF_Buffer = create_rf_ex_buffer()
        self.RF_EX_Buffer = create_rf_ex_buffer()
        self.EX_MEM_Buffer = create_ex_mem_buffer()
        self.MEM_WB_Buffer = create_mem_wb_buffer()

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

        self.RF_EX_Buffer["A"] = A
        self.RF_EX_Buffer["B"] = B
        self.RF_EX_Buffer["rs1"] = rs1_index
        self.RF_EX_Buffer["rs2"] = rs2_index
        self.RF_EX_Buffer["rd"] = get_rd_index(instruction)

        opcode = get_opcode(instruction)
        funct3 = get_funct3(instruction)
        funct7 = get_funct7(instruction)

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

    def ex_stage(self, alu: ALU):
        def input_resolve() -> tuple[bit32, bit32]:
            A = self.RF_EX_Buffer["A"]

            # these cases are for immediate values in load and store instructions
            if self.RF_EX_Buffer["isImm"]:
                B = (bit32(self.RF_EX_Buffer["funct7"]) << 5) + bit32(self.RF_EX_Buffer["rs2"])
            elif self.RF_EX_Buffer["isSt"]:
                B = (bit32(self.RF_EX_Buffer["funct7"]) << 5) + bit32(self.RF_EX_Buffer["rd"])
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

    # TODO: use read / write from memory here instead of direct access
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
      