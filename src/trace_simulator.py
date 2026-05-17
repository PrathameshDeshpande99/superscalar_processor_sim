from virtual_memory import VirtualMemory
from cache import CacheHierarchy
from registers import Registers
from utils import bit32
from memory import Memory


class TraceInstruction:
    def __init__(self, op, addr=None, rd=None, rs1=None, rs2=None):
        self.op = op
        self.addr = addr
        self.rd = rd
        self.rs1 = rs1
        self.rs2 = rs2
        self.remaining_cycles = 0

    def __repr__(self):
        return f"{self.op} {self.addr} {self.rd} {self.rs1} {self.rs2}"


class TraceSimulator:
    def __init__(self, config_params):
        self.params = config_params
        self.vm = VirtualMemory(config_params)

        l1d_config = {
            "size": 4096,
            "block_size": 4,
            "associativity": 1,
            "latency": 1,
            "replacement": "LRU",
        }
        l1i_config = l1d_config.copy()
        l2_config = {
            "size": 0,
            "block_size": 4,
            "associativity": 1,
            "latency": 1,
            "replacement": "LRU",
        }
        main_mem_config = {"latency": 100}

        self.memory = Memory(self.params["physical_size_bytes"])
        self.cache = CacheHierarchy(
            self.memory, self.vm, l1d_config, l1i_config, l2_config, main_mem_config
        )

        self.registers = Registers()
        self.pc = 0
        self.instructions = []
        self.cycle_count = 0
        self.retired_count = 0
        self.stalls = 0

        self.IF_RF = None
        self.RF_EX = None
        self.EX_MEM = None
        self.MEM_WB = None

        self.latencies = {
            "ADD": config_params.get("add_latency", 1),
            "MUL": config_params.get("mul_latency", 3),
            "L": 1,
            "S": 1,
        }

    def load_trace(self, trace_file):
        with open(trace_file, "r") as f:
            for line in f:
                parts = line.strip().split()
                if not parts:
                    continue
                op = parts[0]
                if op == "L":
                    addr = int(parts[1], 16)
                    rd = parts[2]
                    self.instructions.append(TraceInstruction(op, addr=addr, rd=rd))
                elif op == "S":
                    addr = int(parts[1], 16)
                    rs = parts[2]
                    self.instructions.append(
                        TraceInstruction(op, addr=addr, rs1=rs)
                    )  # stored from rs1
                elif op in ["ADD", "MUL"]:
                    rd = parts[1]
                    rs1 = parts[2]
                    rs2 = parts[3]
                    self.instructions.append(
                        TraceInstruction(op, rd=rd, rs1=rs1, rs2=rs2)
                    )

    def run(self):
        while (
            self.pc < len(self.instructions)
            or self.IF_RF
            or self.RF_EX
            or self.EX_MEM
            or self.MEM_WB
        ):
            self.cycle()
        return self.get_stats()

    def cycle(self):
        self.cycle_count += 1

        # WB stage
        if self.MEM_WB and self.MEM_WB.remaining_cycles <= 0:
            self.retired_count += 1
            self.MEM_WB = None

        # MEM stage
        if self.EX_MEM and self.EX_MEM.remaining_cycles <= 0:
            if not self.MEM_WB:
                instr = self.EX_MEM
                if instr.op in ["L", "S"]:
                    if instr.op == "L":
                        _, cache_latency, translation_latency = self.cache.read_word(
                            bit32(instr.addr)
                        )
                    else:
                        cache_latency, translation_latency = self.cache.write_word(
                            bit32(instr.addr), bit32(0)
                        )

                    instr.remaining_cycles = cache_latency + translation_latency - 1
                    self.vm.stats["total_translation_penalty"] += translation_latency
                else:
                    instr.remaining_cycles = 0

                self.MEM_WB = instr
                self.EX_MEM = None

        # EX stage
        if self.RF_EX and self.RF_EX.remaining_cycles <= 0:
            if not self.EX_MEM:
                instr = self.RF_EX
                if instr.op in ["ADD", "MUL"]:
                    instr.remaining_cycles = self.latencies[instr.op] - 1
                else:
                    instr.remaining_cycles = 0
                self.EX_MEM = instr
                self.RF_EX = None

        # RF stage
        if self.IF_RF and self.IF_RF.remaining_cycles <= 0:
            hazard = self.check_hazards(self.IF_RF)
            if not hazard and not self.RF_EX:
                instr = self.IF_RF
                instr.remaining_cycles = 0
                self.RF_EX = instr
                self.IF_RF = None
            else:
                self.stalls += (
                    1  # Increments on BOTH Data Hazards and Structural Backpressure
                )

        # IF stage
        if self.pc < len(self.instructions) and not self.IF_RF:
            instr = self.instructions[self.pc]
            instr.remaining_cycles = 0
            self.IF_RF = instr
            self.pc += 1

        # Progress cycles
        for buffer in [self.IF_RF, self.RF_EX, self.EX_MEM, self.MEM_WB]:
            if buffer:
                buffer.remaining_cycles -= 1

    def check_hazards(self, instr):
        needed_regs = []
        if instr.rs1:
            needed_regs.append(instr.rs1)
        if instr.rs2:
            needed_regs.append(instr.rs2)

        for pending in [self.RF_EX, self.EX_MEM, self.MEM_WB]:
            if pending and pending.rd in needed_regs:
                return True
        return False

    def get_stats(self):
        vm_stats = self.vm.stats
        ipc = self.retired_count / self.cycle_count if self.cycle_count > 0 else 0
        return {
            "total_cycles": self.cycle_count,
            "instructions_retired": self.retired_count,
            "ipc": ipc,
            "stalls": self.stalls,
            "tlb_hits": vm_stats["tlb_hits"],
            "tlb_misses": vm_stats["tlb_misses"],
            "page_walks": vm_stats["page_walks"],
            "page_faults": vm_stats["page_faults"],
            "page_evictions": vm_stats["page_evictions"],
            "dirty_evictions": vm_stats["dirty_evictions"],
            "total_translation_penalty": vm_stats["total_translation_penalty"],
            "l1d_hits": self.cache.l1d.hits,
            "l1d_misses": self.cache.l1d.misses,
        }
