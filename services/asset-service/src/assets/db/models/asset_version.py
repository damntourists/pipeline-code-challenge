import enum

from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import relationship

from assets.db.models.base import Base
from assets.db.models.types import Department, AssetStatus


class AssetVersion(Base):
    """Asset version model"""
    __tablename__ = "asset_versions"

    id = Column(Integer, primary_key=True)
    asset_id = Column(
        Integer,
        ForeignKey("assets.id", ondelete="CASCADE"),
        nullable=False,
    )
    version = Column(Integer, nullable=False)

    department = Column(SAEnum(Department, native_enum=False), nullable=False)
    status = Column(
        SAEnum(AssetStatus, native_enum=False),
        nullable=False,
        default=AssetStatus.ACTIVE,
    )

    asset = relationship("Asset", back_populates="versions")

    __table_args__ = (
        UniqueConstraint(
            'asset_id',
            'department',
            'version',
            name='uix_asset_id_department_version',
        ),
    )