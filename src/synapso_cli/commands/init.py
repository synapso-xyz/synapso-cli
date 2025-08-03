import os
import re
from pathlib import Path
from typing import Any, Dict

import typer
import yaml
from synapso_core.config_manager import GlobalConfig, get_config
from synapso_core.data_store import DataStoreFactory


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


def init_synapso(force: bool = False):
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

    _initialize(str(config_path))


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


def _initialize_sqlite_db(location: str) -> None:
    """
    Initialize the SQLite database.
    """
    db_path = Path(location).expanduser().resolve()
    print("db_path after resolution:", db_path)
    if db_path.exists():
        typer.echo(f"SQLite database already exists at {db_path}")
        return

    db_path.parent.mkdir(parents=True, exist_ok=True)
    db_path.touch()
    typer.echo(f"SQLite database created at {db_path}")


def _initialize(config_file: str):
    _initialize_meta_store(config_file)
    _initialize_vector_store(config_file)
    _initialize_chunk_store(config_file)


def _initialize_meta_store(config_file: str):
    try:
        config: GlobalConfig = get_config(config_file)
        meta_store_path = config.meta_store.meta_db_path
        meta_store_type = config.meta_store.meta_db_type
        typer.echo(f"Initializing meta store at {meta_store_path}")
        _initialize_sqlite_db(meta_store_path)
        meta_store = DataStoreFactory.get_meta_store(meta_store_type)
        meta_store.setup()

    except Exception as e:
        typer.echo(f"Error initializing meta store: {e}", err=True)
        raise typer.Exit(1) from e


def _initialize_vector_store(config_file: str):
    try:
        config: GlobalConfig = get_config(config_file)
        vector_store_path = config.vector_store.vector_db_path
        vector_store_type = config.vector_store.vector_db_type
        typer.echo(f"Initializing vector store at {vector_store_path}")
        _initialize_sqlite_db(vector_store_path)
        vector_store = DataStoreFactory.get_vector_store(vector_store_type)
        vector_store.setup()
    except Exception as e:
        typer.echo(f"Error initializing vector store: {e}", err=True)
        raise typer.Exit(1) from e


def _initialize_chunk_store(config_file: str):
    try:
        config: GlobalConfig = get_config(config_file)
        private_store_path = config.private_store.private_db_path
        private_store_type = config.private_store.private_db_type
        typer.echo(f"Initializing private store at {private_store_path}")
        _initialize_sqlite_db(private_store_path)
        private_store = DataStoreFactory.get_private_store(private_store_type)
        private_store.setup()
    except Exception as e:
        typer.echo(f"Error initializing private store: {e}", err=True)
        raise typer.Exit(1) from e
