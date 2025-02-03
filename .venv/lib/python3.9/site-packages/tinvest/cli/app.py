import typer

from .. import __api_version__, __version__
from .openapi import openapi

app = typer.Typer()
app.add_typer(openapi, name='openapi', help='CLI for invest-openapi')


def version_callback(value: bool) -> None:
    if value:
        typer.echo(f'tinvest {__version__}')
        typer.echo(f'invest-openapi {__api_version__}')
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(  # noqa:B008 pylint:disable=unused-argument
        None,
        '--version',
        callback=version_callback,
        is_eager=True,
        help='Application version',
    ),
):
    return
