import json

from marshmallow import ValidationError as MarshmallowValidationError

from asset_common.logging_utils import setup_logger

from assets.core.service import AssetService
from assets.core.validation.schema import AssetSchema, AssetVersionSchema
from assets.db.models.types import AssetType, Department, AssetStatus

log = setup_logger("json-loader")

def load_from_json(service: AssetService, json_path: str) -> None:
    asset_schema = AssetSchema()
    asset_version_schema = AssetVersionSchema()

    with open(json_path, "r") as f:
        data = json.load(f)

    for index, item in enumerate(data, start=1):
        log.info(f"Processing record {index}: {item}")

        asset_data = item.get("asset", {})
        version_data = {
            "department": item.get("department"),
            "version": item.get("version"),
            "status": item.get("status"),
        }

        try:
            validated_asset = asset_schema.load(asset_data)
            validated_version = asset_version_schema.load(version_data)
        except MarshmallowValidationError as exc:
            log.error(f"Skipping invalid record {index}: {exc.messages}")
            continue

        asset_type = AssetType(validated_asset["type"])
        dept = Department(validated_version["department"])
        status = AssetStatus(validated_version["status"])
        name = validated_asset["name"]
        version = validated_version["version"]

        existing = service.get_asset(name, asset_type)

        if not existing:
            try:
                asset = service.create_new_asset(name, asset_type, dept)

                if version > 1:
                    service.add_version(
                        name=asset.name,
                        asset_type=asset_type,
                        dept=dept,
                        version=version,
                        status=status,
                    )
            except Exception as exc:
                log.error(f"Skipping record {index}: could not create "
                          f"asset '{name}': {exc}")
        else:
            try:
                service.create_version(
                    asset_id=existing.id,
                    dept=dept,
                    version=version,
                    status=status,
                )
            except Exception as exc:
                log.error(
                    f"Skipping record {index}: could not create version for "
                    f"asset '{name}': {exc}"
                )

