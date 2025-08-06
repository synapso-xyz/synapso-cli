import typer

from ...rest_client import SynapsoRestClient
from ..server import ensure_server, get_server_config

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
    ensure_server()
    server_config = get_server_config()
    if not server_config:
        raise typer.BadParameter("Server is not running")
    rest_client = SynapsoRestClient(f"http://127.0.0.1:{server_config['port']}")
    response = rest_client.create_cortex(folder_location, cortex_name)
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
    ensure_server()
    server_config = get_server_config()
    if not server_config:
        raise typer.BadParameter("Server is not running")
    rest_client = SynapsoRestClient(f"http://127.0.0.1:{server_config['port']}")
    response = rest_client.index_cortex(cortex_id, cortex_name)
    typer.echo(response)
    typer.echo(f"Cortex {cortex_id} indexed successfully")


@cortex_app.command(name="list")
def cmd_cortex_list():
    ensure_server()
    server_config = get_server_config()
    if not server_config:
        raise typer.BadParameter("Server is not running")
    rest_client = SynapsoRestClient(f"http://127.0.0.1:{server_config['port']}")
    response = rest_client.get_cortex_list()
    typer.echo(response)
