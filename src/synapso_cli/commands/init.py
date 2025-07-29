import os
from pathlib import Path
from typing import Any, Dict

import typer
import yaml
from synapso_core.config_manager import GlobalConfig, get_config


def init_synapso():
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
        SYNAPSO_HOME.mkdir(parents=True, exist_ok=True)
        os.environ["SYNAPSO_HOME"] = str(SYNAPSO_HOME)
        SYNAPSO_HOME_STR = str(SYNAPSO_HOME.expanduser().resolve())
        typer.echo(f"SYNAPSO_HOME not set, using default: {SYNAPSO_HOME_STR}")
    else:
        typer.echo(f"SYNAPSO_HOME set to: {SYNAPSO_HOME_STR}")

    config_path = Path(SYNAPSO_HOME_STR) / "config.yaml"
    if config_path.exists():
        typer.echo(f"Config file already exists at {config_path}")
        return

    typer.echo(f"Creating config file at {config_path}")
    config_path.touch()

    # copy the default config file to the config file
    default_config = _get_default_config()
    with open(config_path, "w") as f:
        yaml.dump(default_config, f)
    typer.echo(f"Config file created at {config_path}")

    _initialize(str(config_path))


def _get_default_config() -> Dict[str, Any]:
    """
    Get the default config.
    """
    default_config_path = (
        Path(__file__).parent.parent / "resources" / "default_config.yaml"
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
    db_path = Path(location)
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
        _initialize_sqlite_db(meta_store_path)
    except Exception as e:
        typer.echo(f"Error initializing meta store: {e}", err=True)
        raise typer.Exit(1) from e


def _initialize_vector_store(config_file: str):
    try:
        config: GlobalConfig = get_config(config_file)
        vector_store_path = config.vector_store.vector_db_path
        _initialize_sqlite_db(vector_store_path)
    except Exception as e:
        typer.echo(f"Error initializing vector store: {e}", err=True)
        raise typer.Exit(1) from e


def _initialize_chunk_store(config_file: str):
    try:
        config: GlobalConfig = get_config(config_file)
        private_store_path = config.private_store.private_db_path
        _initialize_sqlite_db(private_store_path)
    except Exception as e:
        typer.echo(f"Error initializing private store: {e}", err=True)
        raise typer.Exit(1) from e
