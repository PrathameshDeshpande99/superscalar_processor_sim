"""
Automated workflow to load and assemble instruction files from assembly_programs/
This module provides a pipeline that converts assembly files to Python lists of bit32 instructions.
"""

import json
import os
import tempfile
from pathlib import Path
from Convertor import convert_asm_to_json
from Assembler import assemble_instructions
from utils import bit32


def load_instructions(asm_filename, add_nops=4):
    """
    Load an assembly program and convert it to a list of bit32 instructions.
    
    Args:
        asm_filename: Name of the assembly file (with or without .asm/.txt extension)
                      Should be in assembly_programs/ directory
        add_nops: Number of NOP instructions to append at the end (default: 4)
        
    Returns:
        List of bit32 instruction objects
        
    Raises:
        FileNotFoundError: If the assembly file cannot be found
        ValueError: If the assembly file cannot be processed
    """
    # Get the workspace root directory
    src_dir = Path(__file__).parent
    workspace_root = src_dir.parent
    asm_dir = workspace_root / "assembly_programs"
    
    # Find the assembly file
    asm_file_path = None
    for ext in ['', '.asm', '.txt']:
        candidate = asm_dir / (asm_filename + ext if ext else asm_filename)
        if candidate.exists():
            asm_file_path = candidate
            break
    
    if asm_file_path is None:
        raise FileNotFoundError(
            f"Assembly file '{asm_filename}' not found in {asm_dir}. "
            f"Tried: {asm_filename}, {asm_filename}.asm, {asm_filename}.txt"
        )
    
    # Create a temporary directory for intermediate JSON files
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_json = os.path.join(temp_dir, "temp_instructions.json")
        
        # Step 1: Convert assembly to JSON
        try:
            convert_asm_to_json(str(asm_file_path), temp_json)
        except Exception as e:
            raise ValueError(f"Failed to convert assembly to JSON: {e}")
        
        # Step 2: Load the JSON data
        try:
            with open(temp_json, "r") as f:
                json_data = json.load(f)
        except Exception as e:
            raise ValueError(f"Failed to load JSON data: {e}")
        
        # Step 3: Assemble instructions (JSON to binary)
        try:
            binary_data = assemble_instructions(json_data)
        except Exception as e:
            raise ValueError(f"Failed to assemble instructions: {e}")
    
    # Step 4: Convert binary strings to bit32 objects
    instructions = []
    for instr_num in sorted(binary_data.keys(), key=lambda x: int(x)):
        binary_str = binary_data[instr_num]
        instructions.append(bit32(binary_str))
    
    # Step 5: Add NOPs at the end
    nop = bit32("00000000000000000000000000010011")  # NOP instruction
    for _ in range(add_nops):
        instructions.append(nop)
    
    return instructions
