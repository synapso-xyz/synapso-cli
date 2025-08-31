import json
from typing import Any, Dict

import cyclopts

from ..rest_client import SynapsoRestClientError
from .server import get_rest_client

job_app = cyclopts.App()


@job_app.command(name="list")
def list_jobs():
    rest_client = get_rest_client()
    try:
        response = rest_client.get_job_list()
        print(_format_job_list(response))
    except SynapsoRestClientError as e:
        print(f"Synapso REST client error: {e}")
        raise cyclopts.CycloptsError(f"Synapso REST client error: {e}")
    except Exception as e:
        print(f"Error: {e}")
        raise cyclopts.CycloptsError(f"Error: {e}")


def _format_job_list(job_list_response: Dict[str, Any]) -> str:
    return json.dumps(job_list_response, indent=2)


@job_app.command(name="status")
def get_job_status(job_id: str):
    rest_client = get_rest_client()
    try:
        response = rest_client.get_job(job_id)
        print(response)
    except SynapsoRestClientError as e:
        print(f"Synapso REST client error: {e}")
        raise cyclopts.CycloptsError(f"Synapso REST client error: {e}")
    except Exception as e:
        print(f"Error: {e}")
        raise cyclopts.CycloptsError(f"Error: {e}")
