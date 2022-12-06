from marshmallow import Schema, fields, validate

class UltraSonicSensorSchema(Schema):
    temperature = fields.Number(required=True)
