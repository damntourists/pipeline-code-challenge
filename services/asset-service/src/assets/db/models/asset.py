import enum

from sqlalchemy import Integer, Column, String, UniqueConstraint
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import relationship

from assets.db.models.base import Base
from assets.db.models.types import AssetType

"""
### Asset Data Model

Your data should be validated against the following asset data model. 
What we’re looking for here is a clear extensible representation of an asset, 
versions of an asset, and their properties.  

Each asset has:

Asset:
| Field     | Type      | Notes                                                     |
| -------   | ------    | -------                                                   |
| name      | string    | required                                                  |
| type      | enum      | character, prop, set, environment, vehicle, dressing, fx  |


- Asset uniqueness is described by its (name and type)
    - We do not allow multiple assets with the same name+type, but same name+different type or different name+same type are both fine 

- Each Asset should have at least 1 version associated with it and no duplicate versions 
   - Versions should also increment linearly by integer

- Asset version uniqueness is described by the (asset + department + version)
   - You may have `(hero+character)+animation+v1` and `(hero+character)+cfx+v1`, but not two `(hero+character)+animation+v1` entries

---

"""



class Asset(Base):
    __tablename__ = 'assets'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    type = Column(SAEnum(AssetType), nullable=False)

    versions = relationship(
        "AssetVersion",
        back_populates="asset",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        UniqueConstraint('name', 'type', name='uix_name_type'),
    )
