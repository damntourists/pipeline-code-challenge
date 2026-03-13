import enum

from sqlalchemy.orm import declarative_base

Base = declarative_base()

class AssetType(enum.Enum):
    CHARACTER = "character"
    PROP = "prop"
    SET = "set"
    ENVIRONMENT = "environment"
    VEHICLE = "vehicle"
    DRESSING = "dressing"
    FX = "fx"

class Asset(Base):
    __tablename__ = 'assets'