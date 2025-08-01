import typer
from synapso_core.cortex_manager import CortexManager


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
