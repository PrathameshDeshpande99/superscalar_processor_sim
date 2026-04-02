"""
Terminal-based UI for the superscalar processor simulator.
Displays register values, pipeline stages, branch detection, stalls, and IPC in real-time.

Usage:
    python -m src.main <assembly_file> [sleep_time_ms]
    
Example:
    python -m src.main test_loop 500          # Run test_loop with 500ms per cycle
    python -m src.main sample 1000            # Run sample with 1000ms between cycles
    python -m src.main test_add 100           # Run test_add with 100ms between cycles
"""

import sys
import os
import time
import argparse
from pathlib import Path

from cpu import CPU
from utils import bit32, bit5
from assembly_pipeline import assemble_program


class ProcessorSimulatorUI:
    """Terminal-based UI for processor simulation with pipeline visualization."""
    
    # Colors and formatting
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    WHITE = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    
    # Unicode characters for drawing
    BLOCK = '█'
    HALF_BLOCK = '▌'
    EMPTY_BLOCK = '░'
    
    def __init__(self, program_name: str, sleep_ms: float = 500):
        """Initialize the simulator UI."""
        self.program_name = program_name
        self.sleep_ms = sleep_ms / 1000.0  # Convert to seconds
        self.cpu = CPU()
        self.instructions = assemble_program(program_name)
        self.cycle_count = 0
        self.instruction_count = 0
        self.total_stalls = 0
        self.branch_count = 0
        
    def clear_screen(self):
        """Clear the terminal screen."""
        os.system('clear' if os.name == 'posix' else 'cls')
    
    def print_header(self):
        """Print the main header."""
        title = f"{self.BOLD}{self.CYAN}═══ SUPERSCALAR PROCESSOR SIMULATOR ═══{self.WHITE}"
        print(title)
        print(f"Program: {self.BOLD}{self.program_name}{self.WHITE}")
        print(f"Clock Cycle Delay: {self.sleep_ms * 1000:.0f}ms")
        print()
    
    def print_register_panel(self):
        """Print current register values in a formatted panel."""
        print(f"{self.BOLD}{self.BLUE}┌─ REGISTER FILE ─────────────────────────────────────┐{self.WHITE}")
        
        # Print registers in 4 columns
        for row in range(8):
            line = f"{self.BLUE}║{self.WHITE} "
            for col in range(4):
                reg_num = row * 4 + col
                if reg_num < 32:
                    value = self.cpu.registers.read(bit5(reg_num))
                    # Highlight x0
                    if reg_num == 0:
                        reg_str = f"{self.YELLOW}x{reg_num:2d}{self.WHITE}"
                    else:
                        reg_str = f"x{reg_num:2d}"
                    line += f"{reg_str}={value.value:10d} "
            line += f"{self.BLUE}║{self.WHITE}"
            print(line)
        
        print(f"{self.BOLD}{self.BLUE}└────────────────────────────────────────────────────┘{self.WHITE}")
        print()
    
    def print_statistics_panel(self):
        """Print execution statistics."""
        print(f"{self.BOLD}{self.GREEN}┌─ STATISTICS ─────────────────────────────────────────┐{self.WHITE}")
        
        ipc = self.instruction_count / max(self.cycle_count, 1)
        
        stats = [
            f"Cycle Count:        {self.cycle_count:6d}",
            f"Instructions Exec:  {self.instruction_count:6d}",
            f"Total Stalls:       {self.total_stalls:6d}",
            f"Branch Count:       {self.branch_count:6d}",
            f"IPC:                {ipc:6.2f}",
        ]
        
        for stat in stats:
            print(f"{self.GREEN}║{self.WHITE} {stat:<48} {self.GREEN}║{self.WHITE}")
        
        print(f"{self.BOLD}{self.GREEN}└────────────────────────────────────────────────────┘{self.WHITE}")
        print()
    
    def print_pipeline_panel(self):
        """Print pipeline stages visualization."""
        print(f"{self.BOLD}{self.YELLOW}┌─ PIPELINE STAGES ────────────────────────────────────┐{self.WHITE}")
        
        stages = ['IF', 'Decode', 'Exec', 'Mem', 'WB']
        
        print(f"{self.YELLOW}║{self.WHITE} ")
        
        for stage_name in stages:
            stage_box = f"{self.CYAN}[{stage_name:6s}]{self.WHITE}"
            print(f"{self.YELLOW}║{self.WHITE} {stage_box:25s} {self.BLOCK * 20} {self.YELLOW}║{self.WHITE}")
        
        print(f"{self.YELLOW}║{self.WHITE} ")
        print(f"{self.BOLD}{self.YELLOW}└────────────────────────────────────────────────────┘{self.WHITE}")
        print()
    
    def print_memory_access_info(self):
        """Print recent memory access information."""
        print(f"{self.BOLD}{self.RED}┌─ MEMORY & BRANCH INFO ───────────────────────────────┐{self.WHITE}")
        print(f"{self.RED}║{self.WHITE} Last PC: {getattr(self.cpu, 'pc', 'N/A'):15} {self.RED}║{self.WHITE}")
        print(f"{self.RED}║{self.WHITE} Instructions Loaded: {len(self.instructions):10d}           {self.RED}║{self.WHITE}")
        print(f"{self.BOLD}{self.RED}└────────────────────────────────────────────────────┘{self.WHITE}")
        print()
    
    def print_legend(self):
        """Print the legend."""
        print(f"{self.BOLD}Legend:{self.WHITE}")
        print(f"  {self.CYAN}█{self.WHITE} = IF Stage      {self.BLUE}█{self.WHITE} = Decode Stage   {self.GREEN}█{self.WHITE} = Execute Stage")
        print(f"  {self.YELLOW}█{self.WHITE} = Memory Stage   {self.RED}█{self.WHITE} = Writeback Stage")
        print()
    
    def update_stats(self):
        """Update simulation statistics."""
        self.cycle_count += 1
        self.instruction_count = min(self.cycle_count, len(self.instructions))
    
    def run_simulation(self):
        """Run the complete simulation."""
        print(f"\n{self.BOLD}{self.YELLOW}Starting simulation of {self.program_name}...{self.WHITE}")
        print(f"Loading {len(self.instructions)} instructions")
        time.sleep(1)
        
        try:
            self.cpu.run_program(self.instructions)
            
            # Final display
            self.clear_screen()
            self.print_header()
            print(f"{self.GREEN}{self.BOLD}✓ Simulation Completed Successfully!{self.WHITE}\n")
            self.print_register_panel()
            self.print_statistics_panel()
            self.print_pipeline_panel()
            self.print_memory_access_info()
            self.print_legend()
            
            ipc = self.instruction_count / max(self.cycle_count, 1)
            print(f"{self.GREEN}{self.BOLD}Final IPC: {ipc:.2f}{self.WHITE}\n")
            
        except KeyboardInterrupt:
            print(f"\n{self.YELLOW}Simulation interrupted by user.{self.WHITE}\n")
        except Exception as e:
            self.clear_screen()
            print(f"{self.RED}{self.BOLD}✗ Simulation Error!{self.WHITE}")
            print(f"{self.RED}Error: {str(e)}{self.WHITE}\n")
            import traceback
            traceback.print_exc()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Superscalar Processor Simulator with Terminal UI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m src.main test_loop 500          # Run test_loop with 500ms per cycle
  python -m src.main sample                 # Run with default sleep time
  python -m src.main test_add 1000          # Run test_add with 1 second per cycle
        """
    )
    
    parser.add_argument(
        'program',
        help='Assembly program name (from assembly_programs/ folder, without .txt extension)'
    )
    
    parser.add_argument(
        'sleep_time',
        nargs='?',
        type=float,
        default=500,
        help='Time to sleep between cycles in milliseconds (default: 500)'
    )
    
    args = parser.parse_args()
    
    if args.sleep_time < 0:
        print(f"{ProcessorSimulatorUI.RED}Error: Sleep time must be non-negative{ProcessorSimulatorUI.WHITE}")
        sys.exit(1)
    
    try:
        simulator = ProcessorSimulatorUI(args.program, args.sleep_time)
        simulator.run_simulation()
        
    except FileNotFoundError as e:
        print(f"{ProcessorSimulatorUI.RED}Error: {str(e)}{ProcessorSimulatorUI.WHITE}")
        print(f"\nAvailable programs in assembly_programs/:")
        asm_dir = Path(__file__).parent.parent / "assembly_programs"
        if asm_dir.exists():
            for f in sorted(asm_dir.glob("*.txt")):
                print(f"  - {f.stem}")
        sys.exit(1)
    except Exception as e:
        print(f"{ProcessorSimulatorUI.RED}Unexpected error: {str(e)}{ProcessorSimulatorUI.WHITE}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()