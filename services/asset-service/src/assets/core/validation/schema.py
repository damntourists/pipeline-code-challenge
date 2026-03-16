from marshmallow import Schema, fields, validate

from assets.db.models.types import AssetType

class AssetSchema(Schema):
    name = fields.Str(required=True)
    type = fields.Str(required=True, validate=validate.OneOf(AssetType))

class AssetVersionSchema(Schema):
    department = fields.Str(required=True)
    version = fields.Int(required=True)
    status = fields.Str(required=True)