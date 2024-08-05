#!/usr/bin/env python3

import subprocess
import socket
import typer
from rich.console import Console
from rich.progress import track
from concurrent.futures import ThreadPoolExecutor, as_completed

app = typer.Typer(help="Scan local network for Raspberry Pi.")
console = Console()

RASPBERRY_PI_MAC_PREFIXES = [
    "28:CD:C1",
    "2C:CF:67",
    "B8:27:EB",
    "D8:3A:DD",
    "DC:A6:32",
    "E4:5F:01"
]

def get_current_ip():
    try:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        return local_ip
    except Exception as e:
        console.print(f":warning: [bold yellow]Unable to determine current IP address: {e}[/bold yellow]")
        return None

def get_hostname(ip):
    try:
        host = socket.gethostbyaddr(ip)
        return host[0]  # Hostname
    except socket.herror:
        return None

def get_mac_address_from_arp(current_ip):
    try:
        arp_output = subprocess.check_output(['arp', '-a', '-N', current_ip]).decode('utf-8')
        arp_lines = arp_output.splitlines()
        devices = []
        for line in arp_lines:
            if 'dynamic' in line:
                parts = line.split()
                ip = parts[0]
                mac = parts[1].replace('-', ':')
                devices.append((ip, mac))
        return devices
    except Exception as e:
        console.print(f":warning: [bold yellow]Error getting MAC addresses from ARP: {e}[/bold yellow]")
        return []

def is_raspberry_pi(mac):
    if not mac:
        return False
    mac_prefix = mac.upper()[:8]
    return any(mac_prefix.startswith(prefix) for prefix in RASPBERRY_PI_MAC_PREFIXES)

@app.command()
def main(
    base_ip: str = typer.Argument('', help="Base IP address (default: 192.168.45)"),
):
    """
    Scan local network for Raspberry Pi devices.
    """

    if not base_ip:
        base_ip = get_current_ip()
        base_ip = '.'.join(base_ip.split('.')[:-1])
        if base_ip is None:
            raise typer.Exit()

    current_ip = get_current_ip()
    current_hostname = get_hostname(current_ip)
    console.print(f"Current IP: [bold blue]{current_ip}[/bold blue] ([bold magenta]{current_hostname}[/bold magenta])\n")

    devices = get_mac_address_from_arp(current_ip)

    rpi_devices = [ip for ip, mac in devices if is_raspberry_pi(mac)]
    
    if rpi_devices:
        console.print(":sparkles: [bold green]Raspberry Pi(s) found:[/bold green]")
        for ip in rpi_devices:
            console.print(f"[bold cyan]{ip}[/bold cyan] ([bold magenta]Raspberry Pi[/bold magenta])")
    else:
        console.print(":disappointed: [bold red]No Raspberry Pi(s) found.[/bold red]")

if __name__ == "__main__":
    app()
