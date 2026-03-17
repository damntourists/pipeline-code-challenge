from pathlib import Path

from assets.db.models.types import AssetType, Department, AssetStatus
from assets.core.repository import AssetRepository


def test_health_endpoint(api_client):
    """Test the health endpoint"""
    response = api_client.get("/health")

    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def test_create_asset(api_client):
    """Test creating a new asset"""
    response = api_client.post(
        "/assets",
        json={
            "name": "hero",
            "type": "character",
            "department": "modeling",
        },
    )

    assert response.status_code == 201
    data = response.get_json()
    assert data["name"] == "hero"
    assert data["type"] == "character"
    assert len(data["versions"]) == 1
    assert data["versions"][0]["department"] == "modeling"
    assert data["versions"][0]["version"] == 1
    assert data["versions"][0]["status"] == "active"


def test_create_asset_missing_required_fields_returns_400(api_client):
    """Test creating a new asset with missing required fields"""
    response = api_client.post(
        "/assets",
        json={
            "name": "hero",
            "type": "character",
        },
    )

    assert response.status_code == 400
    assert "error" in response.get_json()


def test_create_asset_invalid_type_returns_400(api_client):
    """Test creating a new asset with an invalid type"""
    response = api_client.post(
        "/assets",
        json={
            "name": "hero",
            "type": "not-real",
            "department": "modeling",
        },
    )

    assert response.status_code == 400
    assert "error" in response.get_json()


def test_get_assets_returns_all_assets(api_client, db_session):
    """Test getting all assets"""
    repo = AssetRepository(db_session)
    repo.create_new_asset(
        "hero",
        asset_type=AssetType.CHARACTER,
        dept=Department.MODELING,
    )
    repo.create_new_asset(
        "dragon",
        asset_type=AssetType.CHARACTER,
        dept=Department.ANIMATION,
    )

    response = api_client.get("/assets")

    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 2
    names = {item["name"] for item in data}
    assert names == {"hero", "dragon"}


def test_get_assets_filters_by_name_and_type(api_client, db_session):
    """Test getting assets by name and type"""
    repo = AssetRepository(db_session)
    repo.create_new_asset(
        "hero",
        asset_type=AssetType.CHARACTER,
        dept=Department.MODELING,
    )
    repo.create_new_asset(
        "hero",
        asset_type=AssetType.PROP,
        dept=Department.MODELING,
    )

    response = api_client.get("/assets?asset=hero&type=character")

    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 1
    assert data[0]["name"] == "hero"
    assert data[0]["type"] == "character"


def test_get_assets_not_found_returns_404(api_client):
    """Test getting assets that don't exist"""
    response = api_client.get("/assets?asset=missing&type=character")

    assert response.status_code == 404
    assert "error" in response.get_json()


def test_create_asset_version(api_client, db_session):
    """Test creating a new asset version"""
    repo = AssetRepository(db_session)
    repo.create_new_asset(
        "hero",
        asset_type=AssetType.CHARACTER,
        dept=Department.MODELING,
    )

    response = api_client.post(
        "/assets/versions",
        json={
            "name": "hero",
            "type": "character",
            "department": "modeling",
            "version": 2,
            "status": "active",
        },
    )

    assert response.status_code == 201
    data = response.get_json()
    assert data["asset_name"] == "hero"
    assert data["asset_type"] == "character"
    assert data["department"] == "modeling"
    assert data["version"] == 2
    assert data["status"] == "active"


def test_create_asset_version_invalid_status_returns_400(api_client, db_session):
    """Test creating a new asset version with an invalid status"""
    repo = AssetRepository(db_session)
    repo.create_new_asset(
        "hero",
        asset_type=AssetType.CHARACTER,
        dept=Department.MODELING,
    )

    response = api_client.post(
        "/assets/versions",
        json={
            "name": "hero",
            "type": "character",
            "department": "modeling",
            "version": 2,
            "status": "deprecated",
        },
    )

    assert response.status_code == 400
    assert "error" in response.get_json()


def test_get_asset_versions_returns_list(api_client, db_session):
    """Test getting all versions for an asset"""
    repo = AssetRepository(db_session)
    asset = repo.create_new_asset(
        "hero",
        asset_type=AssetType.CHARACTER,
        dept=Department.MODELING,
    )
    repo.create_version(
        asset.id,
        dept=Department.MODELING,
        version=2,
        status=AssetStatus.ACTIVE,
    )

    response = api_client.get("/assets/versions?asset=hero&type=character")

    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 2
    assert data[0]["asset_name"] == "hero"
    assert data[0]["asset_type"] == "character"


def test_get_asset_versions_filters_by_department(api_client, db_session):
    """Test getting versions by department"""
    repo = AssetRepository(db_session)
    asset = repo.create_new_asset(
        "hero",
        asset_type=AssetType.CHARACTER,
        dept=Department.MODELING,
    )
    repo.create_version(
        asset.id,
        dept=Department.ANIMATION,
        version=1,
        status=AssetStatus.ACTIVE,
    )

    response = api_client.get(
        "/assets/versions?asset=hero&type=character&department=animation"
    )

    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 1
    assert data[0]["department"] == "animation"
    assert data[0]["version"] == 1


def test_get_single_asset_version(api_client, db_session):
    """Test getting a single asset version"""
    repo = AssetRepository(db_session)
    asset = repo.create_new_asset(
        "hero",
        asset_type=AssetType.CHARACTER,
        dept=Department.MODELING,
    )
    repo.create_version(
        asset.id,
        dept=Department.MODELING,
        version=2,
        status=AssetStatus.INACTIVE,
    )

    response = api_client.get(
        "/assets/versions?asset=hero&type=character&department=modeling&version=2"
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data["asset_name"] == "hero"
    assert data["department"] == "modeling"
    assert data["version"] == 2
    assert data["status"] == "inactive"


def test_get_asset_versions_missing_required_query_params_returns_400(api_client):
    """Test getting asset versions with missing required query params"""
    response = api_client.get("/assets/versions")

    assert response.status_code == 400
    assert "error" in response.get_json()


def test_get_asset_versions_not_found_returns_404(api_client):
    """Test getting asset versions that don't exist"""
    response = api_client.get("/assets/versions?asset=missing&type=character")

    assert response.status_code == 404
    assert "error" in response.get_json()

def test_load_assets_from_json(api_client):
    """Test loading assets from a JSON"""
    sample_file = Path("sample_data/asset_data.json").resolve()

    response = api_client.post(
        "/assets/load",
        json={"file_path": str(sample_file)},
    )

    assert response.status_code == 200


def test_load_assets_missing_file_path_returns_400(api_client):
    """Test loading assets with missing file path"""
    response = api_client.post("/assets/load", json={})

    assert response.status_code == 400
    assert "error" in response.get_json()


def test_load_assets_file_not_found_returns_404(api_client):
    """Test loading assets from a non-existent file"""
    response = api_client.post(
        "/assets/load",
        json={"file_path": "sample_data/does_not_exist.json"},
    )

    assert response.status_code == 404
    assert "error" in response.get_json()