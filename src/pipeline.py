"""
Pipeline module for the superscalar processor simulator.

Implements a 5-stage pipeline (IF, RF, EX, MEM, WB) with hazard resolution,
data forwarding, and branch handling. Manages pipeline buffers and coordinates
execution across all pipeline stages.
"""

from utils import (IF_RF_Buffer_Class, RF_EX_Buffer_Class, EX_MEM_Buffer_Class, 
                   MEM_WB_Buffer_Class, create_if_rf_buffer, create_rf_ex_buffer, 
                   create_ex_mem_buffer, create_mem_wb_buffer, bit32, bit5, bin_to_signed)
from alu import ALU
from processor_config import DATA_FORWARDING_ENABLED


class Pipeline:
    """
    5-stage pipeline implementation for RISC-V instruction execution.
    
    Stages:
        IF (Instruction Fetch): Load instruction from memory
        RF (Register Fetch): Read register operands and decode instruction
        EX (Execute): Perform ALU operations
        MEM (Memory): Access memory for load/store operations
        WB (Write-Back): Write results back to registers
    """

    def __init__(self):
        """Initialize all pipeline buffers with NOP instructions."""
        self.IF_RF_Buffer = create_if_rf_buffer()
        self.RF_EX_Buffer = create_rf_ex_buffer()
        self.EX_MEM_Buffer = create_ex_mem_buffer()
        self.MEM_WB_Buffer = create_mem_wb_buffer()

    # ============================================================================
    # Instruction Field Extraction Helpers
    # ============================================================================

    @staticmethod
    def _extract_opcode(instruction: bit32) -> int:
        """Extract 7-bit opcode from bits [6:0]."""
        return instruction.value & 0x7F

    @staticmethod
    def _extract_funct3(instruction: bit32) -> int:
        """Extract 3-bit function code from bits [14:12]."""
        return (instruction.value >> 12) & 0x7

    @staticmethod
    def _extract_funct7(instruction: bit32) -> int:
        """Extract 7-bit function code from bits [31:25]."""
        return (instruction.value >> 25) & 0x7F

    @staticmethod
    def _extract_rs1(instruction: bit32) -> int:
        """Extract source register 1 index from bits [19:15]."""
        return (instruction.value >> 15) & 0x1F

    @staticmethod
    def _extract_rs2(instruction: bit32) -> int:
        """Extract source register 2 index from bits [24:20]."""
        return (instruction.value >> 20) & 0x1F

    @staticmethod
    def _extract_rd(instruction: bit32) -> int:
        """Extract destination register index from bits [11:7]."""
        return (instruction.value >> 7) & 0x1F

    # ============================================================================
    # Immediate Field Extraction
    # ============================================================================

    @staticmethod
    def _extract_jal_immediate(instruction: bit32) -> int:
        """Extract 20-bit sign-extended immediate from JAL instruction."""
        inst_str = format(instruction.value, '032b')
        immediate_str = inst_str[0] + inst_str[12:20] + inst_str[11] + inst_str[1:11]
        return bin_to_signed(immediate_str)

    @staticmethod
    def _extract_branch_immediate(instruction: bit32) -> int:
        """Extract 12-bit sign-extended immediate from branch instruction."""
        inst_str = format(instruction.value, '032b')
        immediate_str = inst_str[0] + inst_str[24] + inst_str[1:7] + inst_str[20:24]
        return bin_to_signed(immediate_str)

    @staticmethod
    def _extract_itype_immediate(funct7: int, rs2: bit5) -> int:
        """Extract 12-bit sign-extended immediate from I-type instruction."""
        immediate_str = format(funct7, '07b') + str(rs2)
        return bin_to_signed(immediate_str)

    @staticmethod
    def _extract_stype_immediate(funct7: int, rd: bit5) -> int:
        """Extract 12-bit sign-extended immediate from S-type instruction."""
        immediate_str = format(funct7, '07b') + str(rd)
        return bin_to_signed(immediate_str)

    # ============================================================================
    # Instruction Decoding
    # ============================================================================

    @staticmethod
    def _decode_instruction(opcode: int, funct3: int, funct7: int) -> dict:
        """
        Decode instruction type from opcode and function codes.
        
        Returns a dict with boolean flags: isAdd, isSub, isLd, isSt, isAddi
        """
        return {
            'isAdd': opcode == 0b0110011 and funct3 == 0b000 and funct7 == 0b0000000,
            'isSub': opcode == 0b0110011 and funct3 == 0b000 and funct7 == 0b0100000,
            'isAddi': opcode == 0b0010011 and funct3 == 0b000,
            'isLd': opcode == 0b0000011,
            'isSt': opcode == 0b0100011,
        }

    # ============================================================================
    # Pipeline Stages
    # ============================================================================

    def if_stage(self, instructions: list[bit32], pc: int) -> int:
        """
        Instruction Fetch stage: Load instruction from memory.
        
        Args:
            instructions: List of instructions in memory
            pc: Current program counter
        
        Returns:
            int: Updated program counter (pc + 1)
        """
        self.IF_RF_Buffer["instruction"] = instructions[pc]
        return pc + 1

    def rf_stage(self, registers):
        """
        Register Fetch stage: Decode instruction and read operands.
        
        Decodes the instruction format, reads register values, extracts immediates,
        detects branches, and identifies instruction type.
        
        Supported instructions: ADD, SUB, ADDI, LW, SW, BEQ, BNE, BLT, BGE, JAL
        
        Args:
            registers: Registers object for reading operand values
        """
        instruction = self.IF_RF_Buffer["instruction"]

        # Extract instruction fields
        opcode = self._extract_opcode(instruction)
        funct3 = self._extract_funct3(instruction)
        funct7 = self._extract_funct7(instruction)
        rs1_index = self._extract_rs1(instruction)
        rs2_index = self._extract_rs2(instruction)
        rd_index = self._extract_rd(instruction)

        # Read operands from register file
        A = registers.read(rs1_index)
        B = registers.read(rs2_index)

        # Store basic information in RF_EX buffer
        self.RF_EX_Buffer["instruction"] = instruction
        self.RF_EX_Buffer["A"] = A
        self.RF_EX_Buffer["B"] = B
        self.RF_EX_Buffer["rs1"] = bit5(rs1_index)
        self.RF_EX_Buffer["rs2"] = bit5(rs2_index)
        self.RF_EX_Buffer["rd"] = bit5(rd_index)
        self.RF_EX_Buffer["funct7"] = funct7

        # Handle unconditional branch (JAL)
        if opcode == 0b1101111:
            immediate = self._extract_jal_immediate(instruction)
            self.RF_EX_Buffer["isBranchTaken"] = True
            self.RF_EX_Buffer["branch_offset"] = immediate >> 2

        # Handle conditional branches
        elif opcode == 0b1100011:
            immediate = self._extract_branch_immediate(instruction)
            branch_taken = self._evaluate_branch(funct3, A, B)
            
            self.RF_EX_Buffer["isBranchTaken"] = branch_taken
            if branch_taken:
                self.RF_EX_Buffer["branch_offset"] = immediate >> 2
        else:
            self.RF_EX_Buffer["isBranchTaken"] = False

        # Decode instruction type
        instr_type = self._decode_instruction(opcode, funct3, funct7)
        
        is_addi = instr_type['isAddi']
        is_store = instr_type['isSt']
        do_writeback = any([instr_type['isAdd'], instr_type['isSub'], 
                           instr_type['isLd'], is_addi])

        # Store instruction type flags
        self.RF_EX_Buffer["isAdd"] = instr_type['isAdd'] or is_addi
        self.RF_EX_Buffer["isSub"] = instr_type['isSub']
        self.RF_EX_Buffer["isImm"] = is_addi or instr_type['isLd']
        self.RF_EX_Buffer["isLd"] = instr_type['isLd']
        self.RF_EX_Buffer["isSt"] = is_store
        self.RF_EX_Buffer["doWB"] = do_writeback

        # For store instructions, prevent unnecessary data hazards by setting rd to x0
        if is_store:
            self.RF_EX_Buffer["rd"] = bit5(0)

    @staticmethod
    def _evaluate_branch(funct3: int, A: bit32, B: bit32) -> bool:
        """
        Evaluate conditional branch condition.
        
        Args:
            funct3: Function code identifying branch type
            A: First operand
            B: Second operand
        
        Returns:
            bool: True if branch condition is satisfied
        """
        if funct3 == 0b000:  # BEQ
            return A == B
        elif funct3 == 0b001:  # BNE
            return A != B
        elif funct3 == 0b100:  # BLT
            signedA = bin_to_signed(str(A))
            signedB = bin_to_signed(str(B))
            return signedA < signedB
        elif funct3 == 0b101:  # BGE
            signedA = bin_to_signed(str(A))
            signedB = bin_to_signed(str(B))
            return signedA >= signedB
        return False

    def ex_stage(self, alu: ALU):
        """
        Execute stage: Perform ALU operation and compute result.
        
        Resolves input operands (immediate or register), executes ALU operation,
        and passes result to next stage.
        
        Args:
            alu: ALU object for performing arithmetic/logic operations
        """
        A, B = self._resolve_ex_inputs()
        
        # Compute ALU result
        alu_result = alu.Adder(A, B, self.RF_EX_Buffer["isAdd"], 
                              self.RF_EX_Buffer["isSub"], 
                              self.RF_EX_Buffer["isLd"],
                              self.RF_EX_Buffer["isSt"])

        # Pass results to EX_MEM buffer
        self.EX_MEM_Buffer["rd"] = self.RF_EX_Buffer["rd"]
        self.EX_MEM_Buffer["isLd"] = self.RF_EX_Buffer["isLd"]
        self.EX_MEM_Buffer["isSt"] = self.RF_EX_Buffer["isSt"]
        self.EX_MEM_Buffer["alu_result"] = alu_result
        self.EX_MEM_Buffer["doWB"] = self.RF_EX_Buffer["doWB"]
        self.EX_MEM_Buffer["rs2_value"] = self.RF_EX_Buffer["B"]

    def _resolve_ex_inputs(self) -> tuple[bit32, bit32]:
        """
        Resolve EX stage input operands.
        
        For immediate instructions (ADDI, LW, SW), extracts the immediate value.
        For register instructions (ADD, SUB), uses register value from RF_EX buffer.
        
        Returns:
            tuple[bit32, bit32]: Resolved operands (A, B)
        """
        A = self.RF_EX_Buffer["A"]

        if self.RF_EX_Buffer["isImm"]:
            # Extract immediate from I-type instruction
            immediate = self._extract_itype_immediate(self.RF_EX_Buffer["funct7"],
                                                      self.RF_EX_Buffer["rs2"])
            B = bit32(immediate)
        elif self.RF_EX_Buffer["isSt"]:
            # Extract immediate from S-type instruction
            immediate = self._extract_stype_immediate(self.RF_EX_Buffer["funct7"],
                                                      self.RF_EX_Buffer["rd"])
            B = bit32(immediate)
        else:
            # Use register operand
            B = self.RF_EX_Buffer["B"]

        return A, B

    def mem_stage(self, memory):
        """
        Memory stage: Load or store data.
        
        For load instructions, reads data from memory at computed address.
        For store instructions, writes data to memory at computed address.
        For non-memory instructions, passes ALU result through.
        
        Args:
            memory: Memory object for load/store operations
        """
        if self.EX_MEM_Buffer["isLd"]:
            # Load word from memory
            self.MEM_WB_Buffer["writeback_value"] = memory.read_word(self.EX_MEM_Buffer["alu_result"])
        elif self.EX_MEM_Buffer["isSt"]:
            # Store word to memory
            memory.write_word(self.EX_MEM_Buffer["alu_result"], 
                            self.EX_MEM_Buffer["rs2_value"])
        else:
            # Pass ALU result through
            self.MEM_WB_Buffer["writeback_value"] = self.EX_MEM_Buffer["alu_result"]

        # Pass control signals to WB stage
        self.MEM_WB_Buffer["doWB"] = self.EX_MEM_Buffer["doWB"]
        self.MEM_WB_Buffer["rd"] = self.EX_MEM_Buffer["rd"]
        self.MEM_WB_Buffer["isLd"] = self.EX_MEM_Buffer["isLd"]
        self.MEM_WB_Buffer["rs2_value"] = self.EX_MEM_Buffer["rs2_value"]

    def wb_stage(self, registers):
        """
        Write-Back stage: Write result to register file.
        
        Writes the computed result to the destination register if write-back
        is enabled. Does not write to x0 (hardwired to zero).
        
        Args:
            registers: Registers object for writing results
        """
        if self.MEM_WB_Buffer["doWB"]:
            registers.write(self.MEM_WB_Buffer["rd"], 
                          self.MEM_WB_Buffer["writeback_value"])

    # ============================================================================
    # Hazard Resolution
    # ============================================================================

    def hazard_resolution(self, pc: int) -> int:
        """
        Detect and resolve pipeline hazards.
        
        Handles two types of hazards:
        1. Data hazards: When instruction depends on result not yet in register file
           - Solution: Data forwarding (if enabled) or pipeline stall
        2. Control hazards: When branch condition is resolved
           - Solution: Flush pipeline and jump to target address
        
        Note: Data hazard checking must occur before control hazard checking.
        
        Args:
            pc: Current program counter
        
        Returns:
            int: Updated program counter (may be decremented for stall or jumped for branch)
        """
        # Check for data hazards
        pc = self._handle_data_hazards(pc)
        
        # Check for control hazards
        if self.RF_EX_Buffer["isBranchTaken"]:
            pc = self._handle_branch(pc)
        
        return pc

    def _handle_data_hazards(self, pc: int) -> int:
        """
        Detect and handle data hazards.
        
        Returns the updated PC (pc - 1 for stall, or pc if no hazard).
        """
        ex_mem_hazard = self._has_ex_mem_hazard()
        mem_wb_hazard = self._has_mem_wb_hazard()

        if not (ex_mem_hazard or mem_wb_hazard):
            return pc

        if DATA_FORWARDING_ENABLED:
            return self._forward_data(pc, ex_mem_hazard, mem_wb_hazard)
        else:
            return self._stall_pipeline(pc)

    def _has_ex_mem_hazard(self) -> bool:
        """Check if EX/MEM buffer produces value needed by RF/EX buffer."""
        return (self.EX_MEM_Buffer["doWB"] and 
                self.EX_MEM_Buffer["rd"] != bit5(0) and 
                (self.EX_MEM_Buffer["rd"] == self.RF_EX_Buffer["rs1"] or 
                 self.EX_MEM_Buffer["rd"] == self.RF_EX_Buffer["rs2"]))

    def _has_mem_wb_hazard(self) -> bool:
        """Check if MEM/WB buffer produces value needed by RF/EX buffer."""
        return (self.MEM_WB_Buffer["doWB"] and 
                self.MEM_WB_Buffer["rd"] != bit5(0) and 
                (self.MEM_WB_Buffer["rd"] == self.RF_EX_Buffer["rs1"] or 
                 self.MEM_WB_Buffer["rd"] == self.RF_EX_Buffer["rs2"]))

    def _forward_data(self, pc: int, ex_mem_hazard: bool, mem_wb_hazard: bool) -> int:
        """Forward data from later pipeline stages to RF/EX stage."""
        if ex_mem_hazard and self.EX_MEM_Buffer["isLd"]:
            # Load-use hazard: must stall
            return self._stall_pipeline(pc)

        if ex_mem_hazard:
            # Forward from EX/MEM
            if self.EX_MEM_Buffer["rd"] == self.RF_EX_Buffer["rs1"]:
                self.RF_EX_Buffer["A"] = self.EX_MEM_Buffer["alu_result"]
            if self.EX_MEM_Buffer["rd"] == self.RF_EX_Buffer["rs2"]:
                self.RF_EX_Buffer["B"] = self.EX_MEM_Buffer["alu_result"]

        elif mem_wb_hazard:
            # Forward from MEM/WB
            if self.MEM_WB_Buffer["rd"] == self.RF_EX_Buffer["rs1"]:
                self.RF_EX_Buffer["A"] = self.MEM_WB_Buffer["writeback_value"]
            if self.MEM_WB_Buffer["rd"] == self.RF_EX_Buffer["rs2"]:
                self.RF_EX_Buffer["B"] = self.MEM_WB_Buffer["writeback_value"]

        return pc

    def _stall_pipeline(self, pc: int) -> int:
        """Insert a bubble (NOP) into pipeline and refetch current instruction."""
        self.IF_RF_Buffer["instruction"] = self.RF_EX_Buffer["instruction"]
        self.RF_EX_Buffer = create_rf_ex_buffer()
        return pc - 1

    def _handle_branch(self, pc: int) -> int:
        """Handle taken branch by flushing pipeline and jumping to target."""
        self.IF_RF_Buffer = create_if_rf_buffer()  # Flush IF_RF buffer
        # -2 offset: one instruction in IF, one in fetch queue pointed to by pc
        return pc + self.RF_EX_Buffer["branch_offset"] - 2
