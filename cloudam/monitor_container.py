import subprocess
import time
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def get_container_stats(container_name):
    try:
        ans = subprocess.run(['docker', 'stats', '--no-stream', '--format', 
                                 '{{.NetIO}}', container_name], capture_output=True, text=True)
        
        if ans.returncode != 0:
            logging.error(f"Error docker stats: {ans.stderr.strip()}")
            return None
        
        # network I/O stats (1.45kB / 1.75kB)
        net_io = ans.stdout.strip()
        if '/' in net_io:
            rx_bytes, tx_bytes = net_io.split(' / ')
            return rx_bytes, tx_bytes
        else:
            logging.error(f"Error format docker stats: {net_io}")
            return None
    except Exception as e:
        logging.error(f"Error: {str(e)}")
        return None


def log_container_network_stats(container_name):
    while True:
        # Get the transmitted and received bytes for the container
        stats = get_container_stats(container_name)
        if stats:
            rx_bytes, tx_bytes = stats
            # Log the stats with timestamp
            logging.info(f"RX: {rx_bytes}, TX: {tx_bytes}")
        
        # Wait for a few seconds before next iteration (e.g., 10 seconds)
        time.sleep(10)


if __name__ == "__main__":
    container_name = "node01"
    ## considere um array para fazer com vários
    log_container_network_stats(container_name)
