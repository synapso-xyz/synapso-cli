from typing import Any, Dict, List

import typer

from ...rest_client import SynapsoRestClientError
from ..server import get_rest_client

cortex_app = typer.Typer()


@cortex_app.command(name="create")
def create(
    folder_location: str = typer.Option(
        ...,
        help="The location of the folder to create the cortex in",
        metavar="FOLDER_LOCATION",
    ),
    cortex_name: str = typer.Option(
        ..., help="The name of the cortex to create", metavar="CORTEX_NAME"
    ),
):
    rest_client = get_rest_client()
    try:
        response = rest_client.create_cortex(folder_location, cortex_name)
    except SynapsoRestClientError as e:
        typer.echo(f"Synapso REST client error: {e}", err=True)
        raise typer.Exit(1) from e
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1) from e
    typer.echo(response)
    cortex_id = response["cortex"]["id"]
    typer.echo(
        f"Created cortex {cortex_name} at {folder_location}. Cortex ID: {cortex_id}"
    )


@cortex_app.command(name="index")
def index(
    cortex_id: str = typer.Option(
        None,
        help="The ID of the cortex to index",
        metavar="CORTEX_ID",
    ),
    cortex_name: str = typer.Option(
        None,
        help="The name of the cortex to index",
        metavar="CORTEX_NAME",
    ),
):
    if not cortex_id and not cortex_name:
        raise typer.BadParameter("Either cortex_id or cortex_name must be provided")
    rest_client = get_rest_client()
    try:
        response = rest_client.index_cortex(cortex_id, cortex_name)
    except SynapsoRestClientError as e:
        typer.echo(f"Synapso REST client error: {e}", err=True)
        raise typer.Exit(1) from e
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1) from e
    typer.echo(response)
    identifier = cortex_id or cortex_name
    typer.echo(f"Cortex {identifier} indexed successfully")


@cortex_app.command(name="list")
def cmd_cortex_list():
    rest_client = get_rest_client()
    try:
        response = rest_client.get_cortex_list()
    except SynapsoRestClientError as e:
        typer.echo(f"Synapso REST client error: {e}", err=True)
        raise typer.Exit(1) from e
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1) from e
    typer.echo(_format_cortex_list(response))


def _format_cortex_list(cortex_list_response: Dict[str, Any]) -> str:
    cortex_list: List[Dict[str, Any]] = cortex_list_response["cortices"]
    if not cortex_list:
        return "No cortexes found"
    msg = "Cortex ID\tCortex Name\tCortex Path\n"
    for cortex in cortex_list:
        msg += f"{cortex['id']}\t{cortex['name']}\t{cortex['path']}\n"  # noqa: E501
    return msg
