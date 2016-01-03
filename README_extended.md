This is application of privacy filter on Demo app for [FHIR Genomics API](https://github.com/dsrcl/fhir-genomics).

### How to use

#####Setup basic environment
1. This demo app uses `requests` and `flask`. If you have `pip`, simply do
```
$ pip install requests flask
```
Or simply
```
$ pip install -r requirement_app.txt

```
2. Edit `config.py` to point the app to a server.

##### Run for static test
1. Run the original server at localhost with:
```
$ python app.py
```

2. Run modified server at localhost with:
```
$ python app.py
```

3. You will need local database support to see dynamic interation on how this policy works

... To be continued


## Help Guide (No need in final version)
### Transfer.py

*	search_request_patient(patient_id) 
	*	Simply get api search 
*	check_private_policy(resource, resource_id, client_id)
	*	One major function to maintain display of content in json
	*	Need to be better built
*	query_info (data_list, patient_id)
	*	Pick_something_in data_list to be revealed by filtered policy
	*	patient_id is needed to locate data
*	modify_policy(data_list, patient_id)
	*	Simply maintain local db of privacy policy
	*	**To do** : Design an API wrapper to get access of this function

### extended_app.py

*	Basic idea : change json before output or passing value
*	see forward_api(forwarded_url) to get more details
