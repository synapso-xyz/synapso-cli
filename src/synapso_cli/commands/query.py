import cyclopts

from ..rest_client import SynapsoRestClientError
from .server import get_rest_client


def cmd_query(query: str):
    """Execute a query against a cortex."""
    rest_client = get_rest_client()
    try:
        response = rest_client.query(query)
        print(response)
    except SynapsoRestClientError as e:
        print(f"Synapso REST client error: {e}")
        raise cyclopts.CycloptsError(f"Synapso REST client error: {e}")
    except Exception as e:
        print(f"Error: {e}")
        raise cyclopts.CycloptsError(f"Error: {e}")


def cmd_query_stream(query: str):
    """Execute a query against a cortex and stream the results."""
    rest_client = get_rest_client()
    try:
        for chunk in rest_client.query_stream(query):
            print(chunk, end="", flush=True)
    except SynapsoRestClientError as e:
        print(f"Synapso REST client error: {e}")
        raise cyclopts.CycloptsError(f"Synapso REST client error: {e}")
    except Exception as e:
        print(f"Error: {e}")
        raise cyclopts.CycloptsError(f"Error: {e}")
