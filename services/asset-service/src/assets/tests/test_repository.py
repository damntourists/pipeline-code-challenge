
import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from assets.core.repository import AssetRepository
from assets.db.models import AssetVersion
from assets.db.models.types import AssetType, Department, AssetStatus



def test_create_asset_creates_version_1(db_session: Session):
    repo = AssetRepository(db_session)

    asset = repo.create_asset(
        "CharTest",
        asset_type=AssetType.CHARACTER,
        dept=Department.MODELING,
    )

    assert asset.id is not None
    assert len(asset.versions) == 1
    assert asset.versions[0].version == 1
    assert asset.versions[0].asset.name == "CharTest"
    assert asset.versions[0].asset.type == AssetType.CHARACTER
    assert asset.versions[0].department == Department.MODELING


def test_create_version_increment_automatically(db_session: Session):
    repo = AssetRepository(db_session)

    asset = repo.create_asset(
        "CharTest",
        asset_type=AssetType.CHARACTER,
        dept=Department.MODELING,
    )

    v2 = repo.create_version(asset.id, dept=Department.MODELING)
    v3 = repo.create_version(asset.id, dept=Department.MODELING)

    assert v2.version == 2
    assert v3.version == 3


def test_get_by_id_returns_none_for_nonexistent_id(db_session: Session):
    repo = AssetRepository(db_session)
    asset = repo.get_by_id(12345)
    assert asset is None

def test_get_next_version_number_returns_next_version(db_session: Session):
    repo = AssetRepository(db_session)
    asset = repo.create_asset(
        "CharTest",
        asset_type=AssetType.CHARACTER,
        dept=Department.MODELING,
    )
    assert repo.get_next_version_number(asset.id, Department.MODELING) == 2

def test_duplicate_asset_name_and_type_raises_error(db_session: Session):
    repo = AssetRepository(db_session)

    repo.create_asset(
        "CharTest",
        asset_type=AssetType.CHARACTER,
        dept=Department.MODELING,
    )

    # Should raise IntegrityError since we cannot have duplicate name+type
    with pytest.raises(IntegrityError):
        repo.create_asset(
            "CharTest",
            asset_type=AssetType.CHARACTER,
            dept=Department.MODELING,
        )

def test_create_version_for_nonexistent_asset_raises_error(db_session: Session):
    repo = AssetRepository(db_session)

    # Should raise IntegrityError since asset_id does not exist
    with pytest.raises(IntegrityError):
        repo.create_version(12345, dept=Department.MODELING)


def test_unique_asset_constraint_raises_error(db_session: Session):
    repo = AssetRepository(db_session)

    repo.create_asset(
        "CharTest",
        asset_type=AssetType.CHARACTER,
        dept=Department.MODELING,
    )


    # Should raise IntegrityError since we cannot have duplicate name+type for
    # different department
    with pytest.raises(IntegrityError):
        repo.create_asset(
            "CharTest",
            asset_type=AssetType.CHARACTER,
            dept=Department.ANIMATION,
        )
        db_session.flush()

def test_unique_asset_version_constraint_raises_error(db_session: Session):
    repo = AssetRepository(db_session)

    asset = repo.create_asset(
        "CharTest",
        asset_type=AssetType.CHARACTER,
        dept=Department.MODELING,
    )

    duplicate = AssetVersion(
        asset_id=asset.id,
        version=1,
        department=Department.MODELING,
        status=AssetStatus.ACTIVE,
    )

    db_session.add(duplicate)

    # Should raise IntegrityError since we cannot have duplicate asset_id+version
    with pytest.raises(IntegrityError):
        db_session.flush()


def test_version_increments_across_departments(db_session: Session):
    repo = AssetRepository(db_session)

    char_model_asset = repo.create_asset(
        "CharTest",
        asset_type=AssetType.CHARACTER,
        dept=Department.MODELING,
    )

    char_model_asset_v2 = repo.create_version(
        char_model_asset.id,
        dept=Department.MODELING,
    )

    assert char_model_asset_v2.version == 2

    char_anim_asset = repo.create_version(
        char_model_asset.id,
        dept=Department.ANIMATION,
    )

    assert char_anim_asset.version == 1
