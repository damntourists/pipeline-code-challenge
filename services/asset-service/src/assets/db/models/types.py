import enum


class AssetType(enum.Enum):
    """Asset type enum"""
    CHARACTER = "character"
    PROP = "prop"
    SET = "set"
    ENVIRONMENT = "environment"
    VEHICLE = "vehicle"
    DRESSING = "dressing"
    FX = "fx"


class AssetStatus(enum.Enum):
    """Asset status enum"""
    ACTIVE = "active"
    INACTIVE = "inactive"


class Department(enum.Enum):
    """Asset department enum"""
    MODELING = "modeling"
    TEXTURING = "texturing"
    RIGGING = "rigging"
    ANIMATION = "animation"
    CFX = "cfx"
    FX = "fx"
