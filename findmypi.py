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
    
def get_mac_address(ip):
    try:
        arp_output = subprocess.check_output(['arp', '-a', ip]).decode('utf-8')
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

def ping_test(ip):
    try:
        output = subprocess.check_output(['ping', '-n', '1', '-w', '1', ip], stderr=subprocess.STDOUT, timeout=2)
        if b"unreachable" not in output:
            return ip
    except subprocess.CalledProcessError:
        return None
    except:
        return None

def scan_local_network(start_ip, end_ip, base_ip, workers):
    ip_addresses = [f'{base_ip}.{i}' for i in range(start_ip, end_ip + 1)]
    reachable_ips = []

    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {executor.submit(ping_test, ip): ip for ip in ip_addresses}
        for future in track(as_completed(futures), total=len(futures), description=""):
            ip = future.result()
            if ip:
                reachable_ips.append(ip)

    return reachable_ips

@app.command()
def main(
    base_ip: str = typer.Argument('', help="Base IP address (default: 192.168.45)"),
    workers: int = typer.Option(100, help="Maximum number of threads (default: 10)")
):
    """
    Scan local network for Raspberry Pi devices.
    """

    current_ip = get_current_ip() if not base_ip else base_ip
    current_hostname = get_hostname(current_ip)
    console.print(f"Current IP: [bold blue]{current_ip}[/bold blue] ([bold magenta]{current_hostname}[/bold magenta])\n")

    if not base_ip:
        base_ip = get_current_ip()
        base_ip = '.'.join(base_ip.split('.')[:-1])
        if base_ip is None:
            raise typer.Exit()
    else:
        base_ip = '.'.join(base_ip.split('.')[:-1])


    start_ip = 1
    end_ip = 254

    console.print(f":hourglass: Scanning network for Raspberry Pis...")

    reachable_ips = scan_local_network(start_ip, end_ip, base_ip, workers)
    reachable_ips = [ip for ip in reachable_ips if ip != current_ip]    

    devices = []
    for ip in reachable_ips:
        mac_address = get_mac_address(ip)
        if len(mac_address) > 0:
            mac_address = mac_address[0]
            devices.append(mac_address)

    rpi_devices = [ip for ip, mac in devices if is_raspberry_pi(mac)]
    
    if rpi_devices:
        console.print("\n:sparkles: [bold green]Raspberry Pi(s) found:[/bold green]")
        for ip in rpi_devices:
            console.print(f"[bold cyan]{ip}[/bold cyan] ([bold magenta]Raspberry Pi[/bold magenta])")
    else:
        console.print(":disappointed: [bold red]No Raspberry Pi(s) found.[/bold red]")


if __name__ == "__main__":
    app()
