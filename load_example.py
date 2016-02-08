example_policy = {
    "Patient":{
    "name": [
        {
            "text": "Victor Bland"
        }
    ],
    "resourceType": "Patient",
    "text": {
        "status": "generated",
        "div": "<div><p>Victor Bland</p></div>"
    },
    "meta": {
        "versionID": 1,
        "lastUpdated": "2016-01-13T15:31:28.723332"
    },
    "gender": "male",
    "id": "4b9f9ab9-d723-45d2-b185-3439a7f51690"
    }
}


example_id= "4b9f9ab9-d723-45d2-b185-3439a7f51690"




import database as db

db.delete_record(example_id)
db.insert_record(example_id, example_policy, None)
