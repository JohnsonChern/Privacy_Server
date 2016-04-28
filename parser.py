import json
import jsonexample as jp
import template as tp

masked_info = tp.masked_info

basic_type = tp.basic_type

fhir_template = tp.fhir_template

primary_key = tp.primary_key

masked_title = tp.masked_title

masked_info = tp.masked_info

masked_mark = tp.masked_mark


class domain:
    def __init__(self,file,template,key,domain_layer='single'):

        self.sub_domains = []
        self.value = []
        self.domain_layer = domain_layer
        self.domain_type = 'key'
        self.masked = False
        self.display_mask = False
        self.seq = None
        self.primary_key = None
        self.primary_value = None
        #set key for the domain
        self.key = key




        if file ==None:
            # element missing
            self.domain_type = 'miss'
            self.domain_layer = 'miss'

        elif type(template)==list:
            self.domain_layer = 'multi'
            # there maybe more than one element with same strcture
            # if elements are basic type, we can save their in this domain
            # or elements are dict, we should build sub domain for every element
            if type(file)==list:
                if type(template[0]) == dict:
                    # multiple complex type elements
                    for i in range(len(file)):
                        new_domain = domain(file[i],template[0],key,domain_layer='sub_multi')
                        self.sub_domains.append(new_domain)
                elif template[0] in fhir_template:
                    # multiple complex type elements defined in fhir_template
                    temp = fhir_template[template[0]]
                    for i in range(len(file)):
                        new_domain = domain(file[i],temp,key,domain_layer='sub_multi')
                        self.sub_domains.append(new_domain)
                else:
                    self.domain_type = "value"
                    # multiple basic type elements
                    for i in range(len(file)):
                        self.value.append(str(file[i]))
            elif type(file)==dict:
                if type(template[0])==dict:
                    # only one element of complex type element
                    new_domain = domain(file,template[0],key,domain_layer='sub_multi')
                    self.sub_domains.append(new_domain)
                elif template[0] in fhir_template:
                    # only one element of complex type element defined in fhir_template
                    temp = fhir_template[template[0]]
                    new_domain = domain(file,temp,template[0],domain_layer='sub_multi')
                    self.sub_domains.append(new_domain)
                else:
                    print "unexcepted"
            else:
                # only one element of basic type element
                self.domain_type = "value"
                self.value.append(str(file))

        elif type(template)==dict:
            # one complex domain
            self.domain_type='complex'
            for k in template:
                if file.has_key(k):
                    new_domain = domain(file[k],template[k],k)
                    self.sub_domains.append(new_domain)
        elif template in basic_type:
            # one basic domain
            self.domain_type = "value"
            self.value.append(str(file))
        elif template in fhir_template:
            self.domain_type='complex'

            # one complex domain defined in fhir_template
            temp = fhir_template[template]
            for k in temp:
                if file.has_key(k):
                    new_domain = domain(file[k],temp[k],k)
                    self.sub_domains.append(new_domain)
        else:

            print "unexception occurace"



    def dump(self,indent):
        print indent*'\t'+self.key+'\t'+str(self.display_mask)+'\t'+str(self.primary_value)
        if self.value:
            for v in self.value:
                print (indent+1)*'\t'+v
        if self.sub_domains:
            for domain in self.sub_domains:
                domain.dump(indent+1)

    def set_primary_key(self):
        if self.key == 'extension':
            self.primary_key = 'url'
            self.primary_value = self.extra_extension_pv()
        elif self.key in primary_key:
            print 'set'
            print self.key
            self.primary_key = primary_key[self.key]
            self.primary_value = self.extra_value(self.primary_key)


    def init_seq(self,seq):
        if self.domain_layer=='multi':
            for domain in self.sub_domains:
                seq = domain.init_seq(seq)
            return seq
        else:
            self.set_primary_key()
            self.seq = seq
            return seq + 1

    def extra_extension_pv(self):
        for domain in self.sub_domains:
            if domain.key =='url':
                pv = domain.value[0].split('/')[-1]
                return pv
        print 'wrong date no pv found'
        return ''

    def button(self):
        html_file = '<button type="button" class="btn btn-success setting-btn" onclick="botton_toggle(this)" id="botton_'\
                    +str(self.seq)+'">Hide</button>'
        return html_file

    def masked_indicate(self):
        indicate = '<p class="fhir-masked">'\
                   +'<a tabindex="0" role="button" data-toggle="popover" data-placement="top" data-trigger="focus" title="'\
                   +masked_title+'" data-content="'\
                   +masked_info+'">'\
                   +'<span class="label label-default">'+masked_mark+'</span>'+'</a>'+'</p>'
        return indicate

    def class2html(self,kind=None):

        if kind == 'surface':

            if self.domain_type=='value':

                html_file = '<div class="fhir-single-item" id="item_' + str(self.seq) + '">'
                # key column
                html_file += '<div class="fhir-key col-sm-3"><p>' + self.key +'</p></div>'
                # vlaue column
                html_file += '<div class="fhir-value col-sm-6">'
                for v in self.value:
                    html_file += '<p>' + str(v) + '</p>'
                html_file += '</div>'
                #button column
                html_file += '<div class="fhir-button col-sm-3">'+ self.button()+'</div>'

                html_file += '</div>'


            elif self.domain_layer=='multi':
                html_file = '<h2>'+ self.key + '</h2>'
                for domain in self.sub_domains:
                    html_file += domain.class2html(kind='surface')
            elif self.domain_layer == 'sub_multi':

                if self.primary_key:

                    html_key = self.primary_value
                else:
                    html_key = ''



                html_file = '<div class="fhir-title"><h3>'+html_key+self.button()+'</h3></div>'
                html_file +=  '<div class="fhir-block" id="block_'+str(self.seq)+'">'

                for domain in self.sub_domains:
                    if not domain.key==html_key:
                        html_file += '<div class="fhir-item">' + domain.class2html() + '</div>'

                html_file += '</div>'
            elif self.domain_type == 'complex':
                html_file = '<h2>' + self.key + '</h2>'
                html_file +=  '<div class="fhir-title"><h3>'+self.key+self.button()+'</h3></div>'
                html_file +=  '<div class="fhir-block" id="block_'+str(self.seq)+'">'

                for domain in self.sub_domains:
                    html_file += '<div class="fhir-item">' + domain.class2html() + '</div>'

                html_file += '</div>'

            elif self.domain_type=='key':
                if self.primary_key:
                    html_key = self.primary_value
                else:
                    html_key = ''
                html_file = '<div class="fhir-title"><h3>'+ html_key + self.button() + '</h3></div>'
                html_file += '<div class="fhir-block" id="block_' + str(self.seq)+'">'

                for domain in self.sub_domains:
                    if not domain.key == self.primary_key:
                        html_file += '<div class="fhir-item">' + domain.class2html() + '</div>'

                html_file += '</div>'
            else:
                html_file = ''

                print 'unexpected occurance kind surface'
        elif kind=='sequence':

            html_file = '<div class="fhir-title"><h3>'+ self.key + self.button() + '</h3></div>'
            html_file += '<div class="fhir-block" id="block_' + str(self.seq)+'">'

            for domain in self.sub_domains:
                html_file += '<div class="fhir-item">' + domain.class2html() + '</div>'

            html_file += '</div>'



        else:

            if self.domain_type=='value':
                html_file = '<div class="fhir-key col-sm-3"><p>' + self.key + '</p></div>'

                html_file += '<div class="fhir-value col-sm-9">'
                for v in self.value:
                    html_file += '<p>' + str(v) + '</p>'
                html_file += '</div>'
            elif self.domain_layer == 'multi':
                #html_file = '<div class="fhir-title"><h3>'+self.key+'</h3></div>'
                html_file =  '<div class="fhir-block" >'

                for domain in self.sub_domains:
                    html_file += '<div class="fhir-item">' + domain.class2html() + '</div>'

                html_file += '</div>'
            elif self.domain_layer == 'sub_multi':
                html_file = ''
                for domain in self.sub_domains:
                    html_file += '<div class="fhir-item">' + domain.class2html() + '</div>'
            elif self.domain_type == 'complex':
                html_file = ''
                for domain in self.sub_domains:
                    html_file += '<div class="fhir-item">' + domain.class2html() + '</div>'
            elif self.domain_type == 'key':
                #html_file = '<div class="fhir-title"><h3>'+self.key+'</h3></div>'
                html_file =  '<div class="fhir-block" >'

                for domain in self.sub_domains:
                    html_file += '<div class="fhir-item">' + domain.class2html() + '</div>'

                html_file += '</div>'

            else:
                html_file = ''
                print 'unexcepted occurance kind None'


        return html_file

    def display_class2html(self,kind=None):

        if kind == 'surface':

            if self.domain_type=='value':
                if self.display_mask:
                    html_file = '<div class="fhir-single-item">'
                    html_file += '<div class="fhir-key col-sm-3"><p>' + self.key + '</p></div>'
                    html_file += '<dv class="fhir-value col-sm-9>' + self.masked_indicate() + '</div></div>'
                else:

                    html_file = '<div class="fhir-single-item" id="item_' + str(self.seq) + '">'
                    # key column
                    html_file += '<div class="fhir-key col-sm-3"><p>' + self.key +'</p></div>'
                    # vlaue column
                    html_file += '<div class="fhir-value col-sm-9">'
                    for v in self.value:
                        html_file += '<p>' + str(v) + '</p>'
                    html_file += '</div>'
                    #button column


                    html_file += '</div>'


            elif self.domain_layer=='multi':
                html_file = '<h2>'+ self.key + '</h2>'
                for domain in self.sub_domains:
                    html_file += domain.display_class2html(kind='surface')
            elif self.domain_layer == 'sub_multi':

                if self.primary_key:

                    html_key = self.primary_value
                else:
                    html_key = ''


                if self.display_mask:
                    html_file = '<div class="fhir-title"><h3>'+html_key+'</h3></div>'
                    html_file +=  '<div class="fhir-block">'+self.masked_indicate() + '</div>'

                else:
                    html_file = '<div class="fhir-title"><h3>'+html_key+'</h3></div>'
                    html_file +=  '<div class="fhir-block" id="block_'+str(self.seq)+'">'

                    for domain in self.sub_domains:
                        if not domain.key==html_key:
                            html_file += '<div class="fhir-item">' + domain.display_class2html() + '</div>'

                    html_file += '</div>'
            elif self.domain_type == 'complex':
                html_file = '<h2>' + self.key + '</h2>'

                if self.display_mask:
                    html_file +=  '<div class="fhir-title"><h3>'+self.key+'</h3></div>'
                    html_file +=  '<div class="fhir-block" >'+self.masked_indicate()+'</div>'
                else:

                    html_file +=  '<div class="fhir-title"><h3>'+self.key+'</h3></div>'
                    html_file +=  '<div class="fhir-block" id="block_'+str(self.seq)+'">'

                    for domain in self.sub_domains:
                        html_file += '<div class="fhir-item">' + domain.display_class2html() + '</div>'

                    html_file += '</div>'

            elif self.domain_type=='key':
                if self.primary_key:
                    html_key = self.primary_value
                else:
                    html_key = ''

                if self.display_mask:
                    html_file =  '<div class="fhir-title"><h3>'+self.key+'</h3></div>'
                    html_file +=  '<div class="fhir-block" >'+self.masked_indicate()+'</div>'
                else:
                    html_file = '<div class="fhir-title"><h3>'+ html_key + '</h3></div>'
                    html_file += '<div class="fhir-block" id="block_' + str(self.seq)+'">'

                    for domain in self.sub_domains:
                        if not domain.key == self.primary_key:
                            html_file += '<div class="fhir-item">' + domain.display_class2html() + '</div>'

                    html_file += '</div>'
            else:
                html_file = ''

                print 'unexpected occurance kind surface'
        elif kind=='sequence':
            if self.display_mask:
                html_file =  '<div class="fhir-title"><h3>'+self.key+'</h3></div>'
                html_file +=  '<div class="fhir-block" >'+self.masked_indicate()+'</div>'
            else:
                html_file = '<div class="fhir-title"><h3>'+ self.key  + '</h3></div>'
                html_file += '<div class="fhir-block" id="block_' + str(self.seq)+'">'

                for domain in self.sub_domains:
                    html_file += '<div class="fhir-item">' + domain.display_class2html() + '</div>'

                html_file += '</div>'



        else:

            if self.domain_type=='value':
                html_file = '<div class="fhir-key col-sm-3"><p>' + self.key + '</p></div>'

                html_file += '<div class="fhir-value col-sm-9">'
                for v in self.value:
                    html_file += '<p>' + str(v) + '</p>'
                html_file += '</div>'
            elif self.domain_layer == 'multi':
                #html_file = '<div class="fhir-title"><h3>'+self.key+'</h3></div>'
                html_file =  '<div class="fhir-block" >'

                for domain in self.sub_domains:
                    html_file += '<div class="fhir-item">' + domain.display_class2html() + '</div>'

                html_file += '</div>'
            elif self.domain_layer == 'sub_multi':
                html_file = ''
                for domain in self.sub_domains:
                    html_file += '<div class="fhir-item">' + domain.display_class2html() + '</div>'
            elif self.domain_type == 'complex':
                html_file = ''
                for domain in self.sub_domains:
                    html_file += '<div class="fhir-item">' + domain.display_class2html() + '</div>'
            elif self.domain_type == 'key':
                #html_file = '<div class="fhir-title"><h3>'+self.key+'</h3></div>'
                html_file =  '<div class="fhir-block" >'

                for domain in self.sub_domains:
                    html_file += '<div class="fhir-item">' + domain.display_class2html() + '</div>'

                html_file += '</div>'

            else:
                html_file = ''
                print 'unexcepted occurance kind None'


        return html_file

    def extra_value(self,key):
        for domain in self.sub_domains:
            if domain.key == key:
                return domain.value[0]
        return ''

    def mask_by_seq(self,seq):
        if self.seq ==seq:
            self.masked = True
        else:
            for domain in self.sub_domains:
                domain.mask_by_seq(seq)

    def get_masked(self):
        if self.domain_layer == 'multi':

            mask_domain = []
            all_masked = True
            for domain in self.sub_domains:
                if domain.masked:

                    if domain.primary_key:
                        mask_domain.append(domain.primary_value)
                    else:
                        print 'sub domain unable to identify'
                        mask_domain.append(domain.key)
                else:
                    all_masked = False
            if all_masked:
                return self.key,'fhir_mask'
            else:

                return self.key,mask_domain
        else:
            if self.masked:
                return self.key,'fhir_mask'
            else:
                return self.key,None

    def mask_broadcast(self,mask):
        print "mask broadcast first"
        if type(mask) == dict:
            for domain in self.sub_domains:
                if mask.has_key(domain.key):
                    domain.mask_braodcast(mask[domain.key])
        elif mask == 'fhir_mask':
            if self.domain_type=='value':
                self.display_mask = True
            else:
                for domain in self.sub_domains:
                    domain.display_mask = True
        else:
            print "mask broadcast"
            print mask
            for domain in self.sub_domains:
                print 'domain key\t'+str(domain.key)
                print self.primary_value
                if domain.primary_key and domain.primary_value in mask:
                    domain.display_mask = True



class patient:
    def __init__(self):
        self.sub_domains = []

    def load(self,file):
        temp = fhir_template['Patient']
        for key in temp:
            # build sub domain for every field in patient profile
            if file.has_key(key):

                new_domain = domain(file[key],temp[key],key)
                self.sub_domains.append(new_domain)

    def dump(self):
        for domain in self.sub_domains:
            domain.dump(0)

    def init_seq(self,seq):
        self.seq_start = seq
        for domain in self.sub_domains:
            seq = domain.init_seq(seq)
        self.seq_end = seq
        return seq+1

    def has_simple_domain(self):
        for domain in self.sub_domains:
            if domain.domain_type=='value':
                return True
        return False

    def mask_by_seq(self,seq):
        for domain in self.sub_domains:
            domain.mask_by_seq(seq)

    def mask_broadcast(self,mask):
        for domain in self.sub_domains:
            if domain.key in mask:
                domain.mask_broadcast(mask[domain.key])

    def get_masked(self):
        maksed = map(lambda domain:domain.get_masked(),self.sub_domains)
        masked = dict((key,value) for key,value in maksed if value)

        return masked

    def set_select_keys(self,select_keys):
        self.select_keys = select_keys

    def display_has_simple_domain(self):
        for domain in self.sub_domains:
            if domain.domain_type=='value' and domain.key in self.select_keys:
                return True
        return False


class observation:
    def __init__(self):
        self.sub_domains = []

    def load(self,file):
        temp = fhir_template['Observation']
        for f in file:
            new_domain = domain(f,temp,f['id'])
            self.sub_domains.append(new_domain)


    def dump(self):
        for domain in self.sub_domains:
            domain.dump(0)

    def init_seq(self,seq):
        self.seq_start = seq
        for d in self.sub_domains:
            for domain in d.sub_domains:
                seq = domain.init_seq(seq)
        self.seq_end = seq
        return seq+1

    def mask_by_seq(self,seq):
        for domain in self.sub_domains:
            domain.mask_by_seq(seq)

    def mask_broadcast(self,mask):
        for domain in self.sub_domains:
            if domain.key in mask:
                domain.mask_broadcast(mask[domain.key])

    def get_masked(self):
        ob_masked = {}
        for d in self.sub_domains:

            ob_maksed_raw = map(lambda domain:domain.get_masked(),d.sub_domains)

            ob_masked_filter = {}
            for k,v in ob_maksed_raw:
                if v:
                    ob_masked_filter[k]=v


            if ob_masked_filter:
                ob_masked[d.key] =ob_masked_filter




        return ob_masked

class sequences:
    def __init__(self):
        self.sub_domains = []

    def load(self,file):
        temp = fhir_template['Sequence']
        if type(file)==list:
            for f in file:
                new_domain = domain(f,temp,f['id'])
                self.sub_domains.append(new_domain)
        elif type(file) == dict:
            new_domain = domain(file,temp,file['id'])
            self.sub_domains.append(new_domain)
        else:
            print 'wrong sequence format'

    def dump(self):
        for domain in self.sub_domains:
            domain.dump(0)

    def init_seq(self,seq):
        self.seq_start = seq
        for domain in self.sub_domains:
            domain.seq = seq
            seq +=1
        self.seq_end = seq
        return seq+1

    def mask_by_seq(self,seq):
        for domain in self.sub_domains:
            domain.mask_by_seq(seq)

    def mask_broadcast(self,mask):
        for domain in self.sub_domains:
            if domain.key in mask:
                domain.diaplsy_mask = True

    def get_masked(self):
        se_maksed = []
        for domain in self.sub_domains:
            if domain.masked:
                se_maksed.append(domain.key)
        return se_maksed

def get_private_profile(patient_form,patient_class,observation,sequences,patient_json):
    """
    based on the patient's info and patient's private setting get the private profile

    :param patient_form: Form submit from the private setting page
    :param patient_class: Patient_info class
    :param patient_json: str type json file get from server
    :return: str type json file to be seved in our private server
    """
    '''
    for field in patient_form:
        if field.type == 'BooleanField' and field.data == True:
            seq =  int(field.name[14:])
            patient_class.mask_by_seq(seq)
            observation.mask_by_seq(seq)
            sequences.mask_by_seq(seq)


    masked_patient = patient_class.get_masked()
    masked_ob = observation.get_masked()
    masked_se = sequences.get_masked()

    new_dict = {}
    if 'id' in patient_json :
        new_dict['id'] = patient_json['id']

    if 'resourceType' in patient_json:
        new_dict['resourceType'] = patient_json['resourceType']

    if 'resourceID' in patient_json:
        new_dict['resourceID'] = patient_json['resourceID']

    new_dict['Policy'] = {}
    if masked_patient:
        new_dict['Policy']['Patient'] = masked_patient
    else:
        new_dict['Policy']['Patient'] = {}
    if masked_ob:
        new_dict['Policy']['Observation'] = masked_ob
    else:
        new_dict['Policy']['Observation'] = {}
    if masked_se:
        new_dict['Policy']['Sequence'] = masked_se
    else:
        new_dict['Policy']['Sequence'] = {}
    return json.dumps(new_dict)
    '''
    """
    based on the patient's info and patient's private setting get the private profile

    :param patient_form: Form submit from the private setting page
    :param patient_class: Patient_info class
    :param patient_json: str type json file get from server
    :return: str type json file to be seved in our private server
    """

    Hide_Info= ["observedAllele","text","species","coordinate","type","referenceAllele"]

    for field in patient_form:
        if field.type == 'BooleanField' and field.data == True:
            seq =  int(field.name[14:])
            patient_class.mask_by_seq(seq)
            observation.mask_by_seq(seq)
            sequences.mask_by_seq(seq)


    masked_patient = patient_class.get_masked()
    masked_ob= observation.get_masked()
    masked_se = sequences.get_masked()
    #print masked_ob
    #print masked_se


    new_dict = {}
    if 'id' in patient_json :
        new_dict['Identifier'] = new_dict['resourceID'] = patient_json['id']

    if 'resourceType' in patient_json:
        new_dict['resourceType'] = patient_json['resourceType']

    #if 'resourceID' in patient_json:
    #   new_dict['resourceID'] = patient_json['resourceID']

    new_dict['Policy'] = {}
    if masked_patient:
        new_dict['Policy'] = masked_patient
    else:
        new_dict['Policy'] = {}


    new_dict_ob = []
    # Point to patient
    for ob in observation:
        for k,v in masked_ob.items():
            if 'id' in ob and ob['id']==k:
                new_subdict= {}
                new_subdict['Identifier']= new_dict['Identifier']
                new_subdict['resourceType'] = 'Observation'

                if 'id' in seq :
                    new_subdict['resourceID'] = ob['id']

                new_subdict['Policy']=v
                new_dict_ob.append(new_subdict)
    '''
    new_dict_ob['Identifier'] = new_dict['Identifier']

    new_dict_ob['resourceType'] = 'Observation'

    if 'id' in observation :
        new_dict_ob['resourceID'] = observation['id']

    if masked_ob:
        new_dict_ob['Policy'] = {}
        for k,v in masked_ob.items():
            for key in v:
                new_dict_ob['Policy'][key] = 'fhir_mask'
    else:
        new_dict_ob['Policy'] = {}
    '''

    new_dict_seq= []

    for seq in sequences:
        for id in masked_se:
            if 'id' in seq and seq['id']==id:
                new_subdict= {}
                new_subdict['Identifier']= new_dict['Identifier']
                new_subdict['resourceType'] = 'Sequence'

                if 'id' in seq :
                    new_subdict['resourceID'] = seq['id']

                new_subdict['Policy']={}
                for k in seq.keys():
                    if k in Hide_Info:
                        new_subdict['Policy'][k]= 'fhir_mask'
                new_dict_seq.append(new_subdict)



    #print json.dumps(new_dict,indent=4)

    #retrive_patient_info(simple_key+complex_key,json.dumps(new_dict),json.dumps(jp.w))

    #print json.dumps(new_dict_seq)

    return new_dict,new_dict_ob,new_dict_seq


def profile_find(name,profiles,id=None):
    if name == 'Patient':
        for item in profiles:
            print type(item)
            if item['Policy_ResourceType'] == 'Patient':
                return item['Policy']
        return None
    elif name == 'Observation':
        ids= []
        for item in profiles:
            if item['Policy_ResourceType'] == 'Observation':
                ids.append(item['ResourceIdentifier'])
        return ids
    elif name == 'Sequence':
        ids = []
        for item in profiles:
            if item['Policy_ResourceType'] == 'Sequence':
                ids.append(item['ResourceIdentifier'])
        return ids
    else:
        return None

def display(selected_keys,private_profile,raw_json_patient,raw_ob,raw_seq):
    '''

    private_profile:= list
    :param selected_keys:
    :param private_profile:
    :param raw_json_patient:
    :param raw_ob:
    :param raw_seq:
    :return:
    '''
    num = 0
    p_inst = patient()
    p_inst.load(json.loads(raw_json_patient))
    num = p_inst.init_seq(num)


    patient_profile = profile_find('Patient',private_profile)
    #profile = json.loads(private_profile)['Policy']
    #print patient_profile
    #print p_inst
    p_inst.set_select_keys(selected_keys)
    if patient_profile is not None:
        p_inst.mask_broadcast(patient_profile)

    #print raw_ob
    ob_inst = observation()
    ob_inst.load(raw_ob)

    num = ob_inst.init_seq(num)
    ob_profile = profile_find('Observation',private_profile)

    if len(ob_profile)>0:
       ob_inst.mask_broadcast(ob_profile)

    seq_profile = profile_find('Sequence',private_profile)
    #print raw_seq
    seq_inst = sequences()
    for s in raw_seq:
        if isinstance(s, str):
            seq_inst.load(json.loads(s))
        else:
            seq_inst.load(s)

    num = seq_inst.init_seq(num)

    if len(seq_profile)>0:
        seq_inst.mask_broadcast(seq_profile)

    return p_inst,ob_inst,seq_inst

'''
def retrive_patient_info(selected_keys, private_profile, raw_json_patient,raw_ob,raw_seq):
    """

    :param selected_keys: the item of patient's profile that the doctor want to knew about
    :param private_profile: private profile in our private server
    :param raw_json_patient: str type json file about patient's info we get from the server
    :return: str type json file of patient info that the doctor can see, if some filed has been hidden,
                the value of it will be 'mask'
    """
    p_inst = patient()
    p_inst.load(json.loads(raw_json_patient))

    profile = json.loads(private_profile)['Policy']
    patient_json_file = p_inst.retrive_json(profile['Patient'],selected_keys)
    print patient_json_file
    print json.dumps(json.loads(patient_json_file),indent=4)

    ob = json.loads(raw_ob)
    print 'OBSERVATION'
    print ob
    print profile
    print profile['Observation']
    ob_profile = profile['Observation']
    if ob_profile.has_key(ob['id']):
        keys = ob_profile[ob['id']]
        for key in ob.keys():
            if key in keys:
                del ob[key]
    observation = json.dumps(ob)

    print json.dumps(json.loads(ob),indent=4)

    se_profile = json.loads(profile['Sequence'])
    se = map(lambda x:json.loads(x),raw_seq)
    tmp = list(sequence for sequence in se if not sequence['id'] in se_profile )
    sequences = map(lambda x:json.dumps(x),list)

    for s in sequences:
        print json.dumps(json.loads(s),indent=4)




    return patient_json_file,ob,sequences
'''

if __name__ == '__main__':
    #print template['Patient']
    file = jp.read_p
    #print json.dumps(file,indent=4)

    pa = patient()
    pa.load(file)
    pa.init_seq(0)
    pa.dump()


