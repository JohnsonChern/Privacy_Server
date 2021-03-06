from flask import Flask, redirect, request, Response, jsonify, render_template
from urllib import urlencode
import re
from functools import wraps
import requests
import json
import cgi
import copy
from config import AUTH_BASE, API_BASE, CLIENT_ID, REDIRECT_URI, PRIVACY_BASE
from forms import SubmitForm, AuthenticationForm, SubmitDictForm,UserLoginForm,LoginForm,set_query_form,set_relative_info,init_setting
import set_private as sp
from filter import TextFilter
import parser as pe
import template as tp

STATUS_OK = "OK"
STATUS_ERROR = "ERROR"
STATUS_UNKNOWN = "UNKNOWN"
STATUS_UNRELATED = "UNRELATED"


# we use this to shorten a long resource reference when displaying it
MAX_LINK_LEN = 20
# we only care about genomic stuff here
REF_RE = re.compile(r'^(?:Condition|Patient|Sequence|Observation)/.*$')
# list of scopes we need
SCOPES = ['user/Sequence.read',
        'user/Observation.read',
        'user/Condition.read',
        'user/Patient.read',
]

app = Flask(__name__)

class OAuthError(Exception):
    pass

def get_resource_identifier(url,bundle):
    #get unique identifier from url
    # Transferred data might not have key identifier, although this is quite strange
    pattern = re.compile(r'(?<=\/)[0-9A-Za-z-]*(?=\?)')
    identifier = pattern.search(url+'?').group()
    return identifier

def get_access_token(auth_code):
    '''
    exchange `code` with `access token`
    '''
    exchange_data = {
        'code': auth_code,
        'redirect_uri': REDIRECT_URI,
        'client_id': CLIENT_ID,
        'grant_type': 'authorization_code'
    }
    resp = requests.post(AUTH_BASE+'/token', data=exchange_data)
    if resp.status_code != 200:
        raise OAuthError
    else:
        return resp.json()['access_token']

def api_call(api_endpoint):
    '''
    helper function that makes API call
    '''
    access_token = request.cookies['access_token']
    auth_header = {'Authorization': 'Bearer %s'% access_token}
    return requests.get('%s%s'% (API_BASE, api_endpoint), headers=auth_header)

def to_internal_id(full_id):
    '''
    markup an internal resource id with anchor tag.
    e.g. change Patient/123 into <a href='...'>Patient/123</a>
    '''
    if not full_id.startswith(API_BASE):
        internal_id = full_id
    else:
        internal_id = full_id[len(API_BASE)+1:]

    return '<a href="/resources/%s">%s...</a>'% (internal_id, internal_id[:MAX_LINK_LEN])

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


def render_fhir(resource):
    '''
    render a "nice" view of a FHIR bundle
    '''
    if 'is_single_resource' in resource and resource['is_single_resource'] == True:
        resource['entry'][0]['id'] = to_internal_id(resource['entry'][0].get('id', ''))
        resource['entry'][0]['resource'].get('id',resource['entry'][0]['id'])
    else:
        for entry in resource['entry']:
            entry['resource']['id'] = to_internal_id(resource['resourceType']+'/'+entry['resource'].get('id', ''))

    return render_template('bundle_view.html', **resource)

def make_links(resource):
    '''
    scans a resource and replace internal resource references with anchor tags pointing to them
    e.g. turn {'reference': 'Patient/123'} into {'reference': '<a href="...">"Patient/123"</a>'}

    we are not reusing `def to_internal_id` here because that function shortens an id for styles
    '''
    for k, v in resource.iteritems():
        if isinstance(v, dict):
            make_links(v)
        elif isinstance(v, list):
            vs = v
            for v in vs:
                if isinstance(v, dict):
                    make_links(v)
        elif isinstance(v, basestring) and REF_RE.match(v) is not None:
            resource[k] = "<a href='/resources/%s'>%s</a>"% (v, v)


def get_code_snippet(resource):
    code = copy.deepcopy(resource)
    if code.get('text', {}).get('div'):
        embeded_html = code['text']['div']
        code['text']['div'] = cgi.escape(embeded_html).encode('ascii', 'xmlcharrefreplace')
    # replace internal references with anchor tags
    make_links(code)
    return json.dumps(code, indent=4)


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


@app.route('/')
@require_oauth
def index():
    #return redirect('/resources/Patient')
    return redirect('/search')
    #return redirect('/patient_test/f002/Lung cancer')


@app.route('/recv_redirect')
def recv_code():
    code = request.args['code']
    access_token = get_access_token(code)
    resp = redirect('/')
    resp.set_cookie('access_token', access_token)
    return resp

@app.route('/search',methods=['GET', 'POST'])
#@require_oauth
def search():
    form = set_query_form()
    if form.validate_on_submit():
        keys = tp.extend_option(form)
        #get the keys the doctor selected

        return redirect('/patient_test/%s/%s' % (form.identifier.data,form.disease.data))

    return render_template('orientation.html', form=form)

@app.route('/orientation',methods=['GET','POST'])
def orientation():
    form = LoginForm()
    if form.validate_on_submit():
        pass
    return render_template('orientation.html',form=form)


@app.route('/doctor',methods=['GET', 'POST'])
#@require_oauth
def doctor():
    form = set_query_form()
    if form.validate_on_submit():
        keys = tp.extend_option(form)
        #get the keys the doctor selected

        forward_args = request.args.to_dict(flat=False)
        forward_args['_format'] = 'json'
        forwarded_url =  'Patient' + '/' + form.identifier.data
        api_url = '/%s?%s'% (forwarded_url, urlencode(forward_args, doseq=True))
        api_resp = api_call(api_url)
        #print api_resp._content
        raw_patient_file = json.dumps(api_resp.json())
        resp = requests.get('%s/%s' %(PRIVACY_BASE,form.identifier.data), headers={'Content-Type': 'application/json'})
        private_profile = json.loads(json.dumps(resp.json()))
        try:
            private_policy=[]
            for k,v in private_profile['Resource'].items():
                private_policy.append(v)
        except:
            private_policy=[{"Policy":"Nope","Policy_ResourceType":"NULL"}]


        cross_loc = TextFilter(form.identifier.data, form.disease.data)

        # First scan the observation data to locate specific observation result
        cross_loc.get_observation_list()

        #Then to locate the genetic info(i.e. Sequence Resource) in the data base
        cross_loc.observation_prune()
        cross_loc.get_genetic_info()

        #print raw_patient_file
        #print cross_loc.filtered_Observation
        #print cross_loc.correlated_genetic
        #print private_profile
        #if resp.status_code == 404:
        #    return STATUS_ERROR
        #json_data = pe.retrive_patient_info(keys,private_profile,raw_json_file);
        #print cross_loc.filtered_Observation[0]

        #private_policy = json.dumps(private_policy)
        '''
        try:
            patient, observation, sequence = pe.retrive_patient_info(keys, private_policy, raw_patient_file, cross_loc.filtered_Observation[0] ,cross_loc.correlated_genetic)
        except:
            patient, observation, sequence = pe.retrive_patient_info(keys, private_policy, raw_patient_file, json.dumps({"message": "No result"}), cross_loc.correlated_genetic)
        '''
        #get the masked user info
        #query_dict  = json.loads(json_data)

        #token needed, but now I don't konw how to get it
        #user's id still in form.identifier.data

        '''
        return render_template('query_result.html',
                          token= 'Found',
                          json = json.dumps(query_dict,indent=4))
        '''
        #patient = json.loads(patient)
        #print json.dumps(patient)
        #print json.dumps(observation,indent= 4)
        #print json.dumps(sequence,indent= 4)
        print json.dumps(private_policy, indent= 4)

        if(len(cross_loc.filtered_Observation)>0):
            for observation in cross_loc.filtered_Observation:
                resp = requests.get('%s/%s' %(PRIVACY_BASE,observation['id']), headers={'Content-Type': 'application/json'})
                private_profile = json.loads(json.dumps(resp.json()))
                print private_profile
                try:
                    for k,v in private_profile['Resource'].items():
                        private_policy.append(v)
                except:
                    pass
            for seq in cross_loc.correlated_genetic:
                resp = requests.get('%s/%s' %(PRIVACY_BASE,seq['id']), headers={'Content-Type': 'application/json'})
                private_profile = json.loads(json.dumps(resp.json()))
                try:
                    for k,v in private_profile['Resource'].items():
                        private_policy.append(v)
                except:
                    pass
            patient, observation,sequences = pe.display(keys, private_policy, raw_patient_file, cross_loc.filtered_Observation ,cross_loc.correlated_genetic)

        else:
            patient, observation,sequences =  pe.display(keys, private_policy, raw_patient_file, [], cross_loc.correlated_genetic)


        #patient,observation = pe.display(selected_keys, private_profile, raw_json_patient,raw_ob,raw_seq)
        return render_template('rebuild_show.html',patient_info = patient,observation = observation,sequences = sequences)


        #return redirect('/patient_test/%s' % (form.identifier.data))

    return render_template('submit.html',
                           form=form)


@app.route('/submit_policy/<path:patient_id>', methods=['GET', 'POST'])
def submit_policy_page(patient_id):
    data_dict = {}
    for resource_type in ['Patient', 'Sequence', 'Condition', 'Observation']:
        forward_args = request.args.to_dict(flat=False)
        forward_args['_format'] = 'json'
        forwarded_url =  resource_type + '/' + patient_id
        api_url = '/%s?%s'% (forwarded_url, urlencode(forward_args, doseq=True))
        api_resp = api_call(api_url)
        if api_resp.status_code not in [403, 404]:
            data_dict[resource_type] = api_resp.json()
        form = SubmitDictForm("root", data_dict)

    return render_template('submit_policy.html', form=form)


@app.route('/resources/<path:forwarded_url>')
@require_oauth
def forward_api(forwarded_url):
    forward_args = request.args.to_dict(flat=False)
    forward_args['_format'] = 'json'
    api_url = '/%s?%s'% (forwarded_url, urlencode(forward_args, doseq=True))
    api_resp = api_call(api_url)
    bundle = api_resp.json()
    # Here we install the privacy policy for patient
    # There is a sudden change in server so this is modified to avoid throw TypeError

    if ('type' in bundle and bundle['type'] != 'searchset') or ('resourceType' in bundle and bundle['resourceType']!='Bundle'):
        resource = bundle
        #patient_id = resource['id']
        #modified_resource = tr.check_private_policy(resource,patient_id,CLIENT_ID)
        #code_snippet = get_code_snippet(modified_resource)
        code_snippet = get_code_snippet(resource)
        bundle = {
            'resourceType': resource['resourceType'],
            'entry': [{
                'resource': resource,
                'id': forwarded_url
            }],
            'is_single_resource': True,
            'code_snippet': code_snippet
        }
    elif len(bundle.get('entry', [])) > 0:
        bundle['resourceType'] = bundle['entry'][0]['resource']['resourceType']

    # Here is the trick, to use a modified function instead of original one
    #return render_fhir_extended(bundle)
    return render_fhir(bundle)

@app.route('/patient_test/<path:patient_id>/<path:search_text>',methods=['GET','POST'])
def set_form(patient_id,search_text):
    forward_args = request.args.to_dict(flat=False)
    forward_args['_format'] = 'json'
    forwarded_url =  'Patient' + '/' + patient_id
    #api_url = '/neprivacy/%s?%s'% (forwarded_url, urlencode(forward_args, doseq=True))
    api_url='/%s?%s'% (forwarded_url, urlencode(forward_args, doseq=True))
    api_resp = api_call(api_url)
    json_file = api_resp.json()
    #json_file is the user info we get from the server

    cross_loc = TextFilter(patient_id,search_text)

    # First scan the observation data to locate specific observation result
    cross_loc.get_observation_list()

    #Then to locate the genetic info(i.e. Sequence Resource) in the data base
    #cross_loc.observation_prune()
    cross_loc.get_genetic_info()
    print cross_loc.filtered_Observation
    patient_info_form,patient_info_class,observed,sequence = init_setting(json_file,cross_loc.filtered_Observation, cross_loc.correlated_genetic)
    #with the json file we now get from and class

    if patient_info_form.validate_on_submit():
        print observed
        patient_private,ob_private,seq_private =  pe.get_private_profile(patient_info_form,patient_info_class,observed,sequence,json_file)
        # now we get the private profile
        #print type(private_profile)
        #if 'id' in private_profile:
        #    private_profile['resourceID'] = private_profile['id']
        #    del private_profile['id']


        '''
        resp = requests.put('%s/%s' %(PRIVACY_BASE,patient_private['resourceID']), data=json.dumps(patient_private), headers={'Content-Type': 'application/json'})
        for ob in cross_loc.filtered_Observation:
            ob_private['resourceID']=ob['id']
            resp_ob = requests.put('%s/%s' %(PRIVACY_BASE,ob_private['resourceID']), data=json.dumps(ob_private), headers={'Content-Type': 'application/json'})
            if resp_ob.status_code == 404:
                return STATUS_ERROR
        resp_ob = requests.put('%s/%s' %(PRIVACY_BASE,ob_private['resourceID']), data=json.dumps(ob_private), headers={'Content-Type': 'application/json'})

        for seq in seq_private:
            resp_seq = requests.put('%s/%s' %(PRIVACY_BASE,seq['resourceID']), data=json.dumps(seq), headers={'Content-Type': 'application/json'})
            if resp_seq.status_code ==404:
                return STATUS_ERROR

        if resp.status_code == 404 :
            return STATUS_ERROR
        else:
        '''
        return json.dumps(ob_private,indent=4);
            #return render_template('temp.html',result = {"Patient":resp.json(), "Observation": resp_ob.json(), "Sequence": resp_seq.json()})
            #return redirect('/doctor')
    return render_template('rebuild_set.html',form = patient_info_form,patient_info = patient_info_class,observation=observed,sequences= sequence)




@app.route('/masked_content')
def masked_content_info():
    return render_template('masked_content.html')

@app.route('/user_login',methods=['GET','POST'])
def user_login():
    form = UserLoginForm(csrf_enabled=False)
    if form.validate_on_submit():
        return render_template('user_center.html',form=form)
    return render_template('login.html',form=form)

if __name__ == '__main__':
    app.config.from_object('config')
    app.run(debug=True, port=8000)
