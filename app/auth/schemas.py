from marshmallow import Schema, fields, validate


class UserSchema(Schema):
    # userId = fields.Str()
    username = fields.Email(required=True)
    password = fields.Str(required=True)
    first_name = fields.Str()
    last_name = fields.Str()


class TokenSchema(Schema):
    userId = fields.Str(required=True)
    device_id = fields.Str(required=True)
    access_token = fields.Str()
    refresh_token = fields.Str()
    expires_at = fields.DateTime()
    refresh_expires_at = fields.DateTime()
 