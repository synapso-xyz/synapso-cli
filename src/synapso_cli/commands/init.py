import os
import re
from pathlib import Path
from typing import Any, Dict

import typer
import yaml

from ..config import GlobalConfig, get_config
from ..rest_client import SynapsoRestClientError
from .server import ensure_server, get_rest_client, is_server_running
from .server import restart as restart_server


def set_environment_variable_system_wide(var_name: str, var_value: str):
    """Set an environment variable system-wide by modifying shell configuration files."""
    # Validate
    if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", var_name):
        typer.echo(f"Invalid variable name: {var_name}", err=True)
        return

    home = Path.home()
    shell = os.environ.get("SHELL", "")

    # Determine which shell configuration file to use
    if "zsh" in shell:
        config_file = home / ".zshrc"
    elif "bash" in shell:
        config_file = home / ".bash_profile"
        if not config_file.exists():
            config_file = home / ".bashrc"
    else:
        # Default to .zshrc for macOS
        config_file = home / ".zshrc"

    # Check if the variable is already set
    if config_file.exists():
        with open(config_file, "r") as f:
            content = f.read()
            if f"export {var_name}=" in content:
                typer.echo(
                    f"Environment variable {var_name} is already set in {config_file}"
                )
                return

    # Add the export statement to the configuration file
    export_line = f'\nexport {var_name}="{var_value}"\n'

    with open(config_file, "a") as f:
        f.write(export_line)

    typer.echo(f"Added {var_name}={var_value} to {config_file}")
    typer.echo(
        f"Please run 'source {config_file}' or restart your terminal to apply changes"
    )


def init_synapso(force_db_reset: bool = False):
    """
    Initialize a new Synapso project.

    We need to do the following:
    1. Check if $SYNAPSO_HOME is set. If set, ensure that it exists and is a directory.
    2. Ask the user they want to go with default config or custom config.
    3. If they choose default config, create the config file with default values.
    4. If they choose custom config, open the config file in the editor.

    """
    typer.echo("Initializing Synapso project...")
    SYNAPSO_HOME_STR = os.getenv("SYNAPSO_HOME")
    if not SYNAPSO_HOME_STR:
        SYNAPSO_HOME = Path.home() / ".synapso"
        SYNAPSO_HOME_STR = str(SYNAPSO_HOME.expanduser().resolve())

        # Set the environment variable system-wide
        set_environment_variable_system_wide("SYNAPSO_HOME", SYNAPSO_HOME_STR)

        # Also set it for the current process
        os.environ["SYNAPSO_HOME"] = SYNAPSO_HOME_STR
        typer.echo(f"SYNAPSO_HOME not set, using default: {SYNAPSO_HOME_STR}")
    else:
        typer.echo(f"SYNAPSO_HOME set to: {SYNAPSO_HOME_STR}")
        SYNAPSO_HOME = Path(SYNAPSO_HOME_STR)

    SYNAPSO_HOME.mkdir(parents=True, exist_ok=True)

    config_path = Path(SYNAPSO_HOME_STR) / "config.yaml"
    if config_path.exists():
        typer.echo(f"Config file already exists at {config_path}")
    else:
        typer.echo(f"Creating config file at {config_path}")
        default_config = _get_default_config()
        with open(config_path, "w") as f:
            yaml.dump(default_config, f, default_flow_style=False)
        typer.echo(f"Config file created at {config_path}")

    if force_db_reset:
        # Remove db files
        _remove_db_files(config_path)
        if is_server_running():
            restart_server()

    # Start the server
    typer.echo("Starting server...")
    ensure_server()
    typer.echo("Server started.")

    _initialize()


def _remove_db_files(config_path: Path):
    config: GlobalConfig = get_config(str(config_path))

    # Validate that paths are within the SYNAPSO_HOME
    synapso_home = (
        Path(os.getenv("SYNAPSO_HOME", Path.home() / ".synapso")).expanduser().resolve()
    )

    meta_store_path = Path(config.meta_store.meta_db_path).expanduser().resolve()
    vector_store_path = Path(config.vector_store.vector_db_path).expanduser().resolve()
    private_store_path = (
        Path(config.private_store.private_db_path).expanduser().resolve()
    )

    for path in [meta_store_path, vector_store_path, private_store_path]:
        if not str(path).startswith(str(synapso_home)):
            typer.echo(
                f"Path {path} is not within SYNAPSO_HOME {synapso_home}", err=True
            )
            raise typer.Exit(1)

    if meta_store_path.exists():
        typer.echo(f"Removing meta store at {meta_store_path}")
        meta_store_path.unlink()

    if vector_store_path.exists():
        typer.echo(f"Removing vector store at {vector_store_path}")
        vector_store_path.unlink()

    if private_store_path.exists():
        typer.echo(f"Removing private store at {private_store_path}")
        private_store_path.unlink()


def _get_default_config() -> Dict[str, Any]:
    """
    Get the default config.
    """
    default_config_path = (
        Path(__file__).parent.parent.parent.parent / "resources" / "default_config.yaml"
    )
    if not default_config_path.exists():
        typer.echo(
            f"Error: Default config file not found at {default_config_path}", err=True
        )
        raise typer.Exit(1)

    with open(default_config_path, "r") as f:
        default_config = yaml.safe_load(f)
    return default_config


def _initialize():
    rest_client = get_rest_client()
    try:
        response = rest_client.system_init()
    except SynapsoRestClientError as e:
        typer.echo(f"Synapso REST client error: {e}", err=True)
        raise typer.Exit(1) from e
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1) from e
    meta_store_status = response["meta_store_initialized"]
    vector_store_status = response["vector_store_initialized"]
    private_store_status = response["private_store_initialized"]

    if not meta_store_status:
        typer.echo("Meta store not initialized", err=True)
        raise typer.Exit(1)
    if not vector_store_status:
        typer.echo("Vector store not initialized", err=True)
        raise typer.Exit(1)
    if not private_store_status:
        typer.echo("Private store not initialized", err=True)
        raise typer.Exit(1)

    typer.echo("System initialized successfully")
