"""
Unified assembly pipeline that combines text-to-JSON conversion and JSON-to-binary assembly.
Provides a single function to load and assemble programs from the assembly_programs/ folder.
"""

import json
from pathlib import Path
from utils import bit32


def _convert_asm_text_to_dict(text_content: str) -> dict:
    """
    Convert assembly text to a dictionary format.
    
    Args:
        text_content: Assembly program text content.
    
    Returns:
        Dictionary with instruction lines indexed by number.
    """
    data = {}
    i = 1
    
    for line in text_content.split('\n'):
        # Remove comments and extra whitespace
        line = line.split("#")[0].strip().replace(",", " ")
        
        if line == "":
            continue
        
        data[str(i)] = line
        i += 1
    
    return data


def _assemble_instructions(asm_dict: dict) -> dict:
    """
    Convert assembly dictionary to binary instructions.
    
    Args:
        asm_dict: Dictionary with assembly instructions.
    
    Returns:
        Dictionary with binary instruction strings.
    """
    binary_data = {}
    
    for instruction_number in asm_dict:
        original_string = asm_dict[instruction_number]
        
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
            
            instruction_binary = func7 + bin_src_2 + bin_src_1 + func3 + bin_dst + opcode
            binary_data[instruction_number] = instruction_binary
        
        elif string_parts[0] == "lw":
            dest_reg = string_parts[1][1:]
            
            # for source
            source_reg = string_parts[2]
            # offset
            imm = source_reg.split("(")[0]
            # base val
            base_val = source_reg.split("(")[1][:-1]
            base_val = base_val[1:]
            
            bin_dst = f"{int(dest_reg):05b}"
            bin_base = f"{int(base_val):05b}"
            bin_imm = f"{int(imm) & 0xFFF:012b}"
            
            func3 = "010"
            opcode = "0000011"
            
            instruction_binary = bin_imm + bin_base + func3 + bin_dst + opcode
            binary_data[instruction_number] = instruction_binary
        
        elif string_parts[0] == "addi":
            dest_reg = string_parts[1][1:]
            source_reg = string_parts[2][1:]
            imm = string_parts[3]
            
            bin_dst = f"{int(dest_reg):05b}"
            bin_src = f"{int(source_reg):05b}"
            bin_imm = f"{int(imm) & 0xFFF:012b}"
            
            func3 = "000"
            opcode = "0010011"
            
            instruction_binary = bin_imm + bin_src + func3 + bin_dst + opcode
            binary_data[instruction_number] = instruction_binary
        
        elif string_parts[0] == "sw":
            source_2 = string_parts[1][1:]
            
            # for source_2
            source_reg = string_parts[2]
            # offset
            offset = source_reg.split("(")[0]
            
            # base val
            base_val = source_reg.split("(")[1][:-1]
            source_1 = base_val[1:]
            
            bin_src_2 = f"{int(source_2):05b}"
            bin_src_1 = f"{int(source_1):05b}"
            bin_offset = f"{int(offset) & 0xFFF:012b}"
            bin_imm_1 = bin_offset[:7]
            bin_imm_2 = bin_offset[7:]
            
            func3 = "010"
            opcode = "0100011"
            
            instruction_binary = (
                bin_imm_1 + bin_src_2 + bin_src_1 + func3 + bin_imm_2 + opcode
            )
            binary_data[instruction_number] = instruction_binary
        
        elif (
            string_parts[0] == "beq"
            or string_parts[0] == "bne"
            or string_parts[0] == "blt"
            or string_parts[0] == "bge"
        ):
            source_1 = string_parts[1][1:]
            source_2 = string_parts[2][1:]
            
            goto_label = string_parts[3]
            i = int(instruction_number)
            j = int(instruction_number)
            offset = 0
            
            while i >= 1 or j <= len(asm_dict):
                if i >= 1 and (goto_label + ":" in asm_dict.get(str(i), "")):
                    offset = i - int(instruction_number)
                    break
                elif j <= len(asm_dict) and (goto_label + ":" in asm_dict.get(str(j), "")):
                    offset = j - int(instruction_number)
                    break
                else:
                    if i >= 1:
                        i -= 1
                    if j <= len(asm_dict):
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
            
            instruction_binary = (
                bin_imm_1 + bin_src_2 + bin_src_1 + func3 + bin_imm_2 + opcode
            )
            binary_data[instruction_number] = instruction_binary
        
        elif string_parts[0] == "jal":
            dest_reg = string_parts[1][1:]
            goto_label = string_parts[2]
            
            i = int(instruction_number)
            j = int(instruction_number)
            offset = 0
            
            while i >= 1 or j <= len(asm_dict):
                if i >= 1 and (goto_label + ":" in asm_dict.get(str(i), "")):
                    offset = i - int(instruction_number)
                    break
                elif j <= len(asm_dict) and (goto_label + ":" in asm_dict.get(str(j), "")):
                    offset = j - int(instruction_number)
                    break
                else:
                    if i >= 1:
                        i -= 1
                    if j <= len(asm_dict):
                        j += 1
            
            final_offset = offset * 4
            
            bin_dst = f"{int(dest_reg):05b}"
            bin_imm = f"{int(final_offset) & 0xFFFFF:020b}"
            
            bin_imm_final = bin_imm[0] + bin_imm[10:] + bin_imm[9] + bin_imm[1:9]
            
            opcode = "1101111"
            instruction_binary = bin_imm_final + bin_dst + opcode
            binary_data[instruction_number] = instruction_binary
        
        else:
            continue
    
    return binary_data


def assemble_program(program_name: str) -> list[bit32]:
    """
    Load an assembly program from the assembly_programs/ folder and assemble it.
    
    This function automates the entire pipeline:
    1. Reads the .txt assembly file
    2. Converts it to intermediate dictionary format
    3. Assembles to binary instructions
    4. Returns a list of bit32 instruction objects
    
    Args:
        program_name: Name of the program (with or without .txt extension).
                     File should be in assembly_programs/ folder.
    
    Returns:
        List of bit32 instruction objects ready for CPU execution.
    
    Example:
        instructions = assemble_program("sample")
        cpu.run_program(instructions)
    """
    # Handle program name variations
    if not program_name.endswith(".txt"):
        program_name = program_name + ".txt"
    
    # Construct path relative to this module
    program_path = Path(__file__).parent.parent / "assembly_programs" / program_name
    
    if not program_path.exists():
        raise FileNotFoundError(
            f"Assembly program not found: {program_path}\n"
            f"Make sure the file exists in the assembly_programs/ folder."
        )
    
    # Step 1: Read assembly file
    with open(program_path, "r") as f:
        text_content = f.read()
    
    # Step 2: Convert text to dictionary format
    asm_dict = _convert_asm_text_to_dict(text_content)
    
    # Step 3: Assemble to binary instructions
    binary_data = _assemble_instructions(asm_dict)
    
    # Step 4: Convert binary strings to bit32 objects
    instructions = [
        bit32(binary_data[key])
        for key in sorted(binary_data.keys(), key=lambda x: int(x))
    ]
    
    # Add 4 NOP instructions at the end to prevent pipeline early exit
    nop_instruction = bit32("00000000000000000000000000010011")
    instructions.extend([nop_instruction] * 4)
    
    return instructions
