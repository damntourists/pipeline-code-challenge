
import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from assets.core.repository import AssetRepository
from assets.db.models import AssetVersion
from assets.db.models.types import AssetType, Department, AssetStatus



def test_create_new_asset_creates_version_1(db_session: Session):
    repo = AssetRepository(db_session)

    asset = repo.create_new_asset(
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

    asset = repo.create_new_asset(
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
    asset = repo.create_new_asset(
        "CharTest",
        asset_type=AssetType.CHARACTER,
        dept=Department.MODELING,
    )
    assert repo.get_next_version_number(asset.id, Department.MODELING) == 2

def test_duplicate_asset_name_and_type_raises_error(db_session: Session):
    repo = AssetRepository(db_session)

    repo.create_new_asset(
        "CharTest",
        asset_type=AssetType.CHARACTER,
        dept=Department.MODELING,
    )

    # Should raise IntegrityError since we cannot have duplicate name+type
    with pytest.raises(IntegrityError):
        repo.create_new_asset(
            "CharTest",
            asset_type=AssetType.CHARACTER,
            dept=Department.MODELING,
        )
        db_session.flush()

def test_create_version_for_nonexistent_asset_raises_error(db_session: Session):
    repo = AssetRepository(db_session)

    # Should raise IntegrityError since asset_id does not exist
    with pytest.raises(IntegrityError):
        repo.create_version(12345, dept=Department.MODELING)


def test_unique_asset_constraint_raises_error(db_session: Session):
    repo = AssetRepository(db_session)

    repo.create_new_asset(
        "CharTest",
        asset_type=AssetType.CHARACTER,
        dept=Department.MODELING,
    )

    # Should raise IntegrityError since we cannot have duplicate name+type for
    # different department
    with pytest.raises(IntegrityError):
        repo.create_new_asset(
            "CharTest",
            asset_type=AssetType.CHARACTER,
            dept=Department.ANIMATION,
        )
        db_session.flush()

def test_orphaned_asset_version_raises_error(db_session: Session):
    orphaned_version = AssetVersion(
        asset_id=12345,
        department=Department.MODELING,
        version=1,
    )
    db_session.add(orphaned_version)
    with pytest.raises(IntegrityError):
        db_session.flush()

def test_unique_asset_version_constraint_raises_error(db_session: Session):
    repo = AssetRepository(db_session)

    asset = repo.create_new_asset(
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

    char_model_asset = repo.create_new_asset(
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

def test_get_by_name_and_type(db_session: Session):
    repo = AssetRepository(db_session)
    repo.create_new_asset(
        "CharTest",
        asset_type=AssetType.CHARACTER,
        dept=Department.MODELING,
    )

    asset = repo.get_by_name_and_type("CharTest", AssetType.CHARACTER)
    assert asset is not None
    assert asset.name == "CharTest"
    assert asset.type == AssetType.CHARACTER

    not_found_asset = repo.get_by_name_and_type(
        "NonExistent",
        AssetType.CHARACTER,
    )
    assert not_found_asset is None

def test_get_all_assets(db_session: Session):
    repo = AssetRepository(db_session)

    for i in range(5):
        repo.create_new_asset(
            "CharTest%d" % i,
            asset_type=AssetType.CHARACTER,
            dept=Department.MODELING,
        )

    db_session.flush()

    all_assets = repo.get_all_assets()
    assert len(all_assets) == 5

def test_get_all_versions(db_session: Session):
    repo = AssetRepository(db_session)

    # v1
    asset = repo.create_new_asset(
        "CharTest",
        asset_type=AssetType.CHARACTER,
        dept=Department.MODELING,
    )

    # v2-v6
    for i in range(5):
        repo.create_version(asset.id, dept=Department.MODELING)

    db_session.flush()

    assert len(asset.versions) == 6

def test_version_increment_after_jump(db_session: Session):
    repo = AssetRepository(db_session)
    asset = repo.create_new_asset(
        "CharTest",
        asset_type=AssetType.CHARACTER,
        dept=Department.MODELING,
    )

    repo.create_version(asset.id, dept=Department.MODELING, version=10)

    next_version = repo.create_version(asset.id, dept=Department.MODELING)
    assert next_version.version == 11

def test_version_insert_after_jump(db_session: Session):
    repo = AssetRepository(db_session)

    # v1
    v1 = repo.create_new_asset(
        "CharTest",
        asset_type=AssetType.CHARACTER,
        dept=Department.MODELING,
    )

    # v10
    repo.create_version(v1.id, dept=Department.MODELING, version=10)

    # v2
    v2 = repo.create_version(v1.id, dept=Department.MODELING, version=2)

    assert v2.version == 2
    assert len(v1.versions) == 3

def test_create_version_with_status(db_session: Session):
    repo = AssetRepository(db_session)
    asset = repo.create_new_asset(
        "CharTest",
        asset_type=AssetType.CHARACTER,
        dept=Department.MODELING,
    )

    v2 = repo.create_version(asset.id, dept=Department.MODELING,
                             status=AssetStatus.INACTIVE)

    assert v2.status == AssetStatus.INACTIVE

def test_delete_asset_deletes_versions(db_session: Session):
    repo = AssetRepository(db_session)
    asset = repo.create_new_asset(
        "CharTest",
        asset_type=AssetType.CHARACTER,
        dept=Department.MODELING,
    )
    repo.create_version(asset.id, dept=Department.MODELING)
    db_session.flush()

    db_session.delete(asset)
    db_session.flush()

    versions = db_session.query(AssetVersion).filter_by(asset_id=asset.id).all()
    assert len(versions) == 0

def test_asset_name_is_case_sensitive(db_session: Session):
    repo = AssetRepository(db_session)
    repo.create_new_asset(
        "CharTest",
        asset_type=AssetType.CHARACTER,
        dept=Department.MODELING,
    )

    repo.create_new_asset(
        "chartest",
        asset_type=AssetType.CHARACTER,
        dept=Department.MODELING,
    )

    assert len(repo.get_all_assets()) == 2


def test_non_existent_department_raises_error(db_session: Session):
    with pytest.raises(ValueError):
        Department("non_existent")

def test_non_existent_asset_type_raises_error(db_session: Session):
    with pytest.raises(ValueError):
        AssetType("non_existent")

def test_non_existent_asset_status_raises_error(db_session: Session):
    with pytest.raises(ValueError):
        AssetStatus("non_existent")
