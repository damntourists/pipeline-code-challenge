import json

from assets.core.repository import AssetRepository
from assets.core.service import AssetService
from assets.db.models.types import AssetType, Department, AssetStatus

from sqlalchemy.orm import Session

def load_from_json(session: Session, json_path: str) -> None:
    repo = AssetRepository(session)
    service = AssetService(repo)

    with open(json_path, "r") as f:
        data = json.load(f)

    for item in data:
        print(f"Processing {item}")
        asset_type = AssetType(item["asset"]["type"])
        dept = Department(item["department"])
        status = AssetStatus(item["status"])
        name = item["asset"]["name"]
        version = item["version"]

        # check if asset already exists
        existing = repo.get_by_name_and_type(name, asset_type)
        if not existing:
            asset = service.create_new_asset(name, asset_type, dept)

            if version > 1:
                repo.create_version(asset.id, dept, version, status)
        else:
            try:
                repo.create_version(
                    asset_id=existing.id,
                    dept=dept,
                    version=version,
                    status=status,
                )
            except Exception:
                print(f"Asset {name} already exists")

        session.commit()
