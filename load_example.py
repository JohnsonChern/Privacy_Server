example_policy = {
    "Patient":{
    "name": [
        {
            "text": "Elizabeth Murray"
        }
    ],
    "resourceType": "Patient",
    "text": {
        "status": "generated",
        "div": "<div><p>Elizabeth Murray</p></div>"
    },
    "meta": {
        "versionID": 1,
        "lastUpdated": "2016-01-13T15:31:27.105922"
    },
    "gender": "female",
    "id": "17dd336d-1562-40a4-89f3-23649c5c85d8"
    }
}


example_id= "17dd336d-1562-40a4-89f3-23649c5c85d8"




import database as db

db.delete_record(example_id)
db.insert_record(example_id, example_policy, None)
