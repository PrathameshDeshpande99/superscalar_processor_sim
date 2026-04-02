class L1_cache:
    def __init__(
        self,
        block_size,
        cache_size,
        associativity,
        access_latency,
        main_mem_access_time,
        i_to_d_ratio,
    ):
        self.total_cache_size = cache_size
        self.block_size = block_size
        self.associativity = associativity
        self.access_latency = access_latency
        self.main_mem_access_time = main_mem_access_time
        self.i_to_d_ratio = i_to_d_ratio
        self.no_blocks = cache_size / block_size
        self.no_I_blocks = int(self.no_blocks * i_to_d_ratio)
        self.no_D_blocks = self.no_blocks - self.no_I_blocks

