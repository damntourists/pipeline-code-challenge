from assets.db.models.types import AssetType


class BaseAssetException(Exception):
    """Base class for all asset exceptions"""
    pass

class AssetNotFoundError(BaseAssetException):
    """Raised when an asset is not found"""
    def __init__(self, identifier: int):
        super().__init__(f"Asset with identifier '{identifier}' not found")

class DuplicateAssetError(BaseAssetException):
    """Raised when an asset with the same name and type already exists"""
    def __init__(self, name: str, asset_type: AssetType):
        self.name = name
        self.asset_type = asset_type

        super().__init__(
            f"Asset with name '{name}' and type '{asset_type}' already exists"
        )

class ValidationError(BaseAssetException):
    """Raised when an asset fails validation"""
    def __init__(self, message: str):
        super().__init__(f"Asset validation failed: {message}")