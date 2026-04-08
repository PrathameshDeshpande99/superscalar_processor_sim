"""
Terminal-based UI for the superscalar processor simulator.
Displays register values, pipeline stages, branch detection, stalls, and IPC in real-time.

Usage:
    python -m src.main <assembly_file> [sleep_time_ms]
"""

import sys
import os
import time
import argparse
from pathlib import Path

# Add src directory to path for absolute imports
sys.path.insert(0, os.path.dirname(__file__))

from cpu import CPU
from utils import bit32, bit5
from instruction_loader import load_instructions


class ProcessorSimulatorUI:
    """Terminal-based UI for processor simulation with real-time visualization."""
    
    # Colors and formatting
    HEADER = '\033[95m'
    MAGENTA = '\033[35m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    WHITE = '\033[0m'
    BOLD = '\033[1m'
    
    # ANSI Display Controls
    HIDE_CURSOR = '\033[?25l'
    SHOW_CURSOR = '\033[?25h'
    HOME_CURSOR = '\033[H'
    CLEAR_SCREEN = '\033[2J'
    
    def __init__(self, program_name: str, sleep_ms: float = 500):
        """
        Initialize the UI and the underlying CPU simulator.

        Args:
            program_name (str): Name of the assembly file to load.
            sleep_ms (float): Delay between cycles in milliseconds.
        """
        self.program_name = program_name
        self.sleep_s = sleep_ms / 1000.0 
        self.cpu = CPU()
        self.instructions = load_instructions(program_name)
        
        # UI State Tracking
        self.cycle_count = 0
        self.instruction_count = 0
        self.total_stalls = 0  
        self.branch_count = 0  
        
    def setup_terminal(self):
        """Prepare the terminal for flicker-free rendering."""
        sys.stdout.write(self.CLEAR_SCREEN)
        sys.stdout.write(self.HIDE_CURSOR)
        sys.stdout.flush()

    def cleanup_terminal(self):
        """Restore standard terminal behavior."""
        sys.stdout.write(self.SHOW_CURSOR)
        sys.stdout.flush()
        print("\n")

    def format_buffer_contents(self, buffer) -> str:
        """Safely extract readable data from pipeline buffers for the UI."""
        if not buffer:
            return f"{self.WHITE}Empty{self.WHITE}"
            
        parts = []
        if isinstance(buffer, dict):
            if 'pc' in buffer: parts.append(f"PC:{buffer['pc']}")
            if 'op' in buffer: parts.append(f"OP:{buffer['op']}")
            if 'result' in buffer: parts.append(f"Res:{buffer['result']}")
        
        if not parts:
            s = str(buffer)
            return s[:25] + "..." if len(s) > 25 else s
        return " | ".join(parts)

    def draw_memory_snapshot(self):
        """Display the entire memory snapshot after simulation completion."""
        memory = self.cpu.memory
        output = []
        
        output.append(f"\n{self.BOLD}{self.MAGENTA}┌─ MEMORY SNAPSHOT (ALL VALUES) ────────────────────────────────────────────┐{self.WHITE}")
        
        # Find the last non-zero address to avoid printing empty trailing memory
        last_nonzero = -1
        for i in range(memory.size - 1, -1, -1):
            if memory.data[i].value != 0:
                last_nonzero = i
                break
        
        # If all memory is zero, just indicate that
        if last_nonzero == -1:
            output.append(f"{self.MAGENTA}║{self.WHITE} All memory is zero (empty)")
        else:
            # Display memory in 16-byte rows (4 words per row)
            for addr in range(0, last_nonzero + 1, 16):
                line = f"{self.MAGENTA}║{self.WHITE} "
                line += f"{self.CYAN}0x{addr:04x}:{self.WHITE} "
                
                # Display 16 bytes in groups of 4
                for offset in range(16):
                    if addr + offset <= last_nonzero:
                        byte_val = memory.data[addr + offset].value
                        line += f"{byte_val:02x}"
                    else:
                        line += "  "
                    
                    # Add space between words (every 4 bytes)
                    if (offset + 1) % 4 == 0 and offset < 15:
                        line += " "
                    else:
                        line += ""
                
                line += f" {self.MAGENTA}║{self.WHITE}"
                output.append(line)
        
        output.append(f"{self.BOLD}{self.MAGENTA}└───────────────────────────────────────────────────────────────────────────┘{self.WHITE}")
        
        # Print everything
        sys.stdout.write('\n'.join(output) + '\n')
        sys.stdout.flush()

    def draw_dashboard(self):
        """Draw the entire UI dashboard (overwriting previous output)."""
        # Move cursor to top left instead of clearing screen to prevent flicker
        output = [self.HOME_CURSOR]
        
        # --- HEADER ---
        output.append(f"{self.BOLD}{self.CYAN}═══ SUPERSCALAR PROCESSOR SIMULATOR (LIVE) ═══{self.WHITE}")
        output.append(f"Program: {self.BOLD}{self.program_name}{self.WHITE} | Target Delay: {self.sleep_s * 1000:.0f}ms")
        output.append("")
        
        # --- REGISTERS ---
        output.append(f"{self.BOLD}{self.BLUE}┌─ REGISTER FILE ────────────────────────────────────────────────────────┐{self.WHITE}")
        for row in range(8):
            line = f"{self.BLUE}║{self.WHITE} "
            for col in range(4):
                reg_num = row * 4 + col
                if reg_num < 32:
                    value = self.cpu.registers.read(bit5(reg_num)).value
                    reg_str = f"{self.YELLOW}x{reg_num:<2}{self.WHITE}" if reg_num == 0 else f"x{reg_num:<2}"
                    line += f"{reg_str}: {value:<11} "
            line += f"{self.BLUE}║{self.WHITE}"
            output.append(line)
        output.append(f"{self.BOLD}{self.BLUE}└────────────────────────────────────────────────────────────────────────┘{self.WHITE}")
        
        # --- PIPELINE ---
        p = self.cpu.pipeline
        output.append(f"{self.BOLD}{self.YELLOW}┌─ PIPELINE BUFFERS ─────────────────────────────────────────────────────┐{self.WHITE}")
        output.append(f"{self.YELLOW}║{self.WHITE} [IF Stage ] Fetching instruction at PC: {self.cpu.pc:<30} {self.YELLOW}║{self.WHITE}")
        output.append(f"{self.YELLOW}║{self.WHITE} [Decode/RF] {self.format_buffer_contents(p.IF_RF_Buffer):<55} {self.YELLOW}║{self.WHITE}")
        output.append(f"{self.YELLOW}║{self.WHITE} [Execute  ] {self.format_buffer_contents(p.RF_EX_Buffer):<55} {self.YELLOW}║{self.WHITE}")
        output.append(f"{self.YELLOW}║{self.WHITE} [Memory   ] {self.format_buffer_contents(p.EX_MEM_Buffer):<55} {self.YELLOW}║{self.WHITE}")
        output.append(f"{self.YELLOW}║{self.WHITE} [Writeback] {self.format_buffer_contents(p.MEM_WB_Buffer):<55} {self.YELLOW}║{self.WHITE}")
        output.append(f"{self.BOLD}{self.YELLOW}└────────────────────────────────────────────────────────────────────────┘{self.WHITE}")
        
        # --- STATISTICS ---
        ipc = self.instruction_count / max(self.cycle_count, 1)
        output.append(f"{self.BOLD}{self.GREEN}┌─ EXECUTION STATISTICS ─────────────────────────────────────────────────┐{self.WHITE}")
        output.append(f"{self.GREEN}║{self.WHITE} Clock Cycles: {self.cycle_count:<12} Instructions Exec: {self.instruction_count:<13} {self.GREEN}║{self.WHITE}")
        output.append(f"{self.GREEN}║{self.WHITE} Current PC:   {self.cpu.pc:<12} Current IPC:       {ipc:<13.2f} {self.GREEN}║{self.WHITE}")
        output.append(f"{self.BOLD}{self.GREEN}└────────────────────────────────────────────────────────────────────────┘{self.WHITE}")
        
        # Print everything in a single fast write
        sys.stdout.write('\n'.join(output) + '\n')
        sys.stdout.flush()

    def run_simulation(self):
        """Run the simulation loop with live UI updates."""
        try:
            self.setup_terminal()
            
            # Initial drawing before starting
            self.draw_dashboard()
            time.sleep(1)
            
            # Iterate through the execution cycle by cycle
            for exec_count, cycles in self.cpu.execute_program_live(self.instructions):
                self.instruction_count = exec_count
                self.cycle_count = cycles
                
                self.draw_dashboard()
                time.sleep(self.sleep_s)
                
            # Final completion state
            self.draw_dashboard()
            
            # Display memory snapshot
            self.draw_memory_snapshot()
            
            print(f"{self.BOLD}{self.GREEN}✓ Simulation Completed Successfully!{self.WHITE}")
            
        except KeyboardInterrupt:
            print(f"\n\n{self.BOLD}{self.RED}⚠ Simulation interrupted by user.{self.WHITE}")
        except Exception as e:
            print(f"\n\n{self.BOLD}{self.RED}✗ Simulation Error: {str(e)}{self.WHITE}")
            import traceback
            traceback.print_exc()
        finally:
            self.cleanup_terminal()


def main():
    parser = argparse.ArgumentParser(
        description='Superscalar Processor Simulator with Real-Time Terminal UI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m src.main test_loop 500          # Run test_loop with 500ms per cycle
  python -m src.main sample                 # Run with default sleep time
  python -m src.main test_add 1000          # Run test_add with 1 second per cycle
        """
    )
    
    parser.add_argument('program', help='Assembly program name (without .txt extension)')
    parser.add_argument('sleep_time', nargs='?', type=float, default=500, 
                        help='Time to sleep between cycles in milliseconds (default: 500)')
    
    args = parser.parse_args()
    
    if args.sleep_time < 0:
        print(f"Error: Sleep time must be non-negative")
        sys.exit(1)
    
    try:
        simulator = ProcessorSimulatorUI(args.program, args.sleep_time)
        simulator.run_simulation()
        
    except FileNotFoundError as e:
        print(f"Error: {str(e)}")
        print(f"\nAvailable programs in assembly_programs/:")
        asm_dir = Path(__file__).parent.parent / "assembly_programs"
        if asm_dir.exists():
            for f in sorted(asm_dir.glob("*.txt")):
                print(f"  - {f.stem}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()