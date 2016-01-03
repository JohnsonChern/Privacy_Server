example_policy = {
	"Sequence":{
		"resourceType": "Sequence",
   	 	"observedAllele": "masked",
		"variationID": {
        		"coding": [
            			{
                			"code": "masked"
				}
			]
		}
	},
	"Patient":{
		"name": [
        	{
            	"text": "Garret Doremus"
        	}
    	],
    	"gender": "male"
	}
}

example_id= "4d5532fa-d5a1-42bf-82ea-3a223f2cce0b"




import database as db

db.delete_record(example_id)
db.insert_record(example_id, example_policy, None)
