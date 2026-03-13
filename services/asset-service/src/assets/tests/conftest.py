import pytest
from assets.main import app as flask_app
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from assets.db.models.base import Base

@pytest.fixture
def app():
    return flask_app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def db_session(app):
    engine = create_engine("sqlite:///:memory:")

    # Enable foreign key constraints for SQLite
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, *_, **__):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    Base.metadata.create_all(engine)
    session_cls = sessionmaker(bind=engine)
    session = session_cls()

    yield session

    session.close()
    Base.metadata.drop_all(engine)
