"""Rich console helpers for CLI output."""

from rich.console import Console

console = Console()


def info(message: str) -> None:
    console.print(message)


def warn(message: str) -> None:
    console.print(f"[yellow]{message}[/yellow]")


def success(message: str) -> None:
    console.print(f"[green]{message}[/green]")


def done(message: str) -> None:
    console.print(f"[bold green]✓[/bold green] {message}")
