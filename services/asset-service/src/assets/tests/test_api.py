import pytest

from asset_common.logging_utils import setup_logger

logger = setup_logger(__name__)

def test_app_health(client):
    logger.info("Testing app health")
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json == {'status': 'ok'}