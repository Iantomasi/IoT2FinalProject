import pymongo as pymongo
from flask import Flask, request, jsonify
from flask_objectid_converter import ObjectIDConverter
from pymongo import ReturnDocument
from pymongo.server_api import ServerApi
from Schemas import UltraSonicSensorSchema
from bson import json_util, ObjectId
from flask_cors import CORS
import datetime as dt


# loading private connection information from environment variables
from dotenv import load_dotenv

load_dotenv()
import os

#Connecting to MongoDB
client = pymongo.MongoClient("mongodb+srv://GMA:GMASeasonbaby123@iot2project.la8dvua.mongodb.net/?retryWrites=true&w=majority",
                             server_api=ServerApi('1'))
db = client.test

if 'measurement' not in db.list_collection_names():
    db.create_collection("measurement",
                         timeseries={'timeField': 'timestamp', 'metaField': 'sensorId', 'granularity': 'minutes'})




def getTimeStamp():
    return dt.datetime.today().replace(microsecond=0)


app = Flask(__name__)
# adding an objectid type for the URL fields instead of treating it as string
# this is coming from a library we are using instead of building our own custom type
app.url_map.converters['objectid'] = ObjectIDConverter

app.config['DEBUG'] = True
# making our API accessible by any IP
CORS(app)


@app.route("/sensors/<int:sensorId>/measurement", methods=["POST"])
def add_threadMeasurements_value(sensorId):
    error = UltraSonicSensorSchema().validate(request.json)
    if error:
        return error, 400

    data = request.json
    data.update({"timestamp": getTimeStamp(), "sensorId": sensorId})

    db.measurement.insert_one(data)

    data["_id"] = str(data["_id"])
    data["timestamp"] = data["timestamp"].strftime("%Y-%m-%dT%H:%M:%S")
    return data


@app.route("/sensors/<int:sensorId>/measurement", methods=["GET"])
def get_all_threadMeasurements(sensorId):
    start = request.args.get("start")
    end = request.args.get("end")

    query = {"sensorId": sensorId}
    if start is None and end is not None:
        try:
            end = dt.datetime.strptime(end, "%Y-%m-%dT%H:%M:%S")
        except Exception as e:
            return {"error": "timestamp not following format %Y-%m-%dT%H:%M:%S"}, 400

        query.update({"timestamp": {"$lte": end}})

    elif end is None and start is not None:
        try:
            start = dt.datetime.strptime(start, "%Y-%m-%dT%H:%M:%S")
        except Exception as e:
            return {"error": "timestamp not following format %Y-%m-%dT%H:%M:%S"}, 400

        query.update({"timestamp": {"$gte": start}})
    elif start is not None and end is not None:
        try:
            start = dt.datetime.strptime(start, "%Y-%m-%dT%H:%M:%S")
            end = dt.datetime.strptime(end, "%Y-%m-%dT%H:%M:%S")

        except Exception as e:
            return {"error": "timestamp not following format %Y-%m-%dT%H:%M:%S"}, 400

        query.update({"timestamp": {"$gte": start, "$lte": end}})

    data = list(db.measurement.aggregate([
        {
             '$match': query
        }, {
            '$group': {
                '_id': '$sensorId','avgMeasurement': {
                    '$avg': '$measurement'
                },

                '_id': '$sensorId','measurement': {
                    '$push': {
                        'timestamp': '$timestamp',
                        'measurement':'$measurement',
                        '_id': '$sensorId'
                    }
                }
            }
        },


    ]))

    if data:
        data = data[0]
        if "_id" in data:
            del data["_id"]
            data.update({"sensorId": sensorId})

        for tMeasure in data['measurement']:
            tMeasure["timestamp"] = tMeasure["timestamp"].strftime("%Y-%m-%dT%H:%M:%S")

        return data
    else:
        return {"error": "id not found"}, 404



if __name__ == "__main__":
    app.run(port=5001)

