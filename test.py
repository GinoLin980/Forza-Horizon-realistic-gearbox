import sys; sys.dont_write_bytecode = True
import socket
import select
from contextlib import closing
import time

def UDPconnectable(ip: str, port: int, timeout: float = 0.1, retries: int = 3, delay: float = 0.5) -> bool:
    for attempt in range(retries):
        try:
            with closing(socket.socket(socket.AF_INET, socket.SOCK_DGRAM)) as sock:
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                sock.bind((ip, port))
                ready = select.select([sock], [], [], timeout)
                return bool(ready[0])
        except OSError as e:
            if attempt < retries - 1:
                time.sleep(delay)
            else:
                print(f"Error: {e}")
                return False

print(UDPconnectable("127.0.0.1", 8000))
