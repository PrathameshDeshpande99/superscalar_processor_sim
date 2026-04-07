import random
import math

class CacheBlock:
    def __init__(self, block_size):
        self.valid = False
        self.tag = None
        self.data = [0] * block_size
        self.dirty = False
        self.last_access_time = 0  # For LRU

class Cache:
    def __init__(self, name, size, block_size, associativity, latency, replacement_policy="LRU"):
        self.name = name
        self.size = size
        self.block_size = block_size
        self.associativity = associativity
        self.latency = latency
        self.replacement_policy = replacement_policy
        
        self.num_blocks = size // block_size
        self.num_sets = self.num_blocks // associativity
        
        # Initialize cache sets
        self.sets = [[CacheBlock(block_size) for _ in range(associativity)] for _ in range(self.num_sets)]
        
        self.hits = 0
        self.misses = 0
        self.timer = 0 # To track access time for LRU

    def get_indices(self, address):
        # address is an integer
        offset_bits = int(math.log2(self.block_size))
        index_bits = int(math.log2(self.num_sets))
        
        offset = address & (self.block_size - 1)
        index = (address >> offset_bits) & (self.num_sets - 1)
        tag = address >> (offset_bits + index_bits)
        
        return tag, index, offset

    def access(self, address):
        self.timer += 1
        tag, index, offset = self.get_indices(address)
        
        set_to_check = self.sets[index]
        
        # Check for hit
        for block in set_to_check:
            if block.valid and block.tag == tag:
                self.hits += 1
                block.last_access_time = self.timer
                return True, self.latency
        
        # Miss logic
        self.misses += 1
        return False, self.latency

    def update_after_miss(self, address):
        tag, index, offset = self.get_indices(address)
        set_to_update = self.sets[index]
        
        # Find an empty block or replace one
        empty_block = None
        for block in set_to_update:
            if not block.valid:
                empty_block = block
                break
        
        if empty_block:
            empty_block.valid = True
            empty_block.tag = tag
            empty_block.last_access_time = self.timer
        else:
            # Replacement needed
            if self.replacement_policy == "LRU":
                # Find least recently used
                lru_block = min(set_to_update, key=lambda b: b.last_access_time)
                lru_block.tag = tag
                lru_block.last_access_time = self.timer
            else: # Random
                target = random.choice(set_to_update)
                target.tag = tag
                target.last_access_time = self.timer

    def get_miss_rate(self):
        total = self.hits + self.misses
        if total == 0: return 0
        return self.misses / total
