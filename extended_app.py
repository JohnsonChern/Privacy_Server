from flask import Flask, redirect, request, Response, jsonify, render_template
from urllib import urlencode
import re
from functools import wraps
import requests
import json
import cgi
import copy
import transfer as tr
from forms import SubmitForm, AuthenticationForm
from config import AUTH_BASE, API_BASE, CLIENT_ID, REDIRECT_URI

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

def render_fhir_extended(resource):

    #Here we implement privacy policy issue before we render a FHIR bundle
    #We call function to check each type resource and cover those
    #protected data
    for i in range(len(resource['entry'])):
	#print resource['entry'][i]
	resource_id = resource['entry'][i]['resource']['id']
 	resource['entry'][i]['resource']=tr.check_private_policy(resource['entry'][i]['resource'],None,CLIENT_ID)
 	resource['entry'][i]['resource']['id'] = to_internal_id(resource['resourceType']+'/'+resource['entry'][i]['resource'].get('id', ''))
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
    return redirect('/resources/Patient')


@app.route('/recv_redirect')
def recv_code():
    code = request.args['code']
    access_token = get_access_token(code)
    resp = redirect('/')
    resp.set_cookie('access_token', access_token)
    return resp


@app.route('/doctor',methods=['GET', 'POST'])
@require_oauth
def doctor():
    form = SubmitForm(csrf_enabled=False)
    if form.validate_on_submit():
        rawlist = []
        for item in form:
            if item.type == "BooleanField" and item.data == True:
                rawlist.append(item.name)

        token,query_dict = tr.query_info(rawlist,form.identifier.data)

        return render_template('query_result.html',
                          token= token,
                          json = json.dumps(query_dict,indent=4))

    return render_template('submit.html',
                           form=form)

@app.route('/submit_policy/', methods=['GET', 'POST'])
@require_oauth
def submit_policy_page():
    form = AuthenticationForm(csrf_enabled=False)
    
    if form.validate_on_submit():
        patient_id = form.identifier.data
        data_dict = {}
        for resource_type in ['Patient', 'Sequence', 'Condition', 'Observation']:
            forward_args = request.args.to_dict(flat=False)
            forward_args['_format'] = 'json'
            forwarded_url =  resource_type + '/' + patient_id
            api_url = '/%s?%s'% (forwarded_url, urlencode(forward_args, doseq=True))
            api_resp = api_call(api_url)
            if api_resp.status_code not in [403, 404]:
                data_dict[resource_type] = api_resp.json()

        return render_template('submit_policy.html')
    
    return render_template('authentication.html',form=form)

@app.route('/resources/<path:forwarded_url>')
@require_oauth
def forward_api(forwarded_url):
    forward_args = request.args.to_dict(flat=False)
    forward_args['_format'] = 'json'
    api_url = '/%s?%s'% (forwarded_url, urlencode(forward_args, doseq=True))
    api_resp = api_call(api_url)
    '''
	The best way to add privacy policy on json data is to decorate it at serverside,
	however this is not accomplished until now.
	So, we apply a little bit complicated way:
	remember to change the value of json data before
        the apps will do some processing issues (e.g. encoding,extracting,rendering)
	We extend the original example to claim how this works
    '''
    bundle = api_resp.json()
    f = open('./log.txt','w')
    f.write(json.dumps(bundle, indent=2))
    f.close
    # Here we install the privacy policy for patient
    # There is a sudden change in server so this is modified to avoid throw TypeError

    if ('type' in bundle and bundle['type'] != 'searchset') or ('resourceType' in bundle and bundle['resourceType']!='Bundle'):
        resource = bundle
        bundle = {
            'resourceType': resource['resourceType'],
            'entry': [{
                'resource': resource,
                'id': forwarded_url
            }],
            'is_single_resource': True,
            'code_snippet': get_code_snippet(tr.check_private_policy(resource,None,CLIENT_ID))
        }
    elif len(bundle.get('entry', [])) > 0:
        bundle['resourceType'] = bundle['entry'][0]['resource']['resourceType']

    # Here is the trick, to use a modified function instead of original one
    return render_fhir_extended(bundle)


if __name__ == '__main__':
    app.run(debug=True, port=8000)
