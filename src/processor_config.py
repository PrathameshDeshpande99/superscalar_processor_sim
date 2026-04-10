"""
THIS FILE CONTAINS LATENCIES OF DIFFERENT UNITS IN THE PROCESSOR. MODIFY THE LATENCIES AS PER YOUR REQUIREMENTS.
"""

# Cache Configurations
L1D_CONFIG = {
    "size": 8,  # Bytes
    "block_size": 4,  # Bytes
    "associativity": 2,  # Ways
    "latency": 1,  # Clock cycles
    "replacement": "LRU",  # "LRU" or "Random"
}

L1I_CONFIG = {
    "size": 8,  # Bytes
    "block_size": 4,  # Bytes
    "associativity": 2,  # Ways
    "latency": 1,  # Clock cycles
    "replacement": "LRU",  # "LRU" or "Random"
}

L2_CONFIG = {
    "size": 32,
    "block_size": 4,
    "associativity": 8,
    "latency": 5,  # Clock cycles
    "replacement": "Random",
}

MAIN_MEMORY_CONFIG = {
    "latency": 20  # Clock cycles
}

IF_LATENCY = 1
RF_LATENCY = 1
EX_LATENCY = 1
MEM_LATENCY = MAIN_MEMORY_CONFIG["latency"]
WB_LATENCY = 1

DATA_FORWARDING_ENABLED = False
