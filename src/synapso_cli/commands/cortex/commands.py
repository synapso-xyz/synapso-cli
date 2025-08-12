from typing import Annotated, Any, Dict, List

import cyclopts

from ...rest_client import SynapsoRestClientError
from ..server import get_rest_client

cortex_app = cyclopts.App()


@cortex_app.command
def create(
    folder_location: Annotated[
        str, cyclopts.Parameter(name=["--folder-location", "-f"])
    ],
    cortex_name: Annotated[str, cyclopts.Parameter(name=["--cortex-name", "-n"])],
):
    """Create a new cortex."""
    rest_client = get_rest_client()
    try:
        response = rest_client.create_cortex(folder_location, cortex_name)
    except SynapsoRestClientError as e:
        print(f"Synapso REST client error: {e}")
        raise cyclopts.CycloptsError(f"Synapso REST client error: {e}")
    except Exception as e:
        print(f"Error: {e}")
        raise cyclopts.CycloptsError(f"Error: {e}")
    print(response)
    cortex_id = response["cortex"]["id"]
    print(f"Created cortex {cortex_name} at {folder_location}. Cortex ID: {cortex_id}")


@cortex_app.command
def index(
    cortex_id: Annotated[
        str | None, cyclopts.Parameter(name=["--cortex-id", "-i"])
    ] = None,
    cortex_name: Annotated[
        str | None, cyclopts.Parameter(name=["--cortex-name", "-n"])
    ] = None,
):
    """Index a cortex."""
    if not cortex_id and not cortex_name:
        raise cyclopts.CycloptsError("Either cortex_id or cortex_name must be provided")
    rest_client = get_rest_client()
    try:
        response = rest_client.index_cortex(cortex_id, cortex_name)
    except SynapsoRestClientError as e:
        print(f"Synapso REST client error: {e}")
        raise cyclopts.CycloptsError(f"Synapso REST client error: {e}")
    except Exception as e:
        print(f"Error: {e}")
        raise cyclopts.CycloptsError(f"Error: {e}")
    print(response)
    identifier = cortex_id or cortex_name
    print(f"Cortex {identifier} indexed successfully")


@cortex_app.command(name="list")
def cmd_cortex_list():
    rest_client = get_rest_client()
    try:
        response = rest_client.get_cortex_list()
    except SynapsoRestClientError as e:
        print(f"Synapso REST client error: {e}")
        raise cyclopts.CycloptsError(f"Synapso REST client error: {e}")
    except Exception as e:
        print(f"Error: {e}")
        raise cyclopts.CycloptsError(f"Error: {e}")
    print(_format_cortex_list(response))


def _format_cortex_list(cortex_list_response: Dict[str, Any]) -> str:
    cortex_list: List[Dict[str, Any]] = cortex_list_response["cortices"]
    if not cortex_list:
        return "No cortexes found"
    msg = "Cortex ID\tCortex Name\tCortex Path\n"
    for cortex in cortex_list:
        msg += f"{cortex['id']}\t{cortex['name']}\t{cortex['path']}\n"  # noqa: E501
    return msg
