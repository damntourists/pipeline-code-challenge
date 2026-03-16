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
            return self.repo.create_asset(name, asset_type, dept)
        except IntegrityError:
            raise DuplicateAssetError(
                f"Asset with name '{name}' already exists"
            )

    def add_version(self, name: str, asset_type: AssetType,
                    dept: Department, version: int = None,
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

    def get_asset(self, name: str, asset_type: AssetType) -> Optional[Asset]:
        asset = self.repo.get_by_name_and_type(name=name, asset_type=asset_type)
        if not asset:
            raise AssetNotFoundException(
                f"{name} of type {asset_type} not found."
            )
        return asset
