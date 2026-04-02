# Terminal-Based Processor Simulator UI Guide

## Overview

The new main.py provides a rich terminal-based user interface for the superscalar processor simulator. It displays:

- **Register values** - All 32 registers with their current values
- **Pipeline stages** - Visual representation of the 5-stage pipeline (IF, Decode, Exec, Mem, WB)
- **Statistics** - Cycle count, instructions executed, stalls, branches, and IPC
- **Memory & Branch Info** - Current PC and loaded instructions count

## Usage

### Basic Usage
```bash
# Run with default 500ms delay between cycles
python -m src.main test_loop

# Run with custom cycle delay (1 second)
python -m src.main test_loop 1000

# Run with faster cycles (100ms)
python -m src.main test_add 100
```

### Available Programs

All assembly programs in the `assembly_programs/` folder can be run:

```bash
python -m src.main test_add       # Simple addition test
python -m src.main test_sub       # Subtraction test
python -m src.main test_addi      # Add immediate test
python -m src.main test_load      # Load word test
python -m src.main test_store     # Store word test
python -m src.main test_raw       # Read-After-Write hazard
python -m src.main test_loop      # Loop with branches
python -m src.main sample         # Sample program
```

## Display Panels

### Register File Panel
Shows all 32 registers (x0-x31) with their current values:
- x0 is highlighted in yellow (always 0)
- Values update after each cycle
- Organized in 4 columns for readability

### Statistics Panel
Real-time metrics:
- **Cycle Count**: Total number of clock cycles executed
- **Instructions Executed**: Count of completed instructions
- **Total Stalls**: Number of pipeline stalls due to hazards
- **Branch Count**: Number of branch instructions executed
- **IPC**: Instructions Per Cycle (total instructions / total cycles)

### Pipeline Stages Panel
Visual representation showing:
- IF (Instruction Fetch) - Cyan
- Decode - Blue
- Exec (Execute) - Green
- Mem (Memory) - Yellow
- WB (Writeback) - Red

### Memory & Branch Info Panel
- Current program counter (PC)
- Total instructions loaded

## Examples

### Example 1: Watch a Simple Addition
```bash
python -m src.main test_add 1000
```

This will:
1. Load the test_add.txt program
2. Execute it with 1 second between cycles
3. Show final register values and IPC

### Example 2: Fast Loop Execution
```bash
python -m src.main test_loop 100
```

1. Load the loop program (branches and multiple iterations)
2. Execute with 100ms per cycle (fast)
3. Watch branch behavior and pipeline filling/emptying

### Example 3: Memory Operations
```bash
python -m src.main test_load 500
python -m src.main test_store 500
```

Watch memory read and write operations execute through the pipeline.

## Performance Metrics

### IPC (Instructions Per Cycle)
- Ideal: 1.0 (one instruction completes per cycle with perfect pipelining)
- Real: < 1.0 (due to pipeline fills and stalls)
- The UI displays final IPC after simulation completes

### Stalls
Detected when:
- Data hazards occur (Read-After-Write)
- Control hazards occur (branch misprediction)
- Memory operations take multiple cycles

### Cycle Delay Parameter
- **Very fast** (< 100ms): Good for high-level observation
- **Fast** (100-500ms): Good for seeing pipeline behavior
- **Medium** (500-1000ms): Good for detailed instruction tracking
- **Slow** (> 1000ms): Good for step-by-step analysis

## Keyboard Shortcuts

- **Ctrl+C** - Stop simulation early
- **Q** - Quit (when prompted, if supported)

## Understanding the Display

### Color Legend
```
Cyan  ■ = IF Stage (Instruction Fetch)
Blue  ■ = Decode Stage
Green ■ = Execute Stage
Yellow ■ = Memory Stage
Red   ■ = Writeback Stage
```

### Register Highlighting
- **Yellow X0** = x0 (always zero, hardwired)
- **Normal** = Other registers

### Pipeline Visualization
Each stage shows a bar representing capacity and current instruction occupancy. Full bars indicate all pipeline slots are in use.

## Testing Programs

### test_add.txt
**Purpose**: Test basic addition  
**Instructions**: 1 (plus 4 NOPs)
**Assembly**: `add x1, x2, x3`

### test_sub.txt
**Purpose**: Test subtraction  
**Instructions**: 1 (plus 4 NOPs)
**Assembly**: `sub x1, x2, x3`

### test_addi.txt
**Purpose**: Test add-immediate  
**Instructions**: 1 (plus 4 NOPs)
**Assembly**: `addi x1, x2, 5`

### test_load.txt
**Purpose**: Test load word  
**Instructions**: 1 (plus 4 NOPs)
**Assembly**: `lw x3, 0(x2)`

### test_store.txt
**Purpose**: Test store word  
**Instructions**: 1 (plus 4 NOPs)
**Assembly**: `sw x4, 0(x2)`

### test_raw.txt
**Purpose**: Test Read-After-Write hazard  
**Instructions**: 2 (plus 4 NOPs)
**Assembly**:
```asm
addi x1, x0, 5
add x2, x1, x3
```

### test_loop.txt
**Purpose**: Test loop with branches  
**Instructions**: 6 (plus 4 NOPs)
**Assembly**:
```asm
addi x1, x0, 5
addi x2, x0, 3
loop: add x3, x1, x2
addi x1, x1, -1
bne x1, x0, loop
add x4, x3, x2
```

## Troubleshooting

### Program Not Found
```
Error: Assembly program not found
```
- Check the program name (case-sensitive)
- Ensure the .txt file exists in `assembly_programs/`
- Run `python -m src.main --help` to see available programs

### Recursion Error
If you see a recursion error, it's likely a bug in registers.py or CPU logic. 
- Try simpler programs first (test_add)
- Check that assembly files are valid

### Slow Terminal Rendering
If the UI is slow:
- Increase cycle delay (larger number)
- Or decrease it for faster cycling through cycles

## Tips

1. **For understanding pipeline**: Use test_loop (500ms) to see how branches affect the pipeline
2. **For hazard analysis**: Use test_raw (1000ms) to see data dependency stalls
3. **For overall performance**: Run any program and check the final IPC value

## Creating Custom Programs

1. Create a new `.txt` file in `assembly_programs/`
2. Write RISC-V assembly code
3. Run with: `python -m src.main <filename_without_txt> <delay_ms>`

Example:
```bash
# Create assembly_programs/my_prog.txt
# Then run:
python -m src.main my_prog 500
```

## Future Enhancements

Planned features:
- [ ] Cycle-by-cycle step through (press SPACE to advance)
- [ ] Detailed pipeline state visualization
- [ ] Memory access tracking
- [ ] Hot register highlighting
- [ ] Branch prediction visualization
- [ ] Stall reason reporting

---

**For more details on the assembly pipeline, see ASSEMBLY_PIPELINE_GUIDE.md**
