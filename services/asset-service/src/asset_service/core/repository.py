from sqlalchemy.orm import Session
from ..database.models import Asset

class AssetRepository:

    @staticmethod
    def get_by_id(session: Session, asset_id: int) -> Asset:
        return session.query(Asset).filter(Asset.id == asset_id).first()

    @staticmethod
    def create(session: Session, name: str, asset_type: str) -> Asset:
        asset = Asset(name=name, asset_type=asset_type)
        session.add(asset)
        # session.commit()
        # session.refresh(asset)
        return asset

