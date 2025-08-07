import json
import socket
import subprocess
import time
from pathlib import Path

import cyclopts
import psutil
import requests

from ..rest_client import SynapsoRestClient

server_app = cyclopts.App()

CONFIG_PATH = Path.home() / ".synapso" / "api.conf"
CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)

SERVER_LOG_PATH = Path.home() / ".synapso" / "server.log"
SERVER_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)


def get_rest_client():
    """Get a rest client for the server."""
    ensure_server()
    server_config = get_server_config()
    if not server_config:
        raise cyclopts.CycloptsError("Server is not running")
    return SynapsoRestClient(f"http://127.0.0.1:{server_config['port']}")


def get_available_port(preferred_port=50000):
    """Get an available port."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(("localhost", preferred_port))
            return preferred_port
        except OSError:
            s.bind(("", 0))
            return s.getsockname()[1]


def launch_server(preferred_port=50000, timeout=300):
    """Launch the server."""
    port = get_available_port(preferred_port)

    log_file = SERVER_LOG_PATH.open("w")
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
            stdout=log_file,
            stderr=subprocess.STDOUT,
        )
    except FileNotFoundError as e:
        log_file.close()
        raise RuntimeError(
            "uvicorn is not installed. Please install it with 'pip install uvicorn'"
        ) from e
    except Exception as e:
        raise RuntimeError(f"Failed to launch server: {e}") from e

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
    raise RuntimeError(f"Server failed to start within {timeout} seconds.") from None


def is_server_running():
    """Check if the server is running."""
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
    """Ensure the server is running."""
    if is_server_running():
        print("Server already running.")
        return

    config = launch_server()
    print(f"Server started on port {config['port']} (pid {config['pid']})")


def get_server_config():
    """Get the server config."""
    if not CONFIG_PATH.exists():
        return None

    with open(CONFIG_PATH, encoding="utf-8") as f:
        return json.load(f)


@server_app.command()
def start():
    """Start the server."""
    ensure_server()


@server_app.command()
def stop():
    """Stop the server."""
    if not CONFIG_PATH.exists():
        print("Server not running.")
        return

    try:
        with open(CONFIG_PATH, encoding="utf-8") as f:
            config = json.load(f)
        pid = config.get("pid")
        if not pid:
            print("Server not running.")
            return

        p = psutil.Process(pid)
        p.terminate()
        try:
            p.wait(timeout=10)
        except psutil.TimeoutExpired:
            p.kill()
            p.wait()
        CONFIG_PATH.unlink()
        print("Server stopped.")
    except psutil.NoSuchProcess:
        CONFIG_PATH.unlink()
        print("Server not running (stale config cleaned up)")
    except Exception as e:
        print(f"Error stopping server: {e}")
        raise cyclopts.CycloptsError(f"Error stopping server: {e}")


@server_app.command()
def status():
    if is_server_running():
        server_config = get_server_config()
        if not server_config:
            print("Server is running but config is not found.")
        else:
            print(
                f"Server is running on port {server_config['port']} (pid {server_config['pid']})"
            )
    else:
        print("Server is not running.")


@server_app.command()
def restart():
    stop()
    start()
