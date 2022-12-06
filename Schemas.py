from marshmallow import Schema, fields, validate

class UltraSonicSensorSchema(Schema):
    threadMeasurements = fields.Number(required=True)
