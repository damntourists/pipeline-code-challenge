from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from assets.db.models import Asset, AssetVersion
from ..db.models.types import Department, AssetStatus, AssetType

class AssetRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, id_: int) -> Optional[Asset]:
        return self.session.get(Asset, id_)

    def get_next_version_number(self, asset_id: int, dept: Department) -> int:
        version_max = self.session.query(
            func.max(AssetVersion.version)
        ).filter(
            AssetVersion.asset_id == asset_id,
            AssetVersion.department == dept,
        ).scalar()

        return (version_max or 0) + 1

    def create_asset(self, name: str, asset_type: AssetType, dept: Department) -> Asset:
        asset = Asset(name=name, type=asset_type)

        self.session.add(asset)
        self.session.flush()

        version = AssetVersion(
            asset_id=asset.id,
            version=1,
            department=dept,
            status=AssetStatus.ACTIVE,
        )

        self.session.add(version)
        self.session.commit()

        return asset

    def create_version(self, asset_id: int, dept: Department) -> AssetVersion:
        version_next = self.get_next_version_number(asset_id, dept)

        version = AssetVersion(
            asset_id=asset_id,
            version=version_next,
            department=dept,
            status=AssetStatus.ACTIVE,
        )

        self.session.add(version)
        self.session.commit()

        return version

