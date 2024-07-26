import customtkinter as ctk
from tkinter import messagebox
from ping3 import ping, verbose_ping
import logging
import ipaddress
from typing import List, Union
import pydivert
import os
import threading
import re
import sys

### taken from https://github.com/twisteroidambassador/retroflect/blob/master/retroflect.py
DEFAULT_PRIORITY = 822  # A low-ish priority, chosen randomly
IPAddressType = Union[ipaddress.IPv4Address, ipaddress.IPv6Address]

logger = logging.getLogger(__package__)

def reflect(
        reflect_hosts: List[IPAddressType],
        shield_ports: List[int],
        priority: int,
):
    filter_hosts = ' or '.join(
        f'{"ipv6" if host.version == 6 else "ip"}.DstAddr == {host}'
        for host in reflect_hosts
    )
    filter_str = f'outbound and (tcp or udp) and ({filter_hosts})'
    if shield_ports:
        filter_ports = ' or '.join(
            f'tcp.DstPort == {port} or udp.DstPort == {port}' for port in shield_ports)
        filter_str = f'({filter_str}) or ' \
                     f'(inbound and ({filter_ports}))'

    with pydivert.WinDivert(filter_str, priority=priority) as wd:
        for packet in wd:
            logger.debug('Received packet:\n%r', packet)
            if packet.is_outbound:
                (packet.src_addr, packet.dst_addr) = \
                    (packet.dst_addr, packet.src_addr)
                packet.direction = pydivert.Direction.INBOUND
                logger.debug('Reflecting packet:\n%r', packet)
                wd.send(packet)
            else:
                logger.debug('Dropping packet')


def run_reflect(reflect_address: str, shield: int = None, priority: int = DEFAULT_PRIORITY, verbose: bool = False):
    reflect_address = [ipaddress.ip_address(reflect_address)]
    shield = [shield]
    
    loglevel = logging.DEBUG if verbose else logging.WARNING
    logging.basicConfig(level=loglevel)

    if not -1000 <= priority <= 1000:
        sys.exit('Priority level must be between -1000 and 1000 inclusive')

    try:
        reflect(reflect_address, shield, priority)
    except PermissionError as e:
        sys.exit(f'Caught PermissionError: are you running this program '
                 f'with Administrator privileges?\n{e!r}')
###

# File to save not in use IP addresses
NOT_IN_USE_FILE = "not_in_use_ips.txt"

class PingUtility(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Ping and Retroflect Utility")
        self.geometry("700x600")  # Increased size to accommodate instructions

        self.reflect_thread = None

        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(4, weight=1)

        # Create widgets
        self.create_widgets()

    def create_widgets(self):
        # Instructions
        self.instructions = ctk.CTkTextbox(self, width=680, height=140)
        self.instructions.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.instructions.insert("end", "The typical unused IPs are :\n"
                                                        "192.0.2.1 | 198.51.100.1 | 203.0.113.1 | 100.64.0.1 | 172.31.255.1\n")
        self.instructions.insert("end", "Instructions:\n")
        self.instructions.insert("end", "1. Enter an IP address in the field below and click 'Ping' to check if it's in use.\n")
        self.instructions.insert("end", "2. IP addresses not in use will be saved and appear in the dropdown menu.\n")
        self.instructions.insert("end", "3. Select an IP from the dropdown and click 'Retroflect' to start the retroflect process.\n")
        self.instructions.insert("end", "4. Set the Forza Data Out IP to the IP you chose.\n")
        self.instructions.insert("end", "5. Run FHGearbox_MS_store.exe\n")
        self.instructions.configure(state="disabled")  # Make it read-only

        # Entry for IP address
        self.entry_label = ctk.CTkLabel(self, text="Enter IP address:")
        self.entry_label.grid(row=1, column=0, padx=10, pady=(10, 0), sticky="w")
        self.entry = ctk.CTkEntry(self, width=300)
        self.entry.grid(row=2, column=0, padx=10, pady=(0, 10), sticky="we")

        # Ping button
        self.ping_button = ctk.CTkButton(self, text="Ping", command=self.ping_address)
        self.ping_button.grid(row=3, column=0, padx=10, pady=10)

        # Output text area
        self.output_text = ctk.CTkTextbox(self, width=680, height=300, font=ctk.CTkFont(size=15, weight="bold"))
        self.output_text.grid(row=4, column=0, padx=10, pady=10, sticky="nsew")

        self.output_text.tag_config("in_use", foreground="red")
        self.output_text.tag_config("not_in_use", foreground="green")

        # Option menu for IP addresses
        self.selected_ip = ctk.StringVar()
        self.ips = self.load_not_in_use_ips()
        if self.ips:
            self.selected_ip.set(self.ips[0])
        else:
            self.selected_ip.set("")
        self.option_menu = ctk.CTkOptionMenu(self, values=self.ips, variable=self.selected_ip)
        self.option_menu.grid(row=5, column=0, padx=10, pady=10)

        # Retroflect button
        self.retroflect_button = ctk.CTkButton(self, text="Retroflect", command=self.retroflect_command)
        self.retroflect_button.grid(row=6, column=0, padx=10, pady=10)

    def ping_address(self):
        hostname = self.entry.get()

        # Validate input
        if not hostname:
            messagebox.showerror("Error", "Please enter an IP address.")
            return
        if not re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", hostname):
            messagebox.showerror("Error", "Invalid IP address format. Please use XXX.XXX.XXX.XXX.")
            return

        try:
            # Use ping3 for pinging the IP address
            result = ping(hostname)

            if result is not None:
                self.output_text.insert("end", f"{hostname} is in use.\n")
                self.output_text.tag_add("in_use", "end-2l", "end-1l")
            else:
                self.output_text.insert("end", f"{hostname} is not in use.\n")
                self.output_text.tag_add("not_in_use", "end-2l", "end-1l")
                self.save_not_in_use_ip(hostname)
        except Exception as e:
            if str(e) != "not readable":
                self.output_text.insert("end", f"An unexpected error occurred: {e}\n")

        self.output_text.see("end")
        self.update_option_menu()



    def save_not_in_use_ip(self, ip):
        with open(NOT_IN_USE_FILE, "a") as file:
            file.write(ip+"\n")

    def load_not_in_use_ips(self):
        if os.path.exists(NOT_IN_USE_FILE):
            with open(NOT_IN_USE_FILE, "r") as file:
                return [line.strip() for line in file.readlines()]
        return []

    def update_option_menu(self):
        self.ips = self.load_not_in_use_ips()
        self.option_menu.configure(values=self.ips)
        if self.ips:
            self.selected_ip.set(self.ips[0])

    def retroflect_command(self):
        ip = self.selected_ip.get()
        if ip:
            if self.reflect_thread and self.reflect_thread.is_alive():
                messagebox.showinfo("Retroflect", "Retroflect is already running.\nIf you want to use another IP, please restart the program.")
                return

            try:
                self.reflect_thread = threading.Thread(target=run_reflect, args=(ip, 8000))
                self.reflect_thread.daemon = True # make sure thread closes after the main loop ends
                self.reflect_thread.start()
                self.output_text.insert("end", f"Starting Retroflect for {ip}.\n")
            except Exception as e:
                self.output_text.insert("end", f"An error occurred while running retroflect: {e}\n")
        else:
            messagebox.showwarning("Warning", "No IP address selected")

if __name__ == "__main__":
    if sys.platform.startswith('win'):
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    
    app = PingUtility()
    app.mainloop()
    sys.exit(0)
