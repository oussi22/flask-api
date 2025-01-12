from marshmallow import Schema, fields

class DecisionSchema(Schema):
    id = fields.Integer(dump_only=True)
    title = fields.String(required=True)
    formation = fields.String(required=True)
    content = fields.String(required=True)

class UserSchema(Schema):
    id = fields.Integer(dump_only=True)
    username = fields.String(required=True)
    email = fields.String(required=True)