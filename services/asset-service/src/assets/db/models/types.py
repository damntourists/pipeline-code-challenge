import enum


class AssetType(enum.Enum):
    CHARACTER = "character"
    PROP = "prop"
    SET = "set"
    ENVIRONMENT = "environment"
    VEHICLE = "vehicle"
    DRESSING = "dressing"
    FX = "fx"


class AssetStatus(enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class Department(enum.Enum):
    MODELING = "modeling"
    TEXTURING = "texturing"
    RIGGING = "rigging"
    ANIMATION = "animation"
    CFX = "cfx"
    FX = "fx"
