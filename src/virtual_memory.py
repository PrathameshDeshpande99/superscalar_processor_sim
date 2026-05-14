import math


class TLBEntry:
    def __init__(self, vpn, ppn):
        self.vpn = vpn
        self.ppn = ppn
        self.valid = True
        self.last_used = 0


class TLB:
    def __init__(self, num_entries, replacement_policy="lru"):
        self.entries = []
        self.num_entries = num_entries
        self.replacement_policy = replacement_policy
        self.counter = 0
        self.hits = 0
        self.misses = 0

    def lookup(self, vpn):
        self.counter += 1
        for entry in self.entries:
            if entry.valid and entry.vpn == vpn:
                entry.last_used = self.counter
                self.hits += 1
                return entry.ppn
        self.misses += 1
        return None

    def insert(self, vpn, ppn):
        self.counter += 1

        # 1. Update if it already exists
        for entry in self.entries:
            if entry.valid and entry.vpn == vpn:
                entry.ppn = ppn
                entry.last_used = self.counter
                return

        # 2. Try to reuse an invalidated entry (prevents dead entries)
        for entry in self.entries:
            if not entry.valid:
                entry.vpn = vpn
                entry.ppn = ppn
                entry.valid = True
                entry.last_used = self.counter
                return

        # 3. Insert new or Replace
        if len(self.entries) < self.num_entries:
            self.entries.append(TLBEntry(vpn, ppn))
            self.entries[-1].last_used = self.counter
        else:
            if self.replacement_policy == "lru":
                victim = min(self.entries, key=lambda e: e.last_used)
            else:  # FIFO
                victim = self.entries[0]
                self.entries.pop(0)
                self.entries.append(TLBEntry(vpn, ppn))
                return

            victim.vpn = vpn
            victim.ppn = ppn
            victim.last_used = self.counter


class PageTableEntry:
    def __init__(self, ppn=None):
        self.ppn = ppn
        self.valid = False
        self.dirty = False


class VirtualMemory:
    def __init__(self, params):
        self.page_size = params.get("page_size_bytes", 4096)
        self.virtual_mem_size = params.get("virtual_size_bytes", 1 << 32)
        self.physical_mem_size = params.get(
            "physical_size_bytes", 262144
        )  # 64 frames * 4KB

        self.num_vpn = self.virtual_mem_size // self.page_size
        self.num_frames = self.physical_mem_size // self.page_size

        self.page_table = {}
        self.tlb = TLB(
            params.get("dtlb_entries", 16), params.get("replacement_policy", "lru")
        )

        self.free_frames = list(range(self.num_frames))
        self.allocated_frames = []  # List of (vpn, ppn)

        self.tlb_hit_latency = params.get("tlb_hit_latency", 1)
        self.page_walk_latency = params.get("page_walk_latency", 10)
        self.page_fault_latency = params.get("page_fault_latency", 50)
        self.replacement_policy = params.get("replacement_policy", "lru")

        self.stats = {
            "tlb_hits": 0,
            "tlb_misses": 0,
            "page_walks": 0,
            "page_faults": 0,
            "page_evictions": 0,
            "dirty_evictions": 0,
            "total_translation_penalty": 0,
        }

        self.vpn_bits = int(math.log2(self.page_size))

    def translate(self, virtual_address, is_write=False):
        vpn = virtual_address >> self.vpn_bits
        offset = virtual_address & (self.page_size - 1)
        penalty = 0

        # 1. TLB Lookup
        ppn = self.tlb.lookup(vpn)
        if ppn is not None:
            self.stats["tlb_hits"] += 1
            penalty += self.tlb_hit_latency
            if is_write:
                self.page_table[vpn].dirty = True

            # For LRU, update frame usage history
            if self.replacement_policy == "lru":
                for i, (v, p) in enumerate(self.allocated_frames):
                    if v == vpn:
                        self.allocated_frames.pop(i)
                        self.allocated_frames.append((v, p))
                        break

            return (ppn << self.vpn_bits) | offset, penalty

        # 2. TLB Miss -> Page Walk
        self.stats["tlb_misses"] += 1
        self.stats["page_walks"] += 1
        penalty += self.page_walk_latency

        if vpn in self.page_table and self.page_table[vpn].valid:
            ppn = self.page_table[vpn].ppn
            self.tlb.insert(vpn, ppn)
            if is_write:
                self.page_table[vpn].dirty = True
            if self.replacement_policy == "lru":
                for i, (v, p) in enumerate(self.allocated_frames):
                    if v == vpn:
                        self.allocated_frames.pop(i)
                        self.allocated_frames.append((v, p))
                        break
            return (ppn << self.vpn_bits) | offset, penalty

        # 3. Page Fault
        self.stats["page_faults"] += 1
        penalty += self.page_fault_latency

        ppn = self._handle_page_fault(vpn)
        self.tlb.insert(vpn, ppn)
        if is_write:
            self.page_table[vpn].dirty = True

        return (ppn << self.vpn_bits) | offset, penalty

    def _handle_page_fault(self, vpn):
        if self.free_frames:
            ppn = self.free_frames.pop(0)
        else:
            self.stats["page_evictions"] += 1
            if self.replacement_policy == "lru" or self.replacement_policy == "fifo":
                victim_vpn, ppn = self.allocated_frames.pop(0)

            # Check dirty bit
            if self.page_table[victim_vpn].dirty:
                self.stats["dirty_evictions"] += 1

            self.page_table[victim_vpn].valid = False
            self.page_table[victim_vpn].ppn = None

            # Invalidate TLB entry
            for entry in self.tlb.entries:
                if entry.vpn == victim_vpn:
                    entry.valid = False

        self.page_table[vpn] = PageTableEntry(ppn)
        self.page_table[vpn].valid = True
        self.allocated_frames.append((vpn, ppn))
        return ppn
