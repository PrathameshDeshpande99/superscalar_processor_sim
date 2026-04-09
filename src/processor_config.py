"""
THIS FILE CONTAINS LATENCIES OF DIFFERENT UNITS IN THE PROCESSOR. MODIFY THE LATENCIES AS PER YOUR REQUIREMENTS.
"""

IF_LATENCY = 1
RF_LATENCY = 1
EX_LATENCY = 1
MEM_LATENCY = 20
WB_LATENCY = 1

DATA_FORWARDING_ENABLED = False

# Cache Configurations
L1D_CONFIG = {
    "size": 2,           # Bytes
    "block_size": 2,       # Bytes
    "associativity": 1,     # Ways
    "latency": 1,           # Clock cycles
    "replacement": "LRU"    # "LRU" or "Random"
}

L2_CONFIG = {
    "size": 32,
    "block_size": 16,
    "associativity": 2,
    "latency": 5,
    "replacement": "Random"
}

MAIN_MEMORY_CONFIG = {
    "latency": 20
}
