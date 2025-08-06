import warnings

import typer

from .commands.cortex import cortex_app
from .commands.init import init_synapso
from .commands.query import cmd_query
from .commands.server import server_app

warnings.filterwarnings("ignore", category=FutureWarning)

synapso_cli = typer.Typer()
synapso_cli.add_typer(cortex_app, name="cortex")
synapso_cli.add_typer(server_app, name="server")


@synapso_cli.callback()
def main(
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose output including debug logs"
    ),
):
    """Synapso CLI - Local-first AI knowledge management."""
    if verbose:
        set_verbose_logging()


@synapso_cli.command()
def init(
    force_db_reset: bool = typer.Option(
        False, "--force-db-reset", "-f", help="Force reset the database"
    ),
):
    init_synapso(force_db_reset)


@synapso_cli.command()
def query(
    query_text: str = typer.Option(..., help="The query to execute", metavar="QUERY"),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose output including debug logs"
    ),
):
    """Query a cortex with a natural language query."""
    if verbose:
        set_verbose_logging()

    cmd_query(query_text)


def set_verbose_logging(): ...


if __name__ == "__main__":
    synapso_cli()
