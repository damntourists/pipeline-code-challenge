from typing import Optional

from sqlalchemy import func, and_
from sqlalchemy.orm import Session

from assets.db.models import Asset, AssetVersion
from assets.db.models.types import Department, AssetStatus, AssetType

class AssetRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, id_: int) -> Optional[Asset]:
        return self.session.get(Asset, id_)

    def get_by_name_and_type(self, name: str, asset_type: AssetType) -> Optional[Asset]:
        return self.session.query(Asset).filter(
            and_(
                Asset.name == name,
                Asset.type == asset_type,
            )
        ).one_or_none()

    def get_all_assets(self) -> list[type[Asset]]:
        return self.session.query(Asset).all()

    def get_all_versions(self) -> list[type[AssetVersion]]:
        return self.session.query(AssetVersion).all()

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

    def create_version(self, asset_id: int, dept: Department,
                       version: Optional[int] = None,
                       status: AssetStatus = AssetStatus.ACTIVE) -> AssetVersion:

        if version is None:
            version_next = self.get_next_version_number(asset_id, dept)
        else:
            version_next = version

        version = AssetVersion(
            asset_id=asset_id,
            version=version_next,
            department=dept,
            status=status,
        )

        self.session.add(version)
        self.session.commit()

        return version

    def add_version(self, name: str, asset_type: AssetType,
                    dept: Department, version: int,
                    status: AssetStatus) -> Optional[AssetVersion]:

        asset = self.get_by_name_and_type(name, asset_type)

        if asset is None:
            raise Exception("Asset not found")

        return self.create_version(asset.id, dept, version, status=status)

    def get_version(self, name: str, asset_type: AssetType,
                    dept: Department, version: int) -> Optional[AssetVersion]:
        return self.session.query(AssetVersion).join(Asset).filter(
            Asset.name == name,
            Asset.type == asset_type,
            AssetVersion.department == dept,
            AssetVersion.version == version,
        ).one_or_none()
