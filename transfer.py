#Author:  Panzer_wy
#Last updated: 2016/02/09

import re
from datetime import datetime, timedelta
from uuid import uuid4
import sys
import json
import jsondump as jd
import database as db
from flask import Flask, redirect, request, Response, jsonify, render_template
from urllib import urlencode
import re
from functools import wraps
import requests
import cgi
import copy
from config import AUTH_BASE, API_BASE, CLIENT_ID, REDIRECT_URI
import extended_app as extend_api

STATUS_OK = "OK"
STATUS_ERROR = "ERROR"
STATUS_UNKNOWN = "UNKNOWN"
STATUS_UNRELATED = "UNRELATED"
RESERVED_WORD = 'PRIVACY_POLICY_JSON_PARSOR_LAYER_MARK'
'''
    TO DO : Intend this function to be a whole-well organized class
class FHIR_Privacy_Request():
'''

def Catch_dataError():
    with open('error.txt', 'wt') as f:
        f.write("Data Error!")
        f.close()


def list_extension (json_data):
    #Extend resource type into json_list module
    data = jd.json2list(json_data,RESERVED_WORD)
    if isinstance(json_data['resourceType'], unicode):
        s=json_data['resourceType']
    else:
        s=unicode(json_data['resourceType'],"utf-8")
    for i in range(len(data)):
        data[i].insert(0,s)
    return json.dumps(jd.list2json(json_data,RESERVED_WORD),separators=(',',':'))


def get_resource_identifier(url,bundle):
    # get unique identifier from url
    # Transferred data might not have key identifier, although this is quite strange
    if 'Identifier' in bundle:
        return bundle['Identifier']['value']
    else:
        pattern = re.compile(r'(?<=\/)[0-9A-Za-z-]*(?=\?)')
        identifier = pattern.search(url+'?').group()
        # TO-DO: Here pattern.search(url+'?') might get a value of None
        # then there will be a problem for none has no attribute 'group
        return identifier


def retrieve(policy, raw):
    '''

    :param policy: a list to identify a item of patient's info, the policy[-1] is the attribute of the item
    :param raw: result of json2list()
    :return: return processed patient's info
    '''
    not_found_flag = True
    for item in raw:
        if jd.listequal(policy[:-1],item[:-1]):
            not_found_flag = False
            #policy[-1] = 'Mask'
            return u'Mask',item[-1]

    if not_found_flag:
        #policy[-1] = 'Not_Found'
        return u'Not_Found',0


def cover_protected_data(data_list, resource, patient_id, status='full'):
    '''
    data_list : sometimes we don't wanna display all part of this resource, this list will tell us which to display,a list
        resource : json data that wanna to display, the format is dict
    patient_id : extract identifier of policy_list
    '''
    privacy_policy = db.select_policy(patient_id)
    if (privacy_policy == -2):
        #No record in the database
        return resource

    policy_data = jd.json2list(privacy_policy,RESERVED_WORD)

    if type(data_list) is dict:
        data_list = jd.json2list(data_list, RESERVED_WORD)

    if isinstance(resource['resourceType'], unicode):
        s=resource['resourceType']
    else:
        s=unicode(resource['resourceType'],"utf-8")
    resource_data = jd.json2list(resource,RESERVED_WORD)
    print json.dumps(resource, indent=4)
    for i in range(len(resource_data)):
        resource_data[i].insert(0,s)

    data = data_list

    for i in range(len(data)):
        data[i].insert(0,s)
    print 'llala'
    for item in data:
        print item
    print 'lalala'
    #If the query is only part of data,then do the intersection
    for i in range(len(data)):
        if data[i][1] == 'text' or data[i][1] == 'resourceType':
            continue

        tmp = retrieve(data[i],resource_data)
        if tmp[0] == 'Not_Found':
            data[i][-1] = 'Not in the online record'
        else:
            data[i][-1] = tmp[1]

    for i in range(len(data)):
        if data[i][1]=='text' or data[i][1]=='resourceType':
            continue
        tmp =retrieve(data[i],policy_data)
        # Not found or unmasked means we should not change the value
        if tmp[0] == 'Mask':
            #Here we need to filter the policy
            data[i][-1] = 'Protected data due to privacy policy'

    for i in range(len(data)):
        del data[i][0]

    return jd.list2json(data,RESERVED_WORD)

'''
    Note: The official way to resolve this problem is to use
    search parameters: _include & _revinclude
    TO DO: Finish and apply this method to avoid redundant query
'''
def get_resource_refpatientID(resource):
    #resource is a json data
    '''
    This program intends to get resource's
        subject reference of Patient.
    It may involve serveral Patient or has no conncection with a patient.
    So this function return a list of value of patient_id
    '''
    '''
    Usage of _revinclude
    identifer = resource['Identifer']['value']
    forward_args = request.args.to_dict(flat=False)
    forward_args['_format'] = 'json'
    forwarded_url = resource['resourceType']+ '/'+ identifer
    api_url = '/%s?%s'% (forwarded_url, '_revinclude')
    api_resp = extend_api.api_call(api_url)

    if api_resp.status_code != '403':
        response=api_resp.json()
    else:
        return "Http_403_error"
    '''
    # In this demo, however, we simplify this process by assuming certain scenario
    if resource.has_key('reference'):
        for ref in resource['reference']:
            if ref.has_key('subject') and ref['subject']=='Patient':
		        patient_id = ref['text']
    elif resource.has_key('patient'):
        ref=resource['patient']['reference'] 
        patient_id = ref.split('/')[1]
    else: 
        patient_id = STATUS_ERROR
    
    return patient_id



def check_private_policy(resource, resource_id, client_id):
    '''
    check whether resource have something need to be covered
    and apply policy to cover proteceted data
    and it will return the json data after processing
    '''
    #To do, make it more smarter (The complexity of EMR constraints its beauty)
    '''
    The program ,at present time, only can cover some info. in underlying scope:
    Patient
    Observation
    Sequence
    Condition
    '''
    #To do, extend it to all patient-related resources
    #To do, get a more powerful json parser wheel to find intersection
    '''
        Note we have to identify patient's identifier if needed
    In this demo, url is unique
    And unfortunately, all id's performance is not the same in app server
    Someone can change tedious switch cases if eaiser access is available
    '''

    if resource['resourceType'] == 'Patient':
	    #resource['gender']= 'Protected Due to Policy'
        resource = cover_protected_data(resource, resource, resource_id)
        
    elif resource['resourceType'] is not None:
        # In this part , the query data might have reference on patient's data and
        # it is meaningful to filter some policies that forbid someone from access
        # to these info.
        patient_id = get_resource_refpatientID(resource)
        #print patient_id
        if patient_id == STATUS_ERROR:
            #This means it cannot find its source patient's id (or it has no connection with a patient)
            return resource
        resource = cover_protected_data(resource, resource, patient_id)
    else:
        pass
    return resource


def search_request_patient(patient_id):
    # locate specific patient on remote server
    forward_args = request.args.to_dict(flat=False)
    forward_args['_format'] = 'json'
    forwarded_url = 'Patient/' + patient_id
    api_url = '/%s?%s'% (forwarded_url, urlencode(forward_args, doseq=True))
    api_resp = extend_api.api_call(api_url)
    if api_resp.status_code != '403':
        return api_resp.json()
    else:
        return "Http_403_error"

def query_info (data_list, patient_id):
    '''
    data_list is a json_list(need to be extended)
    Now we only support single type data
        This is the query port to ask for specific sequence from remote server
     And , add filter policy
    '''
    #Now time to ask for patient's data
    resource = search_request_patient(patient_id)

    if resource == 'Http_403_error' :
        return 'Not_Found',{}

    data_list = jd.form2list(data_list, jd.formtable, jd.json2list(resource, RESERVED_WORD))
    #print json.dumps(jd.list2json(data_list,RESERVED_WORD),indent=4)
    #data_list = jd.list2json(data_list, RESERVED_WORD)
    #if data_list is None or data_list['resourceType'] is None:
    #Catch_dataError()
    #return 'Not_Found',data_list
    return 'Found',cover_protected_data(
            data_list,
            resource,
            patient_id,
            'cap')

def modify_policy(data_list, patient_id):
    # Receive json data data_list and insert into database
    # Probably its hard to give a direct example
    # Also, only support one-type data
    # Mixed requirement should be splitted into ones

    if data_list is None or data_list['resourceType'] is None:
        Catch_dataError()
        return data_list
    policy_list = list_extension(data_list)
    tag = db.insert_record(patient_id, policy_list, datetime.now())
    if tag == 1:
        return STATUS_OK
    elif tag == 0:
        tag2 = db.add_policy(patient_id, policy_list, datetime.now())
        if tag2 == -1:
            return STATUS_ERROR
        else:
            return STATUS_OK
    else:
        return STATUS_ERROR
