import typer

from ..rest_client import SynapsoRestClient
from .server import ensure_server, get_server_config


def cmd_query(query: str):
    """Execute a query against a cortex."""
    ensure_server()
    server_config = get_server_config()
    if not server_config:
        raise typer.BadParameter("Server is not running")
    rest_client = SynapsoRestClient(f"http://127.0.0.1:{server_config['port']}")
    response = rest_client.query(query)
    typer.echo(response)
