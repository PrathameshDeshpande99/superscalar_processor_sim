"""
Module defining the processor pipeline and its stages.
"""

from utils import PRE_IF_Buffer_Class, IF_RF_Buffer_Class, RF_EX_Buffer_Class, EX_MEM_Buffer_Class, MEM_WB_Buffer_Class, create_pre_if_buffer, create_if_rf_buffer, create_rf_ex_buffer, create_ex_mem_buffer, create_mem_wb_buffer, bit32, bit8, bit5, bin_to_signed
from alu import ALU

from processor_config import DATA_FORWARDING_ENABLED

nop = bit32("00000000000000000000000000010011")

class Pipeline:
    """
    Processor pipeline managing instruction execution through multiple stages.
    """
    # objects in the pipeline:
    # IF_RF_Buffer
    # RF_EX_Buffer
    # EX_MEM_Buffer
    # MEM_WB_Buffer

    def __init__(self):
        """Initialize pipeline with default structures and buffers."""
        self.PRE_IF_Buffer = create_pre_if_buffer()
        self.IF_RF_Buffer = create_if_rf_buffer()
        self.RF_EX_Buffer = create_rf_ex_buffer()
        self.EX_MEM_Buffer = create_ex_mem_buffer()
        self.MEM_WB_Buffer = create_mem_wb_buffer()

    def if_stage(self, instructions: list[bit32], pc: int) -> int:
        """
        Instruction Fetch (IF) stage. Fetches instruction and updates buffer.

        Args:
            instructions (list[bit32]): Memory list containing instructions.
            pc (int): Program counter.

        Returns:
            int: The incremented program counter.
        """
        self.IF_RF_Buffer["instruction"] = instructions[pc]
        pc += 1
        return pc

    def rf_stage(self, registers):

        """
            Supported instructions are:
            - add
            - sub
            - addi
            - lw
            - sw
            - beq
            - bne
            - blt
            - bge
            - jal
        """

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

        # unconditional branch
        if opcode == 0b1101111:
            print("Branch taken")
            instruction_str = format(instruction.value, '032b')
            immediate_str = instruction_str[0] + instruction_str[12: 20] + instruction_str[11] + instruction_str[1: 11]
            immediate = bin_to_signed(immediate_str)
            print("Immediate string: ", immediate_str)
            print("Immediate value: ", immediate)

            self.RF_EX_Buffer["isBranchTaken"] = True
            self.RF_EX_Buffer["branch_offset"] = (immediate >> 2)  # divide by 4 because each instruction is 4 bytes

        # conditional branch
        elif opcode == 0b1100011:
            instruction_str = format(instruction.value, '032b')
            immediate_str = instruction_str[0] + instruction_str[24] + instruction_str[1:7] + instruction_str[20:24]
            immediate = bin_to_signed(immediate_str)

            print("Immediate value: ", immediate)

            branch_taken = False
            if funct3 == 0b000:     # beq case
                if A == B:
                    print("BEQ was taken")
                    branch_taken = True
            elif funct3 == 0b001:   # bne case
                if A != B:
                    branch_taken = True
            elif funct3 == 0b100:   # blt case
                signedA, signedB = bin_to_signed(str(A)), bin_to_signed(str(B))
                if signedA < signedB:
                    branch_taken = True
            elif funct3 == 0b101:   # bge case
                signedA, signedB = bin_to_signed(str(A)), bin_to_signed(str(B))
                if signedA >= signedB:
                    branch_taken = True

            if not branch_taken:
                self.RF_EX_Buffer["isBranchTaken"] = False
                print("Branch not taken")
            else:       # branch taken
                self.RF_EX_Buffer["isBranchTaken"] = True
                self.RF_EX_Buffer["branch_offset"] = (immediate >> 2)  # divide by 4 because each instruction is 4 bytes
        else:
            self.RF_EX_Buffer["isBranchTaken"] = False    
        
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

        # Note: For S-type store instructions, the "rd" field contains Imm[4:0] (lower 5 bits of offset),
        # not a destination register. Do NOT overwrite it with 0 as that would destroy offset information.

    def ex_stage(self, alu: ALU):
        """
        Execution (EX) stage. Resolves inputs and delegates to ALU operations.

        Args:
            alu (ALU): Reference to Arithmetic Logic Unit object.
        """
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
        """
        Memory Access (MEM) stage. Handles reads and writes from/to data memory.

        Args:
            memory (Memory): Reference to Data Memory unit.
        """
        if self.EX_MEM_Buffer["isLd"]:
            self.MEM_WB_Buffer["writeback_value"] = memory.read_word(self.EX_MEM_Buffer["alu_result"])

        elif self.EX_MEM_Buffer["isSt"]:
            memory.write_word(self.EX_MEM_Buffer["alu_result"], self.EX_MEM_Buffer["rs2_value"])

        else:
            self.MEM_WB_Buffer["writeback_value"] = self.EX_MEM_Buffer["alu_result"]

        self.MEM_WB_Buffer["doWB"] = self.EX_MEM_Buffer["doWB"]
        self.MEM_WB_Buffer["rd"] = self.EX_MEM_Buffer["rd"]
        self.MEM_WB_Buffer["isLd"] = self.EX_MEM_Buffer["isLd"]
        self.MEM_WB_Buffer["rs2_value"] = self.EX_MEM_Buffer["rs2_value"]

    def wb_stage(self, registers):
        """
        Write Back (WB) stage. Finalizes register updates.

        Args:
            registers (Registers): Reference to Register file.
        """
        if self.MEM_WB_Buffer["doWB"]:
            registers.write(self.MEM_WB_Buffer["rd"], self.MEM_WB_Buffer["writeback_value"])

    # NOTE: First Data hazards need to be checked, then control hazards
    def hazard_resolution(self, pc: int, registers, memory, alu, instructions) -> int:
        """
        Detection and resolution of data and control hazards across pipeline stages.

        Args:
            pc (int): Current program counter.
            registers (Registers): Reference to Register file.
            memory (Memory): Reference to Data Memory unit.
            alu (ALU): Reference to Arithmetic Logic Unit.
            instructions (list[bit32]): List of instruction objects.

        Returns:
            int: Resolved program counter (possibly stalled or redirected).
        """

        # PIPELINE FORWARDING IS NOT SUPPORTED AT ALL

        # Doing new approach for hazard resolution to handle control, data and structural hazards (new due to variable latencies)
        # APPROACH:
        # every clock cycle reduce remaining_cycles of each buffer by one. 
        # This decrement by 1 is only done for buffers which do not have a data dependencies among the ones already defined, then only you can decrement.
        # If any buffer is hit zero, it is ready to be moved to next buffer
        # only move when next buffer is found to be a nop
        # when a instruction is moved to next buffer, the current one has to be made a nop so that previous stages can know that it is free.

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


        self.PRE_IF_Buffer["remaining_cycles"] -= 1
        self.IF_RF_Buffer["remaining_cycles"] -= 1
         # if there is a hazard, we cannot decrement remaining_cycles of RF_EX_Buffer because it is not moving to next buffer, so we are giving it another cycle to resolve the hazard
        if not ex_mem_hazard and not mem_wb_hazard:
            self.RF_EX_Buffer["remaining_cycles"] -= 1
        self.EX_MEM_Buffer["remaining_cycles"] -= 1
        self.MEM_WB_Buffer["remaining_cycles"] -= 1


        if self.MEM_WB_Buffer["remaining_cycles"] == 0:
            self.wb_stage(registers)
            self.MEM_WB_Buffer = create_mem_wb_buffer()   # make it nop after moving

        if self.EX_MEM_Buffer["remaining_cycles"] == 0 and self.MEM_WB_Buffer["instruction"] == nop:
            self.mem_stage(memory)
            self.EX_MEM_Buffer = create_ex_mem_buffer()   # make it nop after moving

        if self.RF_EX_Buffer["remaining_cycles"] == 0 and self.EX_MEM_Buffer["instruction"] == nop:
            self.ex_stage(alu)
            self.RF_EX_Buffer = create_rf_ex_buffer()     # make it nop after moving

        if self.IF_RF_Buffer["remaining_cycles"] == 0 and self.RF_EX_Buffer["instruction"] == nop:
            self.rf_stage(registers)
            self.IF_RF_Buffer = create_if_rf_buffer()     # make it nop after moving

        if self.PRE_IF_Buffer["remaining_cycles"] == 0 and self.IF_RF_Buffer["instruction"] == nop:
            self.if_stage(instructions, pc)
            self.PRE_IF_Buffer = create_pre_if_buffer()   # make it nop after moving
            pc += 1    # increment pc only when instruction is actually fetched

        return pc
        
        # # CONTROL HAZARDS:
        # if self.RF_EX_Buffer["isBranchTaken"]:
        #     print("Stall due to control hazard")

        #     # flush the currently fetched function in IF_RF Buffer
        #     self.IF_RF_Buffer = create_if_rf_buffer()   # nop
        #     print("New pc:", pc + self.RF_EX_Buffer["branch_offset"] - 2)
        #     return pc + self.RF_EX_Buffer["branch_offset"] - 2      # -2 because pipeline had next 2 instructions lined up: one in IF stage, other pointed by pc

        # return pc   # if no hazard, continue normal execution
