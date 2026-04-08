"""
Assembler module for converting JSON-formatted parsed assembly into binary representation.
"""

import json

def assemble_instructions(data):
    """
    Convert JSON instruction data to binary instructions.
    
    Args:
        data: Dictionary of instruction numbers to assembly strings
        
    Returns:
        Dictionary of instruction numbers to binary string representations
    """
    binary_data = {}

    for Instruction_number in data:
        original_string = data[Instruction_number]

        if ":" in original_string:
            original_string = original_string.split(":")[1]

        if original_string == "":
            continue

        string_parts = original_string.split()

        if string_parts[0] == "add" or string_parts[0] == "sub":
            dest_reg = string_parts[1][1:]
            source_1 = string_parts[2][1:]
            source_2 = string_parts[3][1:]

            bin_dst = f"{int(dest_reg):05b}"
            bin_src_1 = f"{int(source_1):05b}"
            bin_src_2 = f"{int(source_2):05b}"

            func3 = "000"
            func7 = "0000000" if string_parts[0] == "add" else "0100000"
            opcode = "0110011"

            Instruction_binary = func7 + bin_src_2 + bin_src_1 + func3 + bin_dst + opcode

            binary_data[Instruction_number] = Instruction_binary

        elif string_parts[0] == "lw":
            dest_reg = string_parts[1][1:]

            # for source
            source_reg = string_parts[2]
            # ofset
            imm = source_reg.split("(")[0]
            # base val
            base_val = source_reg.split("(")[1][:-1]
            base_val = base_val[1:]

            bin_dst = f"{int(dest_reg):05b}"
            bin_base = f"{int(base_val):05b}"
            bin_imm = f"{int(imm) & 0xFFF:012b}"  # need to specify that 0xFFF asa 012b sets the minimum limit not the excat limit

            func3 = "010"
            opcode = "0000011"

            Instruction_binary = bin_imm + bin_base + func3 + bin_dst + opcode

            binary_data[Instruction_number] = Instruction_binary

        elif string_parts[0] == "addi":
            dest_reg = string_parts[1][1:]
            source_reg = string_parts[2][1:]
            imm = string_parts[3]

            bin_dst = f"{int(dest_reg):05b}"
            bin_src = f"{int(source_reg):05b}"
            bin_imm = f"{int(imm) & 0xFFF:012b}"

            func3 = "000"
            opcode = "0010011"

            Instruction_binary = bin_imm + bin_src + func3 + bin_dst + opcode

            binary_data[Instruction_number] = Instruction_binary

        elif string_parts[0] == "sw":
            source_2 = string_parts[1][1:]

            # for source_2
            source_reg = string_parts[2]
            # ofset
            offset = source_reg.split("(")[0]

            # base val
            base_val = source_reg.split("(")[1][:-1]

            source_1 = base_val[1:]

            bin_src_2 = f"{int(source_2):05b}"
            bin_src_1 = f"{int(source_1):05b}"
            bin_offset = f"{int(offset) & 0xFFF:012b}"  # same reason
            bin_imm_1 = bin_offset[:7]
            bin_imm_2 = bin_offset[7:]

            func3 = "010"
            opcode = "0100011"

            Instruction_binary = (
                bin_imm_1 + bin_src_2 + bin_src_1 + func3 + bin_imm_2 + opcode
            )

            binary_data[Instruction_number] = Instruction_binary

        elif (
            string_parts[0] == "beq"
            or string_parts[0] == "bne"
            or string_parts[0] == "blt"
            or string_parts[0] == "bge"
        ):
            source_1 = string_parts[1][1:]
            source_2 = string_parts[2][1:]

            goto_label = string_parts[3]
            i = int(Instruction_number)
            j = int(Instruction_number)
            offset = 0
            while i >= 1 or j <= len(data):
                if i >= 1 and (goto_label + ":" in data[str(i)]):
                    offset = i - int(Instruction_number)
                    break
                elif j <= len(data) and (goto_label + ":" in data[str(j)]):
                    offset = j - int(Instruction_number)
                    break
                else:
                    if i >= 1:
                        i -= 1
                    if j <= len(data):
                        j += 1

            final_offset = offset * 4

            bin_src_1 = f"{int(source_1):05b}"
            bin_src_2 = f"{int(source_2):05b}"
            bin_offset = f"{int(final_offset) & 0xFFF:012b}"
            bin_imm_1 = bin_offset[0] + bin_offset[2:8]
            bin_imm_2 = bin_offset[8:12] + bin_offset[1]

            func3 = ""
            if string_parts[0] == "beq":
                func3 = "000"
            elif string_parts[0] == "blt":
                func3 = "100"
            elif string_parts[0] == "bne":
                func3 = "001"
            elif string_parts[0] == "bge":
                func3 = "101"

            opcode = "1100011"

            Instruction_binary = (
                bin_imm_1 + bin_src_2 + bin_src_1 + func3 + bin_imm_2 + opcode
            )

            binary_data[Instruction_number] = Instruction_binary

        elif string_parts[0] == "jal":
            dest_reg = string_parts[1][1:]
            goto_label = string_parts[2]

            i = int(Instruction_number)
            j = int(Instruction_number)
            offset = 0

            while i >= 1 or j <= len(data):
                if i >= 1 and (goto_label + ":" in data[str(i)]):
                    offset = i - int(Instruction_number)
                    break
                elif j <= len(data) and (goto_label + ":" in data[str(j)]):
                    offset = j - int(Instruction_number)
                    break
                else:
                    if i >= 1:
                        i -= 1
                    if j <= len(data):
                        j += 1

            final_offset = offset * 4

            bin_dst = f"{int(dest_reg):05b}"
            bin_imm = f"{int(final_offset) & 0xFFFFF:020b}"

            bin_imm_final = bin_imm[0] + bin_imm[10:] + bin_imm[9] + bin_imm[1:9]

            opcode = "1101111"
            Instruction_binary = bin_imm_final + bin_dst + opcode

            binary_data[Instruction_number] = Instruction_binary

        else:
            continue

    return binary_data


# Legacy support: automatically assemble instructions from hardcoded files
if __name__ == "__main__":
    json_file = "json_input.json"
    binary_instruction_file = "binary_input.json"
    
    with open(json_file, "r") as f:
        data = json.load(f)
    
    binary_data = assemble_instructions(data)
    
    with open(binary_instruction_file, "w") as f2:
        json.dump(binary_data, f2, indent=4)
