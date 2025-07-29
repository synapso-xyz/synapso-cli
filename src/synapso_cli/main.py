import typer

from .commands import init_synapso

app = typer.Typer()


@app.command()
def init():
    init_synapso()


if __name__ == "__main__":
    app()
