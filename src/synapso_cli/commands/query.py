import typer

from ..rest_client import SynapsoRestClientError
from .server import get_rest_client


def cmd_query(query: str):
    """Execute a query against a cortex."""
    rest_client = get_rest_client()
    try:
        response = rest_client.query(query)
        typer.echo(response)
    except SynapsoRestClientError as e:
        typer.echo(f"Synapso REST client error: {e}", err=True)
        raise typer.Exit(1) from e
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1) from e


def cmd_query_stream(query: str):
    """Execute a query against a cortex and stream the results."""
    rest_client = get_rest_client()
    try:
        for chunk in rest_client.query_stream(query):
            typer.echo(chunk, nl=False)
    except SynapsoRestClientError as e:
        typer.echo(f"Synapso REST client error: {e}", err=True)
        raise typer.Exit(1) from e
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1) from e
