import pymongo
import datetime as dt
from time import sleep



client = pymongo.MongoClient("mongodb+srv://GMA:GMASeasonbaby123@iot2project.la8dvua.mongodb.net/?retryWrites=true&w=majority")
db = client.test

number = 2
isSensorOn = True

if 'measurement' not in db.list_collection_names():
    db.create_collection("measurement",
                         timeseries={'timeField': 'timestamp', 'metaField': 'sensorId', 'granularity': 'minutes'})


if __name__ == "__main__":
    while isSensorOn:
        measurement = number
        sensorID = 1
        number+=2
        db.measurement.insert_one({
            'timestamp': dt.datetime.now(),
            'sensorId': sensorID,
            'measurement': measurement
        })
        sleep(3)

