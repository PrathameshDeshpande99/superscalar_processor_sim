# Automated Instruction Loading Workflow

## Overview
This document describes the automated workflow that has been implemented to assemble programs from the `assembly_programs/` folder directly into Python lists of instructions without manual intervention.

## Architecture

### Components

1. **Convertor.py** (Modified)
   - Now exports `convert_asm_to_json()` function
   - Converts assembly text files to JSON intermediate format
   - Preserves all original logic and behavior

2. **Assembler.py** (Refactored)
   - Extracted core logic into `assemble_instructions(data)` function
   - Converts JSON instruction data to binary string representations
   - No logic changes - just wrapped in a function
   - Maintains backward compatibility with legacy file-based approach

3. **instruction_loader.py** (New)
   - Main pipeline orchestrator
   - Path: `src/instruction_loader.py`
   - Provides `load_instructions(asm_filename, add_nops=4)` function
   - Seamlessly connects Convertor → Assembler pipeline
   - Returns ready-to-use list of `bit32` instruction objects

### Workflow Pipeline

```
Assembly File (*.asm, *.txt) 
    → Convertor.convert_asm_to_json()
    → JSON instruction data
    → Assembler.assemble_instructions()
    → Binary instruction strings
    → Convert to bit32 objects
    → Add NOP padding
    → Return instruction list
```

## Usage

### Basic Usage in main.py

```python
from instruction_loader import load_instructions

# Load an assembly program from assembly_programs/ folder
instructions = load_instructions("loop_test")  # Loads loop_test.asm or loop_test.txt
cpu = CPU()
cpu.run_program(instructions)
```

### Advanced Usage with Custom NOPs

```python
# Load with custom number of NOPs appended
instructions = load_instructions("my_program", add_nops=8)  # Adds 8 NOP instructions
```

### Error Handling

```python
from instruction_loader import load_instructions

try:
    instructions = load_instructions("my_program")
except FileNotFoundError as e:
    print(f"Assembly file not found: {e}")
except ValueError as e:
    print(f"Failed to assemble: {e}")
```

## Files Modified

### 1. Assembler.py
- Wrapped main assembly logic in `assemble_instructions(data)` function
- Maintained backward compatibility with `__main__` block for legacy usage
- **Net Logic Change**: None - only structural refactoring

### 2. Convertor.py
- No changes to logic or function signature
- Already had `convert_asm_to_json(input_file, output_file)` function exported

### 3. main.py
- Updated to demonstrate the new automated workflow
- Now tries to load `loop_test` assembly program first
- Falls back to hardcoded example if file not found
- Imports `load_instructions` from `instruction_loader`

### 4. tests/test_sim.py
- Added import for `load_instructions`
- Added test: `test_load_instructions_from_file()` - validates basic loading
- Added test: `test_instruction_loader_with_custom_nops()` - validates NOP padding
- All existing tests still pass

## Files Created

### 1. instruction_loader.py (src/)
```
- Main pipeline module
- 75 lines of well-documented code
- Provides single entry point: load_instructions()
- Handles:
  * Path resolution (finds assembly files)
  * Temporary file management
  * Pipeline orchestration
  * Error handling and reporting
  * bit32 conversion
  * NOP padding
```

### 2. loop_test.asm (assembly_programs/)
```
- Sample assembly program in correct format
- Demonstrates the expected format for the assembler
- Test program: loop calculating x3 = x1 + x2 repeatedly
```

## Assembly File Format

Assembly files should follow this format (supported by the existing Convertor/Assembler):

```
addi x1, x0, 5           # Load 5 into x1
addi x2, x0, 3           # Load 3 into x2
loop_label: add x3, x1, x2  # x3 = x1 + x2
addi x1, x1, -1          # Decrement x1
bne x1, x0, loop_label   # Branch if not equal
add x4, x3, x2           # x4 = x3 + x2
```

**Format Rules:**
- Registers: `xi` format (x0, x1, x2, etc.) - NO SPACES
- Labels: End with `:` and can be used in branch instructions
- Comments: Start with `#` and are stripped by Convertor
- Supported Instructions: add, sub, addi, lw, sw, beq, bne, blt, bge, jal

## Benefits

1. **Automation**: Assembly programs are automatically converted to executable instructions
2. **Separation of Concerns**: Assembler and Convertor logic remain unchanged
3. **Ease of Use**: Single function call to load and execute programs
4. **Maintainability**: Pipeline is modular and extensible
5. **Backward Compatibility**: Legacy file-based approach still works
6. **Testing**: Full test coverage for new functionality

## Testing

Run all tests:
```bash
python3 -m pytest tests/test_sim.py -v
```

Run specific new tests:
```bash
python3 -m pytest tests/test_sim.py::test_load_instructions_from_file -v
python3 -m pytest tests/test_sim.py::test_instruction_loader_with_custom_nops -v
```

Run main.py:
```bash
python3 src/main.py
```

## Example Output

```
Successfully converted /path/to/assembly_programs/loop_test.asm to /tmp/temp.json
PC: 0
[CPU execution trace...]
Program executed successfully using automated workflow
```

## Future Enhancements

Possible improvements (without changing core logic):
- Support for assembly files with register aliases (x1 → sp, etc.)
- Format auto-detection for different assembly syntaxes
- Caching of compiled instructions
- Assembly file validation before loading
- Integration with debugger for step-by-step execution
