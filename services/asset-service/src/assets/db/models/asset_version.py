import enum

from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import relationship

from assets.db.models.base import Base
from assets.db.models.types import Department, AssetStatus

"""
Asset Version:
| Field         | Type          | Notes                                                             |
| -------       | ------        | -------                                                           |
| asset         | foreign key   | reference to the asset this version represents                    |
| department    | string        | required: ex. modeling, texturing, rigging, animation, cfx, fx    |
| version       | integer       | ≥ 1 and follows a sequential order                                |
| status        | enum          | active, inactive                                                  |

"""


class AssetVersion(Base):
    __tablename__ = "asset_versions"

    id = Column(Integer, primary_key=True)
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=False)
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