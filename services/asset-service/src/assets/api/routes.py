from pathlib import Path
from typing import Optional

from flask import Blueprint, jsonify, request, Response, g

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


@bp.before_app_request
def log_request_started() -> None:
    """
    Logs the start of a request with details like path, method, and query parameters.
    """
    g.request_path = request.path
    g.request_method = request.method
    log.info(
        "Request started",
        extra={
            "path": request.path,
            "method": request.method,
            "query": request.query_string.decode(
                "utf-8",
                errors="ignore",
            ),
        },
    )


@bp.after_app_request
def log_request_finished(response: Response) -> Response:
    """
    Logs the end of a request with details like path, method, and status code.
    """
    log.info(
        "Request completed",
        extra={
            "path": getattr(g, "request_path", request.path),
            "method": getattr(g, "request_method", request.method),
            "status_code": response.status_code,
        },
    )
    return response


def _get_service() -> tuple:
    """
    Retrieves the database session and asset service.
    """
    session = SessionLocal()
    repo = AssetRepository(session)
    service = AssetService(repo)
    log.info("Database session opened")
    return session, service


def _close_session(session) -> None:
    """
    Closes the database session and logs the action.
    """
    session.close()
    log.info("Database session closed")


def _parse_asset_type(value: Optional[str]) -> AssetType | None:
    """
    Parses the asset type from a string.
    """
    if value is None:
        return None
    return AssetType(value)


def _parse_department(value: Optional[str]) -> Department | None:
    """
    Parses the department from a string.
    """
    if value is None:
        return None
    return Department(value)


def _parse_status(value: Optional[str]) -> AssetStatus | None:
    """
    Parses the asset status from a string.
    """
    if value is None:
        return None
    return AssetStatus(value)


def _asset_to_dict(asset) -> dict:
    """
    Converts an asset object to a dictionary.
    """
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
    """
    Converts an asset version to a dictionary.
    """
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
    """
    Generates an error response with logging.
    """
    log.error(
        "Request failed",
        extra={
            "status_code": status_code,
            "error_message": message,
            "path": request.path,
            "method": request.method,
        },
    )
    return jsonify({"error": message}), status_code


@bp.route("/health", methods=["GET"])
def health() -> Response:
    """
    Endpoint to check the health of the service.
    """
    log.info("Health check requested")
    return jsonify({"status": "ok"})


@bp.route("/assets/load", methods=["POST"])
def load_assets() -> tuple:
    """
    Endpoint to load assets from a file.
    """
    payload = request.get_json(silent=True) or {}
    file_path = payload.get("file_path")

    log.info(
        "Load assets requested",
        extra={
            "file_path": file_path,
        },
    )

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

        log.info(
            "Starting asset load from file",
            extra={
                "file_path": str(resolved_path),
            },
        )

        load_from_json(service, str(resolved_path))

        log.info(
            "Asset load completed",
            extra={
                "file_path": str(resolved_path),
            },
        )

        return jsonify(
            {
                "message": f"Loaded assets from {file_path}",
            }
        ), 200

    except BaseAssetException as exc:
        session.rollback()
        log.warning(
            "Asset load failed with business exception",
            extra={
                "file_path": file_path,
                "error": str(exc),
            },
        )
        return _error_response(str(exc), 400)

    except Exception as exc:
        session.rollback()
        log.exception(
            "Unexpected error while loading assets",
            extra={
                "file_path": file_path,
            },
        )
        return _error_response(str(exc), 500)

    finally:
        _close_session(session)


@bp.route("/assets", methods=["POST"])
def create_asset() -> tuple:
    """
    Endpoint to create a new asset.
    """
    payload = request.get_json(silent=True) or {}

    name = payload.get("name")
    asset_type = payload.get("type")
    department = payload.get("department")

    log.info(
        "Create asset requested",
        extra={
            "asset_name": name,
            "asset_type": asset_type,
            "department": department,
        },
    )

    if not name or not asset_type or not department:
        return _error_response(
            "Fields 'name', 'type', and 'department' are required",
            400,
        )

    session, service = _get_service()

    try:
        parsed_asset_type = _parse_asset_type(asset_type)
        parsed_department = _parse_department(department)

        asset = service.create_new_asset(
            name=name,
            asset_type=parsed_asset_type,
            dept=parsed_department,
        )

        log.info(
            "Asset created successfully",
            extra={
                "asset_id": asset.id,
                "asset_name": asset.name,
                "asset_type": asset.type.value,
                "version_count": len(asset.versions),
            },
        )

        return jsonify(_asset_to_dict(asset)), 201

    except ValueError as exc:
        session.rollback()
        log.warning(
            "Create asset rejected due to invalid enum value",
            extra={
                "asset_name": name,
                "asset_type": asset_type,
                "department": department,
                "error": str(exc),
            },
        )
        return _error_response(str(exc), 400)

    except BaseAssetException as exc:
        session.rollback()
        log.warning(
            "Create asset failed with business exception",
            extra={
                "asset_name": name,
                "asset_type": asset_type,
                "department": department,
                "error": str(exc),
            },
        )
        return _error_response(str(exc), 400)

    except Exception as exc:
        session.rollback()
        log.exception(
            "Unexpected error while creating asset",
            extra={
                "asset_name": name,
                "asset_type": asset_type,
                "department": department,
            },
        )
        return _error_response(str(exc), 500)

    finally:
        _close_session(session)


@bp.route("/assets", methods=["GET"])
def get_assets() -> tuple:
    """
    Endpoint to retrieve assets based on query parameters.
    """
    asset_name = request.args.get("asset")
    asset_type_raw = request.args.get("type")

    log.info(
        "Get assets requested",
        extra={
            "asset_name": asset_name,
            "asset_type": asset_type_raw,
        },
    )

    session, service = _get_service()

    try:
        asset_type = _parse_asset_type(asset_type_raw) if asset_type_raw else None

        assets = service.get_assets(asset_name, asset_type)

        log.info(
            "Assets fetched successfully",
            extra={
                "asset_name": asset_name,
                "asset_type": asset_type_raw,
                "count": len(assets),
            },
        )

        return jsonify([_asset_to_dict(asset) for asset in assets]), 200

    except ValueError as exc:
        log.warning(
            "Get assets rejected due to invalid enum value",
            extra={
                "asset_name": asset_name,
                "asset_type": asset_type_raw,
                "error": str(exc),
            },
        )
        return _error_response(str(exc), 400)

    except AssetNotFoundError as exc:
        log.warning(
            "Assets not found",
            extra={
                "asset_name": asset_name,
                "asset_type": asset_type_raw,
                "error": str(exc),
            },
        )
        return _error_response(str(exc), 404)

    except BaseAssetException as exc:
        log.warning(
            "Get assets failed with business exception",
            extra={
                "asset_name": asset_name,
                "asset_type": asset_type_raw,
                "error": str(exc),
            },
        )

        return _error_response(str(exc), 400)

    except Exception as exc:
        log.exception(
            "Unexpected error while fetching assets",
            extra={
                "asset_name": asset_name,
                "asset_type": asset_type_raw,
            },
        )

        return _error_response(str(exc), 500)

    finally:
        _close_session(session)


@bp.route("/assets/versions", methods=["POST"])
def create_asset_version() -> tuple:
    """
    Endpoint to create a new asset version.
    """
    payload = request.get_json(silent=True) or {}

    name = payload.get("name")
    asset_type = payload.get("type")
    department = payload.get("department")
    version = payload.get("version")
    status = payload.get("status", AssetStatus.ACTIVE.value)

    log.info(
        "Create asset version requested",
        extra={
            "asset_name": name,
            "asset_type": asset_type,
            "department": department,
            "version": version,
            "status": status,
        },
    )

    if not name or not asset_type or not department:
        return _error_response(
            "Fields 'name', 'type', and 'department' are required",
            400,
        )

    session, service = _get_service()

    try:
        parsed_asset_type = _parse_asset_type(asset_type)
        parsed_department = _parse_department(department)
        parsed_status = _parse_status(status)

        asset_version = service.add_version(
            name=name,
            asset_type=parsed_asset_type,
            dept=parsed_department,
            version=version,
            status=parsed_status,
        )

        log.info(
            "Asset version created successfully",
            extra={
                "asset_version_id": asset_version.id,
                "asset_name": asset_version.asset.name,
                "asset_type": asset_version.asset.type.value,
                "department": asset_version.department.value,
                "version": asset_version.version,
                "status": asset_version.status.value,
            },
        )

        return jsonify(_asset_version_to_dict(asset_version)), 201

    except ValueError as exc:
        session.rollback()

        log.warning(
            "Create asset version rejected due to invalid enum or value",
            extra={
                "asset_name": name,
                "asset_type": asset_type,
                "department": department,
                "version": version,
                "status": status,
                "error": str(exc),
            },
        )

        return _error_response(str(exc), 400)

    except BaseAssetException as exc:
        session.rollback()

        log.warning(
            "Create asset version failed with business exception",
            extra={
                "asset_name": name,
                "asset_type": asset_type,
                "department": department,
                "version": version,
                "status": status,
                "error": str(exc),
            },
        )

        return _error_response(str(exc), 400)

    except Exception as exc:
        session.rollback()

        log.exception(
            "Unexpected error while creating asset version",
            extra={
                "asset_name": name,
                "asset_type": asset_type,
                "department": department,
                "version": version,
                "status": status,
            },
        )

        return _error_response(str(exc), 500)

    finally:
        _close_session(session)


@bp.route("/assets/versions", methods=["GET"])
def get_asset_versions() -> tuple:
    """
    Endpoint to retrieve asset versions based on query parameters.
    """
    asset_name = request.args.get("asset")
    asset_type_raw = request.args.get("type")
    department_raw = request.args.get("department")
    status_raw = request.args.get("status")
    version_raw = request.args.get("version")

    log.info(
        "Get asset versions requested",
        extra={
            "asset_name": asset_name,
            "asset_type": asset_type_raw,
            "department": department_raw,
            "status": status_raw,
            "version": version_raw,
        },
    )

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

            log.info(
                "Single asset version fetched successfully",
                extra={
                    "asset_name": asset_version.asset.name,
                    "asset_type": asset_version.asset.type.value,
                    "department": asset_version.department.value,
                    "version": asset_version.version,
                    "status": asset_version.status.value,
                },
            )

            return jsonify(_asset_version_to_dict(asset_version)), 200

        versions = service.get_versions(
            name=asset_name,
            asset_type=asset_type,
            dept=department,
            status=status,
            version=version,
        )

        log.info(
            "Asset versions fetched successfully",
            extra={
                "asset_name": asset_name,
                "asset_type": asset_type_raw,
                "department": department_raw,
                "status": status_raw,
                "version": version_raw,
                "count": len(versions),
            },
        )

        return jsonify([_asset_version_to_dict(item) for item in versions]), 200

    except ValueError as exc:
        log.warning(
            "Get asset versions rejected due to invalid enum or value",
            extra={
                "asset_name": asset_name,
                "asset_type": asset_type_raw,
                "department": department_raw,
                "status": status_raw,
                "version": version_raw,
                "error": str(exc),
            },
        )

        return _error_response(str(exc), 400)

    except AssetNotFoundError as exc:
        log.warning(
            "Asset versions not found",
            extra={
                "asset_name": asset_name,
                "asset_type": asset_type_raw,
                "department": department_raw,
                "status": status_raw,
                "version": version_raw,
                "error": str(exc),
            },
        )

        return _error_response(str(exc), 404)

    except BaseAssetException as exc:
        log.warning(
            "Get asset versions failed with business exception",
            extra={
                "asset_name": asset_name,
                "asset_type": asset_type_raw,
                "department": department_raw,
                "status": status_raw,
                "version": version_raw,
                "error": str(exc),
            },
        )

        return _error_response(str(exc), 400)

    except Exception as exc:
        log.exception(
            "Unexpected error while fetching asset versions",
            extra={
                "asset_name": asset_name,
                "asset_type": asset_type_raw,
                "department": department_raw,
                "status": status_raw,
                "version": version_raw,
            },
        )

        return _error_response(str(exc), 500)

    finally:
        _close_session(session)
