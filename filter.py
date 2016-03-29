from flask import request,redirect
import requests
from urllib import urlencode
from config import API_BASE,CLIENT_ID,REDIRECT_URI,AUTH_BASE
import json
from jsondump import json2list
from functools import wraps

SCOPES = ['user/Sequence.read',
        'user/Observation.read',
        'user/Condition.read',
        'user/Patient.read',
]

NO_USE_KEY = ['meta','extension','text']

def api_call(api_endpoint):
    '''
    helper function that makes API call
    '''
    access_token = request.cookies['access_token']
    auth_header = {'Authorization': 'Bearer %s'% access_token}
    return requests.get('%s%s'% (API_BASE, api_endpoint), headers=auth_header)


def has_access():
    '''
    check if application has access to API
    '''
    if 'access_token' not in request.cookies:
        return False
    # we are being lazy here and don't keep a status of our access token,
    # so we just make a simple API call to see if it expires yet
    test_call = api_call('/Patient?_count=1')
    return test_call.status_code != 403

def require_oauth(view):
    @wraps(view)
    def authorized_view(*args, **kwargs):
        # check is we have access to the api, if not, we redirect to the API's auth page
        if has_access():
            return view(*args, **kwargs)
        else:
            redirect_args = {
                'scope': ' '.join(SCOPES),
                'client_id': CLIENT_ID,
                'redirect_uri': REDIRECT_URI,
                'response_type': 'code'}
            return redirect('%s/authorize?%s'% (AUTH_BASE, urlencode(redirect_args)))

    return authorized_view

class TextFilter(object):
    patient_id = ''
    search_text ='*'
    filtered_Observation = []
    seq_id =[]
    correlated_genetic = []

    def __init__(self,patient_id,text_):
        '''

        :param patient_id:
        :param text_:  * means everything , otherwise it will filter with the text_ info in database
        :return:
        '''
        self.patient_id= patient_id
        self.search_text= text_
        filtered_Observation = {}
        seq_id =[]
        correlated_genetic = []

    @require_oauth
    def get_observation_list(self):
        resource_type = 'Observation'
        forward_args = request.args.to_dict(flat=False)
        forward_args['_format'] = 'json'
        forwarded_url =  resource_type
        api_url = '/%s?%s'% (forwarded_url, urlencode(forward_args, doseq=True))
        print api_url
        resp = api_call(api_url)
        bundle =resp.json();
        if ('type' in bundle and bundle['type'] != 'searchset') or ('resourceType' in bundle and bundle['resourceType']!='Bundle'):
            resource = bundle
            bundle = {
            'resourceType': resource['resourceType'],
            'entry': [{
                'resource': resource,
                'id': forwarded_url
            }],
            'is_single_resource': True,
        }
        elif len(bundle.get('entry', [])) > 0:
            bundle['resourceType'] = bundle['entry'][0]['resource']['resourceType']

        self.filtered_Observation=[]
        self.seq_id=[]
        k=1;

        for i in range(len(bundle['entry'])):
            resource = bundle['entry'][i]['resource']
            #print resource
            try:
                resource_subject = resource['subject']['reference'].split('/')[-1]
            except:
                resource_subject = "Not want to be seen"
            #print json.dumps(resource , indent= 2)
            #print resource_subject
            if resource_subject == self.patient_id:
                if(self.search_text=='*'):
                    self.filtered_Observation.append(resource)
                    self.add_locale_info(resource)
                    k+=1
                else:
                    list_resource = json2list(resource,'FindText')
                    #print list_resource
                    flag= False;
                    for list in list_resource:
                        try:
                            print list
                            if((list[-3]=='text' or list[-2]=='text') and (list[-1]==self.search_text or self.search_text in list[-1])):
                                flag= True;
                                break;
                        except:
                            pass
                    if(flag):
                        print type(resource)
                        print "here\n\n\n"
                        self.filtered_Observation.append(resource)
                        self.add_locale_info(resource)
                        k+=1
        return json.dumps(self.filtered_Observation, indent=4)

    def observation_prune(self):
        new_Observation = []
        for resource in self.filtered_Observation:
            for key in NO_USE_KEY:
                if(key in resource):
                    del resource[key]
            new_Observation.append(resource)
        self.filtered_Observation = new_Observation

    def add_locale_info(self,resource):
        #print resource
        for k, v in resource.iteritems():
            #print k,v
            if isinstance(v,dict):
                #print v
                if 'coding' in v and 'text' in v:
                    if isinstance(v['text'],list):
                        text_ = v['text'][0]
                    else:
                        text_ = v['text']
                    #print text_
                    #print '1'
                    if text_== self.search_text or self.search_text=='*':
                        self.seq_id.append(v)
                    else:
                        self.add_locale_info(v)

            elif isinstance(v,list):
                vs =v
                #print v
                for v in vs:
                    print v
                    if isinstance(v,dict):
                        if 'coding' in v and 'text' in v:
                            if isinstance(v['text'],list):
                                text_ = v['text'][0]
                            else:
                                text_ = v['text']
                            #print type(text_)
                            #print self.search_text
                            if text_== self.search_text or self.search_text=='*':
                                print '3'
                                self.seq_id.append(v)
                        else:
                            self.add_locale_info(v)
            else:
                pass

    def get_code(self,res):
        code = res['coding']
        if isinstance(code,list):
            code = code[0]
        code = code['code']
        if isinstance(code,list):
            code = code[0]
        return code


    def get_system(self,res):
        code = res['coding']
        if isinstance(code,list):
            code = code[0]
        code = code['system']
        if isinstance(code,list):
            code = code[0]
        return code

    @require_oauth
    def get_genetic_info(self):
        resource_type = 'Sequence'
        forward_args = request.args.to_dict(flat=False)
        forward_args['_format'] = 'json'
        forwarded_url =  resource_type
        api_url = '/%s?%s'% (forwarded_url, urlencode(forward_args, doseq=True))
        print api_url
        resp = api_call(api_url)
        bundle =resp.json();
        if ('type' in bundle and bundle['type'] != 'searchset') or ('resourceType' in bundle and bundle['resourceType']!='Bundle'):
            resource = bundle
            bundle = {
            'resourceType': resource['resourceType'],
            'entry': [{
                'resource': resource,
                'id': forwarded_url
            }],
            'is_single_resource': True,
        }
        elif len(bundle.get('entry', [])) > 0:
            bundle['resourceType'] = bundle['entry'][0]['resource']['resourceType']

        #print json.dumps(bundle,indent=4)
        self.correlated_genetic=[]

        seq_id_new =[]
        for seq in self.seq_id:
            flag= False
            print seq
            for res in seq_id_new:
                if self.get_code(res)==self.get_code(seq) and self.get_system(res)==self.get_system(seq):
                        flag= True
            if not flag:
                seq_id_new.append(seq)
        self.seq_id=seq_id_new
        print self.seq_id

        for seq in bundle['entry']:
            resource = seq ['resource']
            if('variationID' in resource):
                identifier = resource['variationID']
                if isinstance(identifier,list):
                    identifier = identifier[0]
                for v in self.seq_id:
                    '''
                    if isinstance(identifier['coding'],list):
                        x=identifier['coding'][0]
                    else:
                        x=identifier['coding']
                    if isinstance(v['coding'],list):
                        y=v['coding'][0]
                    else:
                        y=v['coding']
                    '''
                    if self.get_code(v)==self.get_code(identifier) and self.get_system(v)==self.get_system(identifier):
                        #print "here\n\n\n\n"
                        self.correlated_genetic.append(resource)


