from pathlib import Path
from typing import Optional

from flask import Blueprint, jsonify, request, Response

from assets.core.exceptions import BaseAssetException, AssetNotFoundError
from assets.core.repository import AssetRepository
from assets.core.service import AssetService
from assets.db.connection import SessionLocal
from assets.db.models.types import AssetType, Department, AssetStatus
from assets.scripts.data_loader import load_from_json


from asset_common.logging_utils import setup_logger

log = setup_logger("assets")

bp = Blueprint("assets", __name__)

log.info("Initializing asset service routes", extra={"blueprint": bp})


def _get_service() -> tuple:
    session = SessionLocal()
    repo = AssetRepository(session)
    service = AssetService(repo)
    return session, service


def _parse_asset_type(value: Optional[str]) -> AssetType | None:
    if value is None:
        return None
    return AssetType(value)


def _parse_department(value: Optional[str]) -> Department | None:
    if value is None:
        return None
    return Department(value)


def _parse_status(value: Optional[str]) -> AssetStatus | None:
    if value is None:
        return None
    return AssetStatus(value)


def _asset_to_dict(asset) -> dict:
    return {
        "id": asset.id,
        "name": asset.name,
        "type": asset.type.value,
        "versions": [
            {
                "id": version.id,
                "asset_id": version.asset_id,
                "department": version.department.value,
                "version": version.version,
                "status": version.status.value,
            }
            for version in asset.versions
        ],
    }


def _asset_version_to_dict(asset_version) -> dict:
    return {
        "id": asset_version.id,
        "asset_id": asset_version.asset_id,
        "asset_name": asset_version.asset.name,
        "asset_type": asset_version.asset.type.value,
        "department": asset_version.department.value,
        "version": asset_version.version,
        "status": asset_version.status.value,
    }


def _error_response(message: str, status_code: int) -> tuple:
    log.error(f"{status_code} - {message}")
    return jsonify({"error": message}), status_code


@bp.route("/health", methods=["GET"])
def health() -> Response:
    return jsonify({"status": "ok"})


@bp.route("/assets/load", methods=["POST"])
def load_assets() -> tuple:
    payload = request.get_json(silent=True) or {}
    file_path = payload.get("file_path")

    if not file_path:
        return _error_response(
            "Missing required field 'file_path'",
            400,
        )

    session, service = _get_service()

    try:
        resolved_path = Path(file_path)
        if not resolved_path.exists():
            return _error_response(
                f"File not found: {file_path}",
                404,
            )

        load_from_json(service, str(resolved_path))

        return jsonify(
            {
                "message": f"Loaded assets from {file_path}",
            }
        ), 200

    except BaseAssetException as exc:
        session.rollback()
        return _error_response(str(exc), 400)

    except Exception as exc:
        session.rollback()
        log.exception("Unexpected error while loading assets")
        return _error_response(str(exc), 500)

    finally:
        session.close()


@bp.route("/assets", methods=["POST"])
def create_asset() -> tuple:
    payload = request.get_json(silent=True) or {}

    name = payload.get("name")
    asset_type = payload.get("type")
    department = payload.get("department")

    if not name or not asset_type or not department:
        return _error_response(
            "Fields 'name', 'type', and 'department' are required",
            400,
        )

    session, service = _get_service()

    try:
        asset = service.create_new_asset(
            name=name,
            asset_type=_parse_asset_type(asset_type),
            dept=_parse_department(department),
        )

        return jsonify(_asset_to_dict(asset)), 201

    except ValueError as exc:
        session.rollback()
        return _error_response(str(exc), 400)

    except BaseAssetException as exc:
        session.rollback()
        return _error_response(str(exc), 400)

    except Exception as exc:
        session.rollback()
        log.exception("Unexpected error while creating asset")
        return _error_response(str(exc), 500)

    finally:
        session.close()


@bp.route("/assets", methods=["GET"])
def get_assets() -> tuple:
    asset_name = request.args.get("asset")
    asset_type_raw = request.args.get("type")

    session, service = _get_service()

    try:
        asset_type = _parse_asset_type(
            asset_type_raw,
        ) if asset_type_raw else None

        assets = service.get_assets(asset_name, asset_type)

        return jsonify([_asset_to_dict(asset) for asset in assets]), 200

    except ValueError as exc:
        return _error_response(str(exc), 400)

    except AssetNotFoundError as exc:
        return _error_response(str(exc), 404)

    except BaseAssetException as exc:
        return _error_response(str(exc), 400)

    except Exception as exc:
        log.exception("Unexpected error while fetching assets")
        return _error_response(str(exc), 500)

    finally:
        session.close()


@bp.route("/assets/versions", methods=["POST"])
def create_asset_version() -> tuple:
    payload = request.get_json(silent=True) or {}

    name = payload.get("name")
    asset_type = payload.get("type")
    department = payload.get("department")
    version = payload.get("version")
    status = payload.get("status", AssetStatus.ACTIVE.value)

    if not name or not asset_type or not department:
        return _error_response(
            "Fields 'name', 'type', and 'department' are required",
            400,
        )

    session, service = _get_service()

    try:
        asset_version = service.add_version(
            name=name,
            asset_type=_parse_asset_type(asset_type),
            dept=_parse_department(department),
            version=version,
            status=_parse_status(status),
        )
        return jsonify(_asset_version_to_dict(asset_version)), 201

    except ValueError as exc:
        session.rollback()
        return _error_response(str(exc), 400)

    except BaseAssetException as exc:
        session.rollback()
        return _error_response(str(exc), 400)

    except Exception as exc:
        session.rollback()
        log.exception("Unexpected error while creating asset version")
        return _error_response(str(exc), 500)

    finally:
        session.close()


@bp.route("/assets/versions", methods=["GET"])
def get_asset_versions() -> tuple:
    asset_name = request.args.get("asset")
    asset_type_raw = request.args.get("type")
    department_raw = request.args.get("department")
    status_raw = request.args.get("status")
    version_raw = request.args.get("version")

    if not asset_name or not asset_type_raw:
        return _error_response(
            "Query params 'asset' and 'type' are required",
            400,
        )

    session, service = _get_service()
    try:
        asset_type = _parse_asset_type(asset_type_raw)
        department = _parse_department(
            department_raw,
        ) if department_raw else None
        status = _parse_status(status_raw) if status_raw else None
        version = int(version_raw) if version_raw is not None else None

        if department is not None and version is not None:
            asset_version = service.get_version(
                asset_name,
                asset_type,
                department,
                version,
            )
            return jsonify(_asset_version_to_dict(asset_version)), 200

        versions = service.get_versions(
            name=asset_name,
            asset_type=asset_type,
            dept=department,
            status=status,
            version=version,
        )

        return jsonify([_asset_version_to_dict(item) for item in versions]), 200

    except ValueError as exc:
        return _error_response(str(exc), 400)

    except AssetNotFoundError as exc:
        return _error_response(str(exc), 404)

    except BaseAssetException as exc:
        return _error_response(str(exc), 400)

    except Exception as exc:
        log.exception("Unexpected error while fetching asset versions")
        return _error_response(str(exc), 500)

    finally:
        session.close()
