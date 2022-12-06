from marshmallow import Schema, fields, validate

class UltraSonicSensorSchema(Schema):
    measurement = fields.Number(required=True)
