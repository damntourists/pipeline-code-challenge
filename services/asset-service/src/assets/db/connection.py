import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from asset_common.logging_utils import setup_logger

log = setup_logger("test")

DB_URL = os.getenv("DB_URL", "mysql+pymysql://dbuser:Password123@db:3306/asset_db")

engine = create_engine(DB_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_session():
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()