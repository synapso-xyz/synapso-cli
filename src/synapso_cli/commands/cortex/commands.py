import typer
from synapso_core.cortex_manager import CortexManager

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
        ..., help="The ID of the cortex to index", metavar="CORTEX_ID"
    ),
):
    cmd_index_cortex(cortex_id)
    typer.echo(f"Cortex {cortex_id} indexed successfully")


def cmd_create_cortex(folder_location: str, cortex_name: str):
    cortex_manager = CortexManager()
    return cortex_manager.create_cortex(cortex_name, folder_location)


def cmd_initialize_cortex(cortex_id: str, index_now: bool = False):
    cortex_manager = CortexManager()
    return cortex_manager.initialize_cortex(cortex_id, index_now)


def cmd_index_cortex(cortex_id: str):
    cortex_id = cortex_id.strip().lower()
    if not cortex_id:
        raise typer.BadParameter("Cortex ID is required")
    try:
        cortex_manager = CortexManager()
        return cortex_manager.index_cortex(cortex_id)
    except Exception as e:
        typer.echo(f"Error indexing cortex: {e}", err=True)
        raise typer.Exit(1) from e
