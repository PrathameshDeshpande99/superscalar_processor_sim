# not using this file
import re

# ============================================================
# Instruction Specification
# ============================================================

INSTRUCTION_SET = {
    # R-Type
    "add": {"type": "R", "opcode": "0110011", "funct3": "000", "funct7": "0000000"},
    "sub": {"type": "R", "opcode": "0110011", "funct3": "000", "funct7": "0100000"},
    # I-Type
    "addi": {"type": "I", "opcode": "0010011", "funct3": "000"},
    "lw": {"type": "I", "opcode": "0000011", "funct3": "010"},
    # S-Type
    "sw": {"type": "S", "opcode": "0100011", "funct3": "010"},
    # B-Type
    "bne": {"type": "B", "opcode": "1100011", "funct3": "001"},
    # J-Type
    "jal": {"type": "J", "opcode": "1101111"},
}


# ============================================================
# Utility Functions
# ============================================================


def to_binary(value, bits):
    """Convert signed integer to binary of fixed width."""
    if value < 0:
        value = (1 << bits) + value
    return format(value, f"0{bits}b")


def parse_register(reg):
    """Parse x0, x1, ..., x31"""
    return int(reg.replace("x", "").strip())


# ============================================================
# Encoding Functions
# ============================================================


def encode_r_type(spec, rd, rs1, rs2):
    return (
        spec["funct7"]
        + to_binary(rs2, 5)
        + to_binary(rs1, 5)
        + spec["funct3"]
        + to_binary(rd, 5)
        + spec["opcode"]
    )


def encode_i_type(spec, rd, rs1, imm):
    return (
        to_binary(imm, 12)
        + to_binary(rs1, 5)
        + spec["funct3"]
        + to_binary(rd, 5)
        + spec["opcode"]
    )


def encode_s_type(spec, rs1, rs2, imm):
    imm_bin = to_binary(imm, 12)
    return (
        imm_bin[:7]
        + to_binary(rs2, 5)
        + to_binary(rs1, 5)
        + spec["funct3"]
        + imm_bin[7:]
        + spec["opcode"]
    )


def encode_b_type(spec, rs1, rs2, imm):
    imm_bin = to_binary(imm, 13)  # 13 bits for signed branch
    return (
        imm_bin[0]
        + imm_bin[2:8]
        + to_binary(rs2, 5)
        + to_binary(rs1, 5)
        + spec["funct3"]
        + imm_bin[8:12]
        + imm_bin[1]
        + spec["opcode"]
    )


def encode_j_type(spec, rd, imm):
    imm_bin = to_binary(imm, 21)
    return (
        imm_bin[0]
        + imm_bin[10:20]
        + imm_bin[9]
        + imm_bin[1:9]
        + to_binary(rd, 5)
        + spec["opcode"]
    )


# ============================================================
# Assembler Class
# ============================================================


class Assembler:
    def __init__(self):
        self.labels = {}
        self.instructions = []

    # -----------------------------
    # First Pass: Collect Labels
    # -----------------------------
    def first_pass(self, lines):
        pc = 0
        for line in lines:
            line = self.clean_line(line)
            if not line:
                continue

            if ":" in line:
                label, rest = line.split(":", 1)
                self.labels[label.strip()] = pc
                line = rest.strip()

            if line:
                pc += 4

    # -----------------------------
    # Second Pass: Encode
    # -----------------------------
    def second_pass(self, lines):
        pc = 0
        for line in lines:
            original_line = line
            line = self.clean_line(line)
            if not line:
                continue

            if ":" in line:
                _, line = line.split(":", 1)
                line = line.strip()
                if not line:
                    continue

            binary = self.encode_instruction(line, pc)
            self.instructions.append(binary)
            pc += 4

    # -----------------------------
    # Instruction Encoding
    # -----------------------------
    def encode_instruction(self, line, pc):
        tokens = re.split(r"[,\s()]+", line)
        tokens = [t for t in tokens if t]

        mnemonic = tokens[0].lower()
        spec = INSTRUCTION_SET[mnemonic]

        if spec["type"] == "R":
            rd = parse_register(tokens[1])
            rs1 = parse_register(tokens[2])
            rs2 = parse_register(tokens[3])
            return encode_r_type(spec, rd, rs1, rs2)

        elif spec["type"] == "I":
            if mnemonic == "lw":
                rd = parse_register(tokens[1])
                imm = int(tokens[2])
                rs1 = parse_register(tokens[3])
            else:
                rd = parse_register(tokens[1])
                rs1 = parse_register(tokens[2])
                imm = int(tokens[3])
            return encode_i_type(spec, rd, rs1, imm)

        elif spec["type"] == "S":
            rs2 = parse_register(tokens[1])
            imm = int(tokens[2])
            rs1 = parse_register(tokens[3])
            return encode_s_type(spec, rs1, rs2, imm)

        elif spec["type"] == "B":
            rs1 = parse_register(tokens[1])
            rs2 = parse_register(tokens[2])
            label = tokens[3]
            offset = self.labels[label] - pc
            return encode_b_type(spec, rs1, rs2, offset)

        elif spec["type"] == "J":
            rd = parse_register(tokens[1])
            label = tokens[2]
            offset = self.labels[label] - pc
            return encode_j_type(spec, rd, offset)

    # -----------------------------
    # Helpers
    # -----------------------------
    def clean_line(self, line):
        line = line.split("#")[0]
        return line.strip()

    # -----------------------------
    # Public Interface
    # -----------------------------
    def assemble(self, filename):
        with open(filename, "r") as f:
            lines = f.readlines()

        self.first_pass(lines)
        self.second_pass(lines)
        return self.instructions


# ============================================================
# Example Usage
# ============================================================

if __name__ == "__main__":
    assembler = Assembler()
    machine_code = assembler.assemble("program.s")

    for instr in machine_code:
        print(instr)
