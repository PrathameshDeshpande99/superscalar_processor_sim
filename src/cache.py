import random
import math
from utils import bit8, bit32

class CacheLine:
    def __init__(self, block_size):
        self.valid = False
        self.dirty = False
        self.tag = -1
        self.data = [bit8(0) for _ in range(block_size)]
        self.last_used = 0  # For LRU policy

class CacheSet:
    def __init__(self, associativity, block_size, replacement_policy):
        self.lines = [CacheLine(block_size) for _ in range(associativity)]
        self.replacement_policy = replacement_policy
        self.counter = 0

    def find_line(self, tag):
        self.counter += 1
        for line in self.lines:
            if line.valid and line.tag == tag:
                line.last_used = self.counter
                return line
        return None

    def evict_and_insert(self, tag, data_block):
        self.counter += 1
        # 1. Look for an invalid line first (no eviction required)
        for line in self.lines:
            if not line.valid:
                line.valid = True
                line.dirty = False
                line.tag = tag
                # Assuming data_block is a list of bit8 objects
                line.data = list(data_block)
                line.last_used = self.counter
                return None

        # 2. Need to evict
        evicted_line = None
        if self.replacement_policy == "LRU":
            evicted_line = min(self.lines, key=lambda l: l.last_used)
        else: # Random
            evicted_line = random.choice(self.lines)

        # Store evicted info if dirty
        evicted_info = None
        if evicted_line.dirty:
            evicted_info = (evicted_line.tag, list(evicted_line.data))

        # Replace with new data
        evicted_line.tag = tag
        evicted_line.data = list(data_block)
        evicted_line.dirty = False
        evicted_line.last_used = self.counter

        return evicted_info

class Cache:
    def __init__(self, name, config, lower_level=None, memory=None, main_mem_latency=100):
        self.name = name
        self.size = config["size"]
        self.block_size = config["block_size"]
        self.associativity = config["associativity"]
        self.latency = config["latency"]
        self.replacement = config["replacement"]
        
        self.num_sets = self.size // (self.block_size * self.associativity)
        self.sets = [CacheSet(self.associativity, self.block_size, self.replacement) for _ in range(self.num_sets)]
        
        self.lower_level = lower_level
        self.memory = memory
        self.main_mem_latency = main_mem_latency
        
        self.offset_bits = int(math.log2(self.block_size))
        self.index_bits = int(math.log2(self.num_sets))
        
        self.hits = 0
        self.misses = 0

    def get_tag_index_offset(self, address_val):
        offset = address_val & ((1 << self.offset_bits) - 1)
        index = (address_val >> self.offset_bits) & ((1 << self.index_bits) - 1)
        tag = (address_val >> (self.offset_bits + self.index_bits))
        return tag, index, offset

    def get_base_address(self, tag, index):
        return (tag << (self.offset_bits + self.index_bits)) | (index << self.offset_bits)

    def _fetch_block_from_lower(self, block_base):
        if self.lower_level:
            return self.lower_level.read_block(block_base, self.block_size)
        else:
            # Lowest cache level: fetch from main memory
            data = []
            for i in range(self.block_size):
                addr = block_base + i
                if addr < self.memory.size:
                    data.append(self.memory.data[addr])
                else:
                    data.append(bit8(0))
            return data, self.main_mem_latency

    def _write_block_to_lower(self, evicted_base, evicted_data):
        if self.lower_level:
            return self.lower_level.write_block(evicted_base, evicted_data)
        else:
            # Write directly to main memory
            for i in range(len(evicted_data)):
                addr = evicted_base + i
                if addr < self.memory.size:
                    self.memory.data[addr] = evicted_data[i]
            return self.main_mem_latency

    def read_byte(self, address_val):
        tag, index, offset = self.get_tag_index_offset(address_val)
        cache_set = self.sets[index]
        line = cache_set.find_line(tag)
        
        if line:
            self.hits += 1
            return line.data[offset], self.latency
            
        self.misses += 1
        block_base = address_val & ~((1 << self.offset_bits) - 1)
        
        block_data, fetch_latency = self._fetch_block_from_lower(block_base)
        
        eviction_latency = 0
        evicted_info = cache_set.evict_and_insert(tag, block_data)
        if evicted_info:
            evicted_tag, evicted_data = evicted_info
            evicted_base = self.get_base_address(evicted_tag, index)
            eviction_latency = self._write_block_to_lower(evicted_base, evicted_data)
            
        # Re-fetch line
        line = cache_set.find_line(tag)
        return line.data[offset], self.latency + fetch_latency + eviction_latency

    def read_block(self, addr, size):
        tag, index, offset = self.get_tag_index_offset(addr)
        cache_set = self.sets[index]
        line = cache_set.find_line(tag)
        
        if line:
            self.hits += 1
            return list(line.data[offset : offset + size]), self.latency
            
        self.misses += 1
        block_base = addr & ~((1 << self.offset_bits) - 1)
        
        block_data, fetch_latency = self._fetch_block_from_lower(block_base)
        
        eviction_latency = 0
        evicted_info = cache_set.evict_and_insert(tag, block_data)
        if evicted_info:
            evicted_tag, evicted_data = evicted_info
            evicted_base = self.get_base_address(evicted_tag, index)
            eviction_latency = self._write_block_to_lower(evicted_base, evicted_data)
            
        line = cache_set.find_line(tag)
        return list(line.data[offset : offset + size]), self.latency + fetch_latency + eviction_latency

    def write_byte(self, address_val, value: bit8):
        tag, index, offset = self.get_tag_index_offset(address_val)
        cache_set = self.sets[index]
        line = cache_set.find_line(tag)
        latency = self.latency
        
        if line:
            self.hits += 1
            line.data[offset] = value
            line.dirty = True
            return latency
            
        self.misses += 1
        block_base = address_val & ~((1 << self.offset_bits) - 1)
        block_data, fetch_latency = self._fetch_block_from_lower(block_base)
        
        eviction_latency = 0
        evicted_info = cache_set.evict_and_insert(tag, block_data)
        if evicted_info:
            evicted_tag, evicted_data = evicted_info
            evicted_base = self.get_base_address(evicted_tag, index)
            eviction_latency = self._write_block_to_lower(evicted_base, evicted_data)
            
        line = cache_set.find_line(tag)
        line.data[offset] = value
        line.dirty = True
        return latency + fetch_latency + eviction_latency

    def write_block(self, addr, data_block):
        size = len(data_block)
        tag, index, offset = self.get_tag_index_offset(addr)
        cache_set = self.sets[index]
        line = cache_set.find_line(tag)
        latency = self.latency
        
        if line:
            self.hits += 1
            line.data[offset : offset + size] = list(data_block)
            line.dirty = True
            return latency
            
        self.misses += 1
        block_base = addr & ~((1 << self.offset_bits) - 1)
        full_block_data, fetch_latency = self._fetch_block_from_lower(block_base)
        
        eviction_latency = 0
        evicted_info = cache_set.evict_and_insert(tag, full_block_data)
        if evicted_info:
            evicted_tag, evicted_data = evicted_info
            evicted_base = self.get_base_address(evicted_tag, index)
            eviction_latency = self._write_block_to_lower(evicted_base, evicted_data)
            
        line = cache_set.find_line(tag)
        line.data[offset : offset + size] = list(data_block)
        line.dirty = True
        return latency + fetch_latency + eviction_latency

class CacheHierarchy:
    def __init__(self, memory, l1d_config, l2_config, main_mem_config):
        self.memory = memory
        self.main_mem_latency = main_mem_config["latency"]
        
        self.l2 = Cache("L2", l2_config, lower_level=None, memory=memory, main_mem_latency=self.main_mem_latency)
        self.l1d = Cache("L1D", l1d_config, lower_level=self.l2)
        self.total_mem_stalls = 0

    def flush_all_caches(self):
        """
        Flush all dirty cache lines from L1D and L2 caches to main memory.
        This ensures that all written data is synchronized with main memory.
        """
        # Flush L1D cache
        for cache_set in self.l1d.sets:
            for line in cache_set.lines:
                if line.valid and line.dirty:
                    base_addr = self.l1d.get_base_address(line.tag, self.l1d.sets.index(cache_set))
                    self.l1d._write_block_to_lower(base_addr, line.data)
                    line.dirty = False
        
        # Flush L2 cache
        for cache_set in self.l2.sets:
            for line in cache_set.lines:
                if line.valid and line.dirty:
                    base_addr = self.l2.get_base_address(line.tag, self.l2.sets.index(cache_set))
                    self.l2._write_block_to_lower(base_addr, line.data)
                    line.dirty = False
        
    def read_word(self, address: bit32):
        b1, l1 = self.l1d.read_byte(address.value)
        b2, l2 = self.l1d.read_byte(address.value + 1)
        b3, l3 = self.l1d.read_byte(address.value + 2)
        b4, l4 = self.l1d.read_byte(address.value + 3)
        val = bit32(b1.value << 24 | b2.value << 16 | b3.value << 8 | b4.value)
        latency = max(l1, l2, l3, l4)
        if latency > 1:
            self.total_mem_stalls += (latency - 1)
        return val, latency

    def write_word(self, address: bit32, value: bit32):
        l1 = self.l1d.write_byte(address.value, bit8(value.value >> 24))
        l2 = self.l1d.write_byte(address.value + 1, bit8((value.value >> 16) & 0xFF))
        l3 = self.l1d.write_byte(address.value + 2, bit8((value.value >> 8) & 0xFF))
        l4 = self.l1d.write_byte(address.value + 3, bit8(value.value & 0xFF))
        latency = max(l1, l2, l3, l4)
        if latency > 1:
            self.total_mem_stalls += (latency - 1)
        return latency
