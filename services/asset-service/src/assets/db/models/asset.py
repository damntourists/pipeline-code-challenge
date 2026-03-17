import enum

from sqlalchemy import Integer, Column, String, UniqueConstraint
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import relationship

from assets.db.models.base import Base
from assets.db.models.types import AssetType

class Asset(Base):
    """Asset model"""
    __tablename__ = 'assets'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    type = Column(SAEnum(AssetType), nullable=False)

    versions = relationship(
        "AssetVersion",
        back_populates="asset",
        passive_deletes=True,
        cascade="all, delete-orphan",
        order_by="AssetVersion.version",
    )

    __table_args__ = (
        UniqueConstraint('name', 'type', name='uix_name_type'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type.name,
            'version_count': len(self.versions),
        }