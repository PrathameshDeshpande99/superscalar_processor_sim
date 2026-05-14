import configparser
import os

def parse_config(config_file):
    if not os.path.exists(config_file):
        raise FileNotFoundError(f"Config file {config_file} not found.")
    
    config = configparser.ConfigParser()
    config.read(config_file)
    
    params = {}
    
    # Pipeline
    if 'pipeline' in config:
        params['forwarding_enabled'] = config['pipeline'].getboolean('forwarding_enabled', fallback=False)
    
    # Latencies
    if 'latencies' in config:
        params['add_latency'] = config['latencies'].getint('ADD', fallback=1)
        params['mul_latency'] = config['latencies'].getint('MUL', fallback=3)
        
    # Memory
    if 'memory' in config:
        params['virtual_size_bytes'] = config['memory'].getint('virtual_size_bytes', fallback=1024*1024*1024*4) # 4GB default
        params['physical_size_bytes'] = config['memory'].getint('physical_size_bytes', fallback=1024*1024) # 1MB default
        params['page_size_bytes'] = config['memory'].getint('page_size_bytes', fallback=4096)
        
    # VM
    if 'vm' in config:
        params['dtlb_entries'] = config['vm'].getint('dtlb_entries', fallback=16)
        params['tlb_hit_latency'] = config['vm'].getint('tlb_hit_latency', fallback=1)
        params['page_walk_latency'] = config['vm'].getint('page_walk_latency', fallback=10)
        params['page_fault_latency'] = config['vm'].getint('page_fault_latency', fallback=50)
        params['replacement_policy'] = config['vm'].get('replacement_policy', fallback='lru').lower()
        
    return params
