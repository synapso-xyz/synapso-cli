import warnings
from typing import Annotated

import cyclopts

from .commands.cortex import cortex_app
from .commands.init import init_synapso
from .commands.query import cmd_query, cmd_query_stream
from .commands.server import server_app

warnings.filterwarnings("ignore", category=FutureWarning)

synapso_cli = cyclopts.App(
    name="synapso",
)

synapso_cli.command(cortex_app, name="cortex")
synapso_cli.command(server_app, name="server")


@synapso_cli.command
def init(
    force_db_reset: Annotated[
        bool, cyclopts.Parameter(name=["--force-db-reset", "-f"])
    ] = False,
):
    init_synapso(force_db_reset)


def query(
    query_text: Annotated[str, cyclopts.Parameter(name=["--query", "-q"])],
    cortex_id: Annotated[
        str | None, cyclopts.Parameter(name=["--cortex-id", "-c"])
    ] = None,  # noqa
):
    """Query a cortex with a natural language query."""
    cmd_query(query_text)


@synapso_cli.command(name="ask")
def query_stream(
    query_text: Annotated[str, cyclopts.Parameter(name=["--query", "-q"])],
    cortex_id: Annotated[
        str | None, cyclopts.Parameter(name=["--cortex-id", "-c"])
    ] = None,  # noqa
):
    """Query a cortex with a natural language query and stream the results."""
    cmd_query_stream(query_text)


if __name__ == "__main__":
    synapso_cli()
