from typing import List

import typer
from synapso_core.cortex_manager import CortexManager
from synapso_core.data_store.data_models import DBCortex

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
    cortex_id = cmd_create_cortex(folder_location, cortex_name)
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
        raise typer.BadParameter("Either cortex ID or cortex name is required")
    cmd_index_cortex(cortex_id, cortex_name)
    typer.echo(f"Cortex {cortex_id} indexed successfully")


@cortex_app.command(name="list")
def cmd_cortex_list():
    cortex_manager = CortexManager()
    result = cortex_manager.list_cortices()
    result_str = _format_cortex_list(result)
    typer.echo(result_str)


def cmd_create_cortex(folder_location: str, cortex_name: str):
    cortex_manager = CortexManager()
    return cortex_manager.create_cortex(cortex_name, folder_location)


def cmd_index_cortex(cortex_id: str, cortex_name: str):
    # Process cortex_id only if provided
    if cortex_id:
        cortex_id = cortex_id.strip().lower()
    try:
        cortex_manager = CortexManager()
        cortex_manager.index_cortex(cortex_id, cortex_name)
    except Exception as e:
        typer.echo(f"Error indexing cortex: {e}", err=True)
        raise typer.Exit(1) from e

def _format_cortex_list(cortex_list: List[DBCortex]):
    msg = "Cortex ID\tCortex Name\tCortex Path\n"
    for cortex in cortex_list:
        msg += f"{cortex.cortex_id}\t{cortex.cortex_name}\t{cortex.path}\n"
    return msg
