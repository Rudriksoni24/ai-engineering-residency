import getpass
import importlib.metadata
import os
import platform
from pathlib import Path

import typer
from dotenv import load_dotenv

load_dotenv()

app = typer.Typer(help="python-environment CLI")


@app.command()
def hello(name: str = typer.Option("world", "--name", "-n", help="Name to greet")):
    """Say hello."""
    typer.echo(f"Hello, {name}!")


@app.command()
def version():
    """Show package version."""
    try:
        version_value = importlib.metadata.version("python-environment")
    except importlib.metadata.PackageNotFoundError:
        version_value = "0.1.0"
    typer.echo(f"python-environment version: {version_value}")


@app.command()
def env():
    """Print environment variables loaded from .env."""
    typer.echo("Environment variables:")
    for key in ["APP_NAME", "ENVIRONMENT", "Debug"]:
        typer.echo(f"{key}={os.getenv(key)}")


@app.command()
def system():
    """Print system information."""
    typer.echo(f"python_version={platform.python_version()}")
    typer.echo(f"platform={platform.platform()}")
    typer.echo(f"os={platform.system()}")
    typer.echo(f"current_user={getpass.getuser()}")
    typer.echo(f"current_directory={Path.cwd()}")


if __name__ == "__main__":
    app()
