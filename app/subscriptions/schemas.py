from datetime import datetime
from jsonschema import ValidationError
from marshmallow import Schema, fields, post_load, validate
from marshmallow.validate import OneOf, Length


class ISODate(fields.Date):
    def _serialize(self, value, attr, obj, **kwargs):
        return value.isoformat() if value else None

    def _deserialize(self, value, attr, data, **kwargs):
        if value:
            try:
                return datetime.strptime(value, '%Y-%m-%d').date()
            except ValueError as e:
                raise ValidationError("Invalid date format.")
        return None


class SubscriptionSchema(Schema):
    userId = fields.Str(required=True)
    name = fields.Str(required=True, validate=Length(max=30))
    price = fields.Str(required=True, validate=Length(
        max=10))  # Use string for price
    payment_method = fields.Str(required=True, validate=Length(max=30))
    date = ISODate(required=True)
    started_on = ISODate(missing=lambda: datetime.utcnow().isoformat())
    subscription_type = fields.Str(validate=OneOf(["M", "Y"]), missing="M")
    create_reminder = fields.Boolean(missing=False)

    class Meta:
        unknown = 'include'  # Include unknown fields in the deserialized data
