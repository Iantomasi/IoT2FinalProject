from marshmallow import Schema, fields, validate

class TemperatureSensorSchema(Schema):
    temperature = fields.Number(required=True)
