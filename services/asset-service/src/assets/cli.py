"""
Command-line interface for the Asset Service.
"""

import click

from assets.core.exceptions import BaseAssetException
from assets.core.repository import AssetRepository
from assets.core.service import AssetService
from assets.db.connection import SessionLocal
from assets.db.models.types import AssetType, Department, AssetStatus
from assets.scripts.data_loader import load_from_json


def _parse_asset_type(value: str) -> AssetType:
    try:
        return AssetType(value)
    except ValueError as exc:
        raise click.BadParameter(
            f"Invalid asset type '{value}'. Valid values: "
            f"{', '.join(item.value for item in AssetType)}"
        ) from exc

def _parse_department(value: str) -> Department:
    try:
        return Department(value)
    except ValueError as exc:
        raise click.BadParameter(
            f"Invalid department '{value}'. Valid values: "
            f"{', '.join(item.value for item in Department)}"
        ) from exc

def _parse_status(value: str) -> AssetStatus:
    try:
        return AssetStatus(value)
    except ValueError as exc:
        raise click.BadParameter(
            f"Invalid status '{value}'. Valid values: "
            f"{', '.join(item.value for item in AssetStatus)}"
        ) from exc

def _format_asset(asset) -> str:
    return (
        f"name={asset.name}, "
        f"type={asset.type.value}, "
        f"versions={len(asset.versions)}"
    )

def _format_version(asset_version) -> str:
    return (
        f"asset={asset_version.asset.name}, "
        f"type={asset_version.asset.type.value}, "
        f"department={asset_version.department.value}, "
        f"version={asset_version.version}, "
        f"status={asset_version.status.value}"
    )

@click.group()
@click.pass_context
def cli(ctx):
    """Asset Validation & Registration Service CLI"""
    ctx.ensure_object(dict)
    session = SessionLocal()
    repo = AssetRepository(session)
    ctx.obj["session"] = session
    ctx.obj["service"] = AssetService(repo)


@cli.result_callback()
@click.pass_context
def close_session(ctx, _result, **_kwargs):
    session = ctx.obj.get("session")
    if session is not None:
        session.close()


@cli.command()
@click.argument("file_path", type=click.Path(exists=True))
@click.pass_context
def load(ctx, file_path):
    """Load assets from a JSON file."""
    _service = ctx.obj["service"]
    try:
        load_from_json(_service, file_path)
        click.echo(f"Loaded assets from {file_path}")
    except BaseAssetException as exc:
        raise click.ClickException(str(exc)) from exc


@cli.command()
@click.argument("asset_name")
@click.argument("asset_type")
@click.argument("department")
@click.pass_context
def add(ctx, asset_name, asset_type, department):
    """Add an asset and its initial version."""
    _service = ctx.obj["service"]

    parsed_asset_type = _parse_asset_type(asset_type)
    parsed_department = _parse_department(department)

    try:
        asset = _service.create_new_asset(
            asset_name,
            parsed_asset_type,
            parsed_department,
        )
        click.echo(f"Created asset: {_format_asset(asset)}")
    except BaseAssetException as exc:
        raise click.ClickException(str(exc)) from exc


@cli.command()
@click.argument("asset_name")
@click.argument("asset_type")
@click.pass_context
def get(ctx, asset_name, asset_type):
    """Get an asset by name and type."""
    _service = ctx.obj["service"]
    parsed_asset_type = _parse_asset_type(asset_type)

    try:
        asset = _service.get_asset(asset_name, parsed_asset_type)
        if asset is None:
            raise click.ClickException(
                f"Asset '{asset_name}' with type '{parsed_asset_type.value}' "
                f"not found"
            )
        click.echo(_format_asset(asset))
    except BaseAssetException as exc:
        raise click.ClickException(str(exc)) from exc


@cli.command(name="list")
@click.option(
    "--asset-name",
    "asset_name",
    required=False,
    default=None,
    help="Filter by asset name",
)
@click.option(
    "--asset-type",
    "asset_type",
    required=False,
    default=None,
    help="Filter by asset type",
)
@click.pass_context
def list_cmd(ctx, asset_name, asset_type):
    """List all assets."""
    _service = ctx.obj["service"]
    parsed_asset_type = _parse_asset_type(asset_type) if asset_type else None

    try:
        assets = _service.get_assets(asset_name, parsed_asset_type)
        for asset in assets:
            click.echo(_format_asset(asset))
    except BaseAssetException as exc:
        raise click.ClickException(str(exc)) from exc


@cli.group()
def versions():
    """CLI group to manage asset version subcommands"""
    pass


@versions.command("add")
@click.argument("asset_name")
@click.argument("asset_type")
@click.argument("department")
@click.argument("version_num", type=int)
@click.argument("status")
@click.pass_context
def versions_add(ctx, asset_name, asset_type, department, version_num, status):
    """Add an asset version."""
    _service = ctx.obj["service"]

    parsed_asset_type = _parse_asset_type(asset_type)
    parsed_department = _parse_department(department)
    parsed_status = _parse_status(status)

    try:
        asset_version = _service.add_version(
            name=asset_name,
            asset_type=parsed_asset_type,
            dept=parsed_department,
            version=version_num,
            status=parsed_status,
        )
        click.echo(f"Created version: {_format_version(asset_version)}")
    except BaseAssetException as exc:
        raise click.ClickException(str(exc)) from exc


@versions.command("get")
@click.argument("asset_name")
@click.argument("asset_type")
@click.argument("department")
@click.argument("version_num", type=int)
@click.pass_context
def versions_get(ctx, asset_name, asset_type, department, version_num):
    """Get a specific asset version."""
    _service = ctx.obj["service"]

    parsed_asset_type = _parse_asset_type(asset_type)
    parsed_department = _parse_department(department)

    try:
        asset_version = _service.get_version(
            asset_name,
            parsed_asset_type,
            parsed_department,
            version_num,
        )
        click.echo(_format_version(asset_version))
    except BaseAssetException as exc:
        raise click.ClickException(str(exc)) from exc


@versions.command("list")
@click.argument("asset_name")
@click.argument("asset_type")
@click.option("--department", required=False, default=None,
              help="Filter by department")
@click.option("--status", required=False, default=None,
              help="Filter by status")
@click.option("--version", required=False, default=None, type=int,
              help="Filter by version")
@click.pass_context
def versions_list(ctx, asset_name, asset_type, department, status, version):
    """List all versions of an asset."""
    _service = ctx.obj["service"]

    parsed_asset_type = _parse_asset_type(asset_type)
    parsed_department = _parse_department(department) if department else None
    parsed_status = _parse_status(status) if status else None

    try:
        asset_versions = _service.get_versions(
            name=asset_name,
            asset_type=parsed_asset_type,
            dept=parsed_department,
            status=parsed_status,
            version=version,
        )
        for asset_version in asset_versions:
            click.echo(_format_version(asset_version))
    except BaseAssetException as exc:
        raise click.ClickException(str(exc)) from exc


def main():
    """Entry point for the CLI."""
    cli(obj={})


if __name__ == "__main__":
    main()