#!/usr/bin/env python3

import os
import time
import typer
from rich.console import Console
from rich.live import Live
from rich.table import Table
from rich.progress import track
from concurrent.futures import ThreadPoolExecutor, as_completed

app = typer.Typer(help=__doc__)
console = Console()

def get_folder_size(folder_path):
    total_size = 0
    for dirpath, _, filenames in os.walk(folder_path):
        for filename in filenames:
            try:
                file_path = os.path.join(dirpath, filename)
                total_size += os.stat(file_path).st_size
            except OSError as e:
                print(f"Error calculating size for {file_path}: {e}")
    return total_size


def human_readable_size(size):
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024

def calculate_folder_sizes(directory, table, live):
    folder_sizes = []
    items = [os.path.join(directory, item) for item in os.listdir(directory) if os.path.isdir(os.path.join(directory, item))]

    with ThreadPoolExecutor() as executor:
        future_to_folder = {executor.submit(get_folder_size, item): item for item in items}

        for future in as_completed(future_to_folder):
        # for future in track(as_completed(future_to_folder), total=len(items), description="Calculating folder sizes..."):
            folder = future_to_folder[future]
            size = future.result()
            folder_sizes.append((os.path.basename(folder), size))
            table.add_row(os.path.basename(folder), human_readable_size(size))
            live.refresh()

    return folder_sizes

@app.command()
def main(
    directory: str,
    sort_by: str = typer.Option("name", help="Sort by 'name' or 'size'."),
    order: str = typer.Option("asc", help="Order 'asc' for ascending or 'desc' for descending.")
):
    """
    Calculate the sizes of folders in a specified directory.
    """
    if not os.path.isdir(directory):
        typer.echo("The provided path is not a directory or does not exist.")
        raise typer.Exit()

    folder_count = sum(os.path.isdir(os.path.join(directory, item)) for item in os.listdir(directory))
    console.print(f":hourglass: Calculating folder sizes for [bold blue]{folder_count} folders...[/bold blue]")

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Folder", justify="left")
    table.add_column("Size", justify="right")

    start_time = time.time()

    with Live(table, refresh_per_second=1, console=console) as live:
        folder_sizes = calculate_folder_sizes(directory, table, live)

        if sort_by == "name":
            folder_sizes.sort(key=lambda x: x[0], reverse=(order == "desc"))
        elif sort_by == "size":
            folder_sizes.sort(key=lambda x: x[1], reverse=(order == "desc"))

        # Create a new table for sorted results
        sorted_table = Table(show_header=True, header_style="bold magenta")
        sorted_table.add_column("Folder", justify="left")
        sorted_table.add_column("Size", justify="right")

        for folder, size in folder_sizes:
            sorted_table.add_row(folder, human_readable_size(size))

        live.update(sorted_table)

    end_time = time.time()
    elapsed_time = end_time - start_time

    console.print(f":sparkles: [bold green]Folder sizes in [bold white]'{directory}'[/bold white] calculated in {elapsed_time:.2f}s.[/bold green]")

if __name__ == "__main__":
    app()
