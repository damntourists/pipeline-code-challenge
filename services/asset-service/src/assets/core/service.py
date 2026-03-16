from typing import Optional

from sqlalchemy.exc import IntegrityError
from assets.core.repository import AssetRepository
from assets.core.exceptions import (DuplicateAssetError,
                                    AssetNotFoundError)
from assets.core.validation.rules import VersionSequenceValidator
from assets.db.models import Asset, AssetVersion
from assets.db.models.types import AssetType, Department, AssetStatus

class AssetService:
    def __init__(self, repository: AssetRepository):
        self.repo = repository
        self.validator = VersionSequenceValidator()

    def create_new_asset(self, name: str, asset_type: AssetType,
                         dept: Department) -> Asset:
        try:
            return self.repo.create_new_asset(name, asset_type, dept)
        except IntegrityError:
            raise DuplicateAssetError(name, asset_type)

    def add_version(self, name: str, asset_type: AssetType, dept: Department,
                    version: Optional[int] = None,
                    status: AssetStatus = AssetStatus.ACTIVE) -> AssetVersion:
        asset = self.repo.get_by_name_and_type(name=name, asset_type=asset_type)
        if not asset:
            raise AssetNotFoundError(name)

        latest = self.repo.get_next_version_number(asset.id, dept) - 1
        self.validator.validate(latest, version)

        return self.repo.create_version(
            asset_id=asset.id,
            dept=dept,
            version=version,
            status=status,
        )

    def create_version(self, asset_id: int, dept: Department,
                       version: Optional[None] = None,
                       status: AssetStatus = AssetStatus.ACTIVE) -> AssetVersion:
        latest = self.repo.get_next_version_number(asset_id, dept) - 1

        if version is not None:
            self.validator.validate(latest, version)

        return self.repo.create_version(
            asset_id=asset_id,
            dept=dept,
            version=version,
            status=status,
        )

    def get_asset(self, name: str, asset_type: AssetType) -> Asset | None:
        return self.repo.get_by_name_and_type(name=name, asset_type=asset_type)

    def get_assets(self, name: str = None,
                   asset_type: AssetType = None) -> list[type[Asset]]:
        assets = []

        if name is None and asset_type is None:
            assets = self.repo.get_all_assets()

            if not assets:
                raise AssetNotFoundError("No assets found")

        elif name is not None and asset_type is None:
            assets = self.repo.get_all_assets_by_name(name)

            if not assets:
                raise AssetNotFoundError(f"No assets found with name '{name}'")

        elif name is None and asset_type is not None:
            assets = self.repo.get_all_assets_by_type(asset_type)

            if not assets:
                raise AssetNotFoundError(
                    f"No assets found with type '{asset_type}'",
                )
        else:
            asset = self.repo.get_by_name_and_type(
                name=name,
                asset_type=asset_type,
            )

            if asset:
                assets.append(asset)

        if not assets:
            raise AssetNotFoundError(
                f"No assets found with name '{name}' and type '{asset_type}'",
            )

        return assets

    def get_version(self, name: str, asset_type: AssetType, dept: Department,
                    version: int) -> AssetVersion:
        asset_version = self.repo.get_version(name, asset_type, dept, version)
        if not asset_version:
            raise AssetNotFoundError(
                f"No version found for asset '{name}' type '{asset_type.value}' "
                f"department '{dept.value}' version '{version}'"
            )
        return asset_version

    def get_versions(self, name: str, asset_type: AssetType,
                     dept: Optional[Department] = None,
                     status: Optional[AssetStatus] = None,
                     version: Optional[int] = None) -> list[type[AssetVersion]]:
        versions = self.repo.get_all_versions_by_name_and_asset_type(name, asset_type)

        if dept is not None:
            versions = [item for item in versions if item.department == dept]
        if status is not None:
            versions = [item for item in versions if item.status == status]
        if version is not None:
            versions = [item for item in versions if item.version == version]

        if not versions:
            raise AssetNotFoundError(
                f"No versions found for asset '{name}' and type '{asset_type.value}'"
            )

        return versions
