

example_policy = {
    "Patient":{
        "name": [
            {
                "text": "David Penrod"
            }
        ],
        "resourceType": "Patient",
        "text": {
            "status": "generated",
            "div": "<div><p>David Penrod</p></div>"
        },
        "meta": {
            "versionID": 1,
            "lastUpdated": "2016-01-13T15:31:33.555627"
        },
        "gender": "male",
        "id": "a770136e-616f-45b0-8752-3be0ad9cab42"
    }
}


example_id= "a770136e-616f-45b0-8752-3be0ad9cab42"




import database as db
import json

db.delete_record(example_id)
db.insert_record(example_id, example_policy, None)


if __name__ == '__main__':
    print json.dumps(db.select_policy("7ff9db40-783d-48c4-b564-fffa42d45e04"),indent=2)
