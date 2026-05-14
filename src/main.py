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
# from instruction_loader import load_instructions


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
            if 'remaining_cycles' in buffer: parts.append(f"Remaining Cycles: {buffer['remaining_cycles']}")
            if 'instruction' in buffer: parts.append(f"Instr: {buffer['instruction']}")
            # if 'writeback_value' in buffer: parts.append(f"Writeback_value: {buffer['writeback_value']}")
            # if 'rd' in buffer: parts.append(f"rd: {buffer['rd']}")
            # if 'alu_result' in buffer: parts.append(f"alu_result: {buffer['alu_result']}")
            # if 'A' in buffer: parts.append(f"A: {buffer['A']}")
            # if 'B' in buffer: parts.append(f"B: {buffer['B']}")
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
                    
                # Print address in decimal
                line += f"{self.CYAN}{addr:<6}:{self.WHITE} "
                    
                # Process 4 words (each word = 4 bytes)
                for word_offset in range(0, 16, 4):
                    base = addr + word_offset
                        
                    if base + 3 <= last_nonzero:
                        # Combine 4 bytes into a 32-bit word (little endian)
                        b0 = memory.data[base].value
                        b1 = memory.data[base + 1].value
                        b2 = memory.data[base + 2].value
                        b3 = memory.data[base + 3].value
                            
                        word = (b0 << 24) | (b1 << 16) | (b2 << 8) | b3
                            
                        # Convert to signed 32-bit integer
                        if word & (1 << 31):
                            word -= (1 << 32)
                            
                        line += f"{word:<10} "
                    else:
                        line += " " * 10
                    
                line += f"{self.MAGENTA}║{self.WHITE}"
                output.append(line)
        
        output.append(f"{self.BOLD}{self.MAGENTA}└───────────────────────────────────────────────────────────────────────────┘{self.WHITE}")
        
        # Print everything
        sys.stdout.write('\n'.join(output) + '\n')
        sys.stdout.flush()

    def get_memory_lines(self, start=1024, num_words=20):
        """Return formatted memory lines (compact view)."""
        memory = self.cpu.memory
        lines = []

        for i in range(num_words):
            addr = start + i * 4

            if addr + 3 >= memory.size:
                break

            # Big endian word reconstruction
            b0 = memory.data[addr].value
            b1 = memory.data[addr + 1].value
            b2 = memory.data[addr + 2].value
            b3 = memory.data[addr + 3].value

            word = (b0 << 24) | (b1 << 16) | (b2 << 8) | b3

            # signed conversion
            if word & (1 << 31):
                word -= (1 << 32)

            lines.append(f"{addr:<6}: {word:<10}")

        return lines

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
        output.append(f"{self.YELLOW}║{self.WHITE} [IF Stage ] Fetching instruction at PC: {self.cpu.pc:<30} {self.format_buffer_contents(p.IF_RF_Buffer):<55} {self.YELLOW}║{self.WHITE}")
        output.append(f"{self.YELLOW}║{self.WHITE} [Decode/RF] {self.format_buffer_contents(p.IF_RF_Buffer):<55} {self.YELLOW}║{self.WHITE}")
        output.append(f"{self.YELLOW}║{self.WHITE} [Execute  ] {self.format_buffer_contents(p.RF_EX_Buffer):<55} {self.YELLOW}║{self.WHITE}")
        output.append(f"{self.YELLOW}║{self.WHITE} [Memory   ] {self.format_buffer_contents(p.EX_MEM_Buffer):<55} {self.YELLOW}║{self.WHITE}")
        output.append(f"{self.YELLOW}║{self.WHITE} [Writeback] {self.format_buffer_contents(p.MEM_WB_Buffer):<55} {self.YELLOW}║{self.WHITE}")
        output.append(f"{self.BOLD}{self.YELLOW}└────────────────────────────────────────────────────────────────────────┘{self.WHITE}")
        
        # --- STATISTICS ---
        ipc = self.instruction_count / max(self.cycle_count, 1)
        
        l1d_hits = self.cpu.cache_hierarchy.l1d.hits
        l1d_misses = self.cpu.cache_hierarchy.l1d.misses
        l1d_total = l1d_hits + l1d_misses
        l1d_miss_rate = (l1d_misses / l1d_total * 100) if l1d_total > 0 else 0.0

        l1i_hits = self.cpu.cache_hierarchy.l1i.hits
        l1i_misses = self.cpu.cache_hierarchy.l1i.misses
        l1i_total = l1i_hits + l1i_misses
        l1i_miss_rate = (l1i_misses / l1i_total * 100) if l1i_total > 0 else 0.0
        
        l2_hits = self.cpu.cache_hierarchy.l2.hits
        l2_misses = self.cpu.cache_hierarchy.l2.misses
        l2_total = l2_hits + l2_misses
        l2_miss_rate = (l2_misses / l2_total * 100) if l2_total > 0 else 0.0
        
        output.append(f"{self.BOLD}{self.GREEN}┌─ EXECUTION STATISTICS ─────────────────────────────────────────────────┐{self.WHITE}")
        output.append(f"{self.GREEN}║{self.WHITE} Clock Cycles: {self.cycle_count:<12} Instructions Exec: {self.instruction_count:<13} {self.GREEN}║{self.WHITE}")
        output.append(f"{self.GREEN}║{self.WHITE} Current PC:   {self.cpu.pc:<12} Current IPC:       {ipc:<13.2f} {self.GREEN}║{self.WHITE}")
        output.append(f"{self.GREEN}║{self.WHITE} L1D Miss Rate:{l1d_miss_rate:>6.1f}%      L1I Miss Rate:     {l1i_miss_rate:>6.1f}% {self.GREEN}║{self.WHITE}")
        output.append(f"{self.GREEN}║{self.WHITE} L2 Miss Rate: {l2_miss_rate:>6.1f}%                                          {self.GREEN}║{self.WHITE}")
        output.append(f"{self.BOLD}{self.GREEN}└────────────────────────────────────────────────────────────────────────┘{self.WHITE}")
        
        # # --- MEMORY (LIVE SNAPSHOT) ---
        # output.append(f"{self.BOLD}{self.MAGENTA}┌─ MEMORY (LIVE) ───────────────────────────────────────────────┐{self.WHITE}")

        # mem_lines = self.get_memory_lines(start=1024, num_words=8)

        # for line_mem in mem_lines:
        #     output.append(f"{self.MAGENTA}║{self.WHITE} {line_mem:<60} {self.MAGENTA}║{self.WHITE}")

        # output.append(f"{self.BOLD}{self.MAGENTA}└──────────────────────────────────────────────────────────────┘{self.WHITE}")

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


from src.trace_simulator import TraceSimulator
from src.config_parser import parse_config

def run_trace_simulation(trace_file, config_file):
    params = parse_config(config_file)
    simulator = TraceSimulator(params)
    simulator.load_trace(trace_file)
    stats = simulator.run()
    
    print("\n" + "="*40)
    print("TRACE SIMULATION RESULTS")
    print("="*40)
    print(f"Total Cycles: {stats['total_cycles']}")
    print(f"Instructions Retired: {stats['instructions_retired']}")
    print(f"IPC: {stats['ipc']:.4f}")
    print(f"Stalls: {stats['stalls']}")
    print("-" * 20)
    print(f"TLB Hits: {stats['tlb_hits']}")
    print(f"TLB Misses: {stats['tlb_misses']}")
    print(f"Page Walks: {stats['page_walks']}")
    print(f"Page Faults: {stats['page_faults']}")
    print(f"Page Evictions: {stats['page_evictions']}")
    print(f"Dirty Evictions/Writebacks: {stats['dirty_evictions']}")
    print(f"Total Translation Penalty Cycles: {stats['total_translation_penalty']}")
    print("-" * 20)
    print(f"L1D Hits: {stats['l1d_hits']}")
    print(f"L1D Misses: {stats['l1d_misses']}")
    print("="*40 + "\n")

def main():
    parser = argparse.ArgumentParser(
        description='Superscalar Processor Simulator with Real-Time Terminal UI',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('program', nargs='?', help='Assembly program name (without .txt extension)')
    parser.add_argument('sleep_time', nargs='?', type=float, default=500, 
                        help='Time to sleep between cycles in milliseconds (default: 500)')
    parser.add_argument('--trace', type=str, help='Trace file to replay')
    parser.add_argument('--config', type=str, help='Configuration file for simulation')
    
    args = parser.parse_args()
    
    if args.trace:
        if not args.config:
            print("Error: --config is required when using --trace")
            sys.exit(1)
        run_trace_simulation(args.trace, args.config)
        return

    if not args.program:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()