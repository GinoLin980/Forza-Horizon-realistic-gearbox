# 2024/5/9 v2.3 updated with custom tkinter
# By GinoLin980
import sys; sys.dont_write_bytecode = True # prevent the generation of .pyc files
import socket
import keyboard, time
from DATAOUT import *
import GUI

# the splash photo when startup
try:
    import pyi_splash
    pyi_splash.close()
except ImportError:
    pass

class Gearbox():
    def __init__(self):
        self.VERSION = "v2.3"
        
        self.UDP_IP = "127.0.0.1"  # This sets server ip to localhost
        self.UDP_PORT = 8000  # You can freely edit this
        
        