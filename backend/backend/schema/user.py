from marshmallow import fields
from marshmallow.validate import Length, OneOf

from backend.model.user import Role, User
from . import ma


class UserSchema(ma.SQLAlchemyAutoSchema):  # type: ignore
    class Meta:
        model = User
        load_instance = True
        exclude = ['password', '_email']

    id = fields.String(required=True, dump_only=True)
    creation_date = fields.DateTime(required=True, dump_only=True)
    email = fields.Email(required=True)
    first_name = fields.String(required=True, validate=Length(min=1))
    last_name = fields.String(required=True, validate=Length(min=1))
    role = fields.String(
        required=True,
        validate=OneOf(Role.__members__.values()),
    )
    enabled = fields.Boolean()
