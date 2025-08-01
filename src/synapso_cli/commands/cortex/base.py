import typer

from .create import cmd_create_cortex
from .index import cmd_index_cortex
from .init import cmd_initialize_cortex

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


@cortex_app.command(name="init")
def initialize(
    cortex_id: str = typer.Option(
        ..., help="The ID of the cortex to initialize", metavar="CORTEX_ID"
    ),
    index_now: bool = typer.Option(
        False, help="Whether to index the cortex now", metavar="INDEX_NOW"
    ),
):
    cmd_initialize_cortex(cortex_id, index_now)
    action = "initialized and indexed" if index_now else "initialized"
    typer.echo(f"Cortex {cortex_id} {action} successfully")


@cortex_app.command(name="index")
def index(
    cortex_id: str = typer.Option(
        ..., help="The ID of the cortex to index", metavar="CORTEX_ID"
    ),
):
    cmd_index_cortex(cortex_id)
