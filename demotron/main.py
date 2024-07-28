"""
This CLI tool is designed to interact with Google BigQuery
to manage and manipulate raw event data for live demos.
It provides commands to append generated fake data to a specified BigQuery table
and to rename columns in an existing BigQuery table.
The tool uses service account credentials saved in an environment variable for authentication with Google Cloud services.
"""

import sys
from pathlib import Path

# Add the project root to the Python path
project_root = str(Path(__file__).resolve().parent.parent)
sys.path.insert(0, project_root)

import typer
from typing_extensions import Annotated
from google.oauth2 import service_account
from demotron.rename_column_util import rename_column_util
from demotron.load_raw_events import RawEventLoader
from datetime import datetime
from demotron.config import get_service_account_info
from demotron import __version__

app = typer.Typer(
    help="demotron: CLI to delight real people with live demos",
    no_args_is_help=True,
)


def version_callback(value: bool):
    if value:
        typer.echo(f"demotron version: {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: Annotated[
        bool,
        typer.Option(
            "--version",
            callback=version_callback,
            is_eager=True,
            help="Show the version and exit.",
        ),
    ] = False,
):
    """
    CLI to delight real people with live demos.
    """


@app.command()
def rename_column(
    project_name: str = typer.Option(
        "sqlmesh-public-demo", help="The Google Cloud project name."
    ),
    dataset_name: str = typer.Option(
        "tcloud_raw_data", help="The BigQuery dataset name."
    ),
    table_name: str = typer.Option("raw_events", help="The BigQuery table name."),
    old: str = typer.Option(
        "named_events", help="The name of the column to be renamed."
    ),
    new: str = typer.Option("event_name", help="The new name for the column."),
):
    """
    Rename a column in a BigQuery table to create an error OR fix for a raw table
    """
    # Get the service account info securely
    service_account_info = get_service_account_info()

    # Create credentials object
    credentials = service_account.Credentials.from_service_account_info(
        service_account_info
    )

    # Call the rename_column_util with credentials
    rename_column_util(
        credentials=credentials,
        project_name=project_name,
        dataset_name=dataset_name,
        table_name=table_name,
        column_to_rename=old,
        new_column_name=new,
    )


@app.command()
def append_rawdata(
    table_name: str = typer.Option(
        "tcloud_raw_data.raw_events",
        help="The fully qualified BigQuery table name (dataset.table).",
    ),
    num_rows: int = typer.Option(20, help="The number of rows to append.", min=1),
    end_date: str = typer.Option(
        datetime.today().strftime("%Y-%m-%d"),
        help="End date in YYYY-MM-DD format. Defaults to today's date.",
    ),
    project_id: str = typer.Option(
        "sqlmesh-public-demo", help="The Google Cloud project ID."
    ),
):
    """
    Append raw data to a BigQuery table intended to impact the incremental_events.sql model
    """
    service_account_info = get_service_account_info()
    credentials = service_account.Credentials.from_service_account_info(
        service_account_info
    )

    loader = RawEventLoader(credentials, project_id)
    loader.append_to_bigquery_table(table_name, num_rows, end_date)


if __name__ == "__main__":
    app()
