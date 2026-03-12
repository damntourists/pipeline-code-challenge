import os
from sqlalchemy import create_engine, create_url
from sqlalchemy.orm import sessionmaker, scoped_session

DB_URL = os.getenv("DB_URL", "mysql+pymysql://dbuser:Password123@db:3306/asset_db")

engine = create_engine(DB_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# session_scope = scoped_session(SessionLocal)

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