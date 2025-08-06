import json
import socket
import subprocess
import time
from pathlib import Path

import psutil
import requests
import typer

from ..rest_client import SynapsoRestClient

server_app = typer.Typer()

CONFIG_PATH = Path.home() / ".synapso" / "api.conf"
CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)


def get_rest_client():
    ensure_server()
    server_config = get_server_config()
    if not server_config:
        raise typer.BadParameter("Server is not running")
    return SynapsoRestClient(f"http://127.0.0.1:{server_config['port']}")


def get_available_port(preferred_port=50000):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(("localhost", preferred_port))
            return preferred_port
        except OSError:
            s.bind(("", 0))
            return s.getsockname()[1]


def launch_server(preferred_port=50000, timeout=300):
    port = get_available_port(preferred_port)
    SERVER_LOG_PATH = Path.home() / ".synapso" / "server.log"
    SERVER_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    try:
        process = subprocess.Popen(
            [
                "uvicorn",
                "synapso_api.main:synapso_api",
                "--host",
                "127.0.0.1",
                "--port",
                str(port),
            ],
            stdout=SERVER_LOG_PATH.open("w"),
            stderr=SERVER_LOG_PATH.open("w"),
        )
    except FileNotFoundError:
        raise RuntimeError(
            "uvicorn is not installed. Please install it with 'pip install uvicorn'"
        )
    except Exception as e:
        raise RuntimeError(f"Failed to launch server: {e}")

    # Wait for healthcheck
    url = f"http://127.0.0.1:{port}/"
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(url, timeout=1)
            if (
                response.status_code == 200
                and response.json().get("message") == "Synapso API is running"
            ):
                # Success — write config
                config = {"pid": process.pid, "port": port}
                CONFIG_PATH.write_text(json.dumps(config))
                return config
        except requests.RequestException:
            pass
        time.sleep(0.3)

    # Timed out — kill process
    process.kill()
    raise RuntimeError(f"Server failed to start within {timeout} seconds.")


def is_server_running():
    if not CONFIG_PATH.exists():
        return False

    try:
        with open(CONFIG_PATH, encoding="utf-8") as f:
            config = json.load(f)
        pid = config.get("pid")
        port = config.get("port")

        if not pid or not port:
            return False

        response = requests.get(f"http://127.0.0.1:{port}/", timeout=1)
        if (
            response.status_code == 200
            and response.json().get("message") == "Synapso API is running"
        ):
            return True
    except Exception:
        return False

    return False


def ensure_server():
    if is_server_running():
        typer.echo("Server already running.")
        return

    config = launch_server()
    typer.echo(f"Server started on port {config['port']} (pid {config['pid']})")


def get_server_config():
    if not CONFIG_PATH.exists():
        return None

    with open(CONFIG_PATH, encoding="utf-8") as f:
        return json.load(f)


@server_app.command()
def start():
    ensure_server()


@server_app.command()
def stop():
    if not CONFIG_PATH.exists():
        typer.echo("Server not running.")
        return

    try:
        with open(CONFIG_PATH, encoding="utf-8") as f:
            config = json.load(f)
        pid = config.get("pid")
        if not pid:
            typer.echo("Server not running.")
            return

        p = psutil.Process(pid)
        p.terminate()
        try:
            p.wait(timeout=10)
        except psutil.TimeoutExpired:
            p.kill()
            p.wait()
        CONFIG_PATH.unlink()
        typer.echo("Server stopped.")
    except psutil.NoSuchProcess:
        CONFIG_PATH.unlink()
        typer.echo("Server not running (stale config cleaned up)")
    except Exception as e:
        typer.echo(f"Error stopping server: {e}", err=True)
        raise typer.Exit(1)


@server_app.command()
def status():
    if is_server_running():
        server_config = get_server_config()
        if not server_config:
            typer.echo("Server is running but config is not found.")
        else:
            typer.echo(
                f"Server is running on port {server_config['port']} (pid {server_config['pid']})"
            )
    else:
        typer.echo("Server is not running.")


@server_app.command()
def restart():
    stop()
    start()
