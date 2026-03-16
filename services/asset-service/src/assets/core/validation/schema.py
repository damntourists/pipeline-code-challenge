from marshmallow import Schema, fields, validate

from assets.db.models.types import AssetType, AssetStatus, Department


class AssetSchema(Schema):
    name = fields.Str(
        required=True,
        validate=validate.Length(min=1),
    )
    type = fields.Str(
        required=True,
        validate=validate.OneOf([item.value for item in AssetType]),
    )


class AssetVersionSchema(Schema):
    department = fields.Str(
        required=True,
        validate=validate.OneOf([item.value for item in Department]),
    )
    version = fields.Int(
        required=True,
        strict=True,
        validate=validate.Range(min=1),
    )
    status = fields.Str(
        required=True,
        validate=validate.OneOf([item.value for item in AssetStatus]),
    )