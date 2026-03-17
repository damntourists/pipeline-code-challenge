from typing import Any, Generator

import pytest


from assets.api import routes
from assets.main import app as flask_app
from sqlalchemy import create_engine, event, Engine
from sqlalchemy.orm import sessionmaker, Session

from assets.db.models.base import Base

@pytest.fixture
def app():
    """Fixture to provide the Flask app for testing"""
    return flask_app

@pytest.fixture
def client(app):
    """Fixture to provide a test client for the Flask app"""
    return app.test_client()

@pytest.fixture(scope="session")
def engine() -> Engine:
    """Fixture to provide a test database engine"""
    engine = create_engine("sqlite:///:memory:")

    # Enable foreign key constraints for SQLite
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, *_, **__):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    Base.metadata.create_all(engine)

    return engine

@pytest.fixture
def db_session(app, engine):
    """Fixture to provide a database session"""
    connection = engine.connect()
    transaction = connection.begin()
    session = sessionmaker(bind=connection)()

    yield session

    session.close()
    if transaction.is_active:
        transaction.rollback()
    connection.close()

@pytest.fixture
def api_client(client, db_session, monkeypatch):
    """Fixture to provide a test client for the Flask app"""
    def _session_factory():
        return db_session

    monkeypatch.setattr(routes, "SessionLocal", _session_factory)
    return client