from flask_marshmallow import Marshmallow
from marshmallow import Schema, fields

ma = Marshmallow()


class EmptySchema(Schema):
    pass


class CreateSchema(Schema):
    id = fields.String()
