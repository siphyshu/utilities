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
    Scan local network for reachable IP addresses to find Raspberry Pi.
    """

    if not base_ip:
        base_ip = get_current_ip()
        base_ip = '.'.join(base_ip.split('.')[:-1])
        if base_ip is None:
            raise typer.Exit()

    current_ip = get_current_ip()
    current_hostname = get_hostname(current_ip)
    console.print(f"Current IP: [bold blue]{current_ip}[/bold blue] ([bold magenta]{current_hostname}[/bold magenta])\n")
    
    start_ip = 1
    end_ip = 254

    console.print(f":hourglass: Scanning network for Raspberry Pis...")

    reachable_ips = scan_local_network(start_ip, end_ip, base_ip, workers)

    # remove current IP from the list
    reachable_ips = [ip for ip in reachable_ips if ip != current_ip]

    if reachable_ips:
        console.print("\n:sparkles: [bold green]Reachable IPs found:[/bold green]")
        for ip in reachable_ips:
            console.print(f"[bold cyan]{ip}[/bold cyan] ([bold magenta]Raspberry Pi[/bold magenta])")
    else:
        console.print(":disappointed: [bold red]No reachable IPs found.[/bold red]")

if __name__ == "__main__":
    app()
