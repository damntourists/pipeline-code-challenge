import pytest

from assets.core.exceptions import ValidationError
from assets.core.repository import AssetRepository
from assets.core.service import AssetService
from assets.db.models.types import AssetStatus, Department, AssetType


def test_version_sequence_validation_failure(db_session):
    """Test that version sequence validation fails when jumping a version"""
    repo = AssetRepository(db_session)
    service = AssetService(repo)

    # Create an asset v1
    asset = service.create_new_asset(
        "Hero",
        asset_type=AssetType.CHARACTER,
        dept=Department.MODELING,
    )

    with pytest.raises(ValidationError):
        # Attempt to create v3 before v2
        service.add_version(name=asset.name,
                            asset_type=AssetType.CHARACTER,
                            dept=Department.MODELING, version=3,
                            status=AssetStatus.ACTIVE)
