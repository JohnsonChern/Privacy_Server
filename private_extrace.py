import jsonexample as jp
import jsondump as jd

import copy
import json



patient_template =json.loads('''
{
    "name":[
        {
            "use":"code",
            "text":"string",
            "family":"list",
            "given":"list",
            "prefix":"list",
            "period":"period"

        }
    ],
    "telecom":[
        {
            "system":"code",
            "value":"string",
            "use":"code",
            "rank":"int",
            "period":"period"
        }
    ],
    "gender":"code",
    "birthDate":"code",
    "multipleBirthBoolean":"boolean",
    "multipleBirthInteger":"integer",
    "deceasedDateTime":"dataTime",
    "deceasedBoolean":"boolean",
    "address":[
        {
            "use":"code",
            "type":"code",
            "text":"string",
            "line":"string",
            "city":"string",
            "district":"string",
            "state":"string",
            "state":"string",
            "postalCode":"string",
            "country":"string",
            "period":"period"
        }
    ],
    "contact":[
        {
            "relationship":[
                {
                    "coding":[
                        {
                            "system":"uri",
                            "version":"string",
                            "code":"code",
                            "display":"string",
                            "userSelected":"boolean"
                        }
                    ],
                    "text":"string"
                }
            ],
            "name":[
                {
                    "use":"code",
                    "text":"string",
                    "family":"list",
                    "given":"list",
                    "prefix":"list",
                    "period":"period"

                }
            ],
            "telecom":[
                {
                    "system":"code",
                    "value":"string",
                    "use":"code",
                    "rank":"int",
                    "period":"period"
                }
            ],
            "address":[
                {
                    "use":"code",
                    "type":"code",
                    "text":"string",
                    "line":"string",
                    "city":"string",
                    "district":"string",
                    "state":"string",
                    "state":"string",
                    "postalCode":"string",
                    "country":"string",
                    "period":"period"
                }
            ],
            "gender":"code",
            "period":"period"
        }
    ],
    "communication":[
        {
            "language":[
                {
                    "coding":[
                        {
                            "system":"uri",
                            "version":"string",
                            "code":"code",
                            "display":"string",
                            "userSelected":"boolean"
                        }
                    ],
                    "text":"string"
                }
            ],
            "preferred":"boolean"
        }
    ],
    "maritalStatus":[
        {
            "coding":[
                {
                    "system":"uri",
                    "version":"string",
                    "code":"code",
                    "display":"string",
                    "userSelected":"boolean"
                }
            ],
            "text":"string"
        }
    ]



}

'''
                             )

sequence_template = json.loads(
    '''
    {
        "type":"code",
        "patient":"Reference",
        "specimen":"Reference",
        "device":"Reference",
        "quantity":"Quantity",
        "species":"CodeableConcept",
        "variation":{
            "start":"integer",
            "end":"integer",
            "observedAllele":"string",
            "referenceAllele":"string",
            "cigar":"string"
        },
        "quality":{
            "start":"integer",
            "end":"integer",
            "score":"Quantity",
            "method":"string"
        },
        "allelicState":"CodeableConcept",
        "readCoverage":"integer",
        "pointer":["Reference"],
        "observedSeq":"string",
        "ovservation":"Reference",
        "structureVariation":{
            "precisionOfBoundaries":"string",
            "reportedaCGHRation":"decimal",
            "length":"integer",
            "outer":{
                "start":"integer",
                "end":"integer"
            },
            "inner":{
                "start":"integer",
                "end":"integer"
            }
        }
    }
    '''
)

Quantity_template = json.loads(
    '''
    {
        "value":"decimal",
        "comparator":"code",
        "unit":"string",
        "system":"uri",
        "code":"code"
    }
    '''
)

observation_template = json.loads(
    '''
    {
        "component":[
            {
                "code":"CodeableConcept",
                "value":"value_set",
                "dataAbsentReason":"CodeableConcept"
            }
        ],
        "subject":"Reference",
        "performer":["Reference"],
        "specimen":"Reference",
        "category":"CodeableConcept",
        "code":"CodeableConcept",
        "dataAbsentReason":"CodeableConcept",
        "interpretation":"CodeableConcept",
        "bodySite":"CodeableConcept",
        "method":"CodeableConcept"
    }
    '''
)

observation_value_set = json.loads(
    '''
    {
        "valueQuantity":{
            "value":"decimal",
            "comparator":"code",
            "unit":"string",
            "system":"uri",
            "code":"code"
        },
        "valueCodeableConcept":"CodeableConcept",
        "valueString":"string",
        "valueRange":"Range",
        "valueRatio":{
            "numerator":{
                "value":"decimal",
                "comparator":"code",
                "unit":"string",
                "system":"uri",
                "code":"code"
            },
            "denominator":{
                "value":"decimal",
                "comparator":"code",
                "unit":"string",
                "system":"uri",
                "code":"code"
            }
        },
        "valueSampledData":"SampledData",
        "valueAttachment":"Attachment",
        "valueTime":"time",
        "valueDateTime":"dateTime",
        "valuePeriod":"Period"
    }

    '''
)

Reference_template = json.loads(
    '''
    {
        "reference":"string",
        "display":"string"
    }
    '''
)

CodeableConcept_template = json.loads(
    '''
    {
        "coding":[
            {
                "system":"uri",
                "version":"string",
                "code":"code",
                "display":"string",
                "userSelected":"boolean"
            }
        ],
        "text":"string"
    }

    '''
)

complex_key = ['name','telecom','contact','address','animal','communication','maritalStatus']
simple_key = ['gender','birthDate']
choice_key = {'multipleBirth':['multipleBirthBoolean','multipleBirthInteger'],'deceased':['deceasedBoolean','deceasedDateTime']}

def get_option():
    """

    :return:list of key, item in the list is the field that doctor can choose to see
    """
    return complex_key+simple_key+choice_key.keys()

def extend_option(form):
    """

    :param form: form submit from doctor
    :return: list of key, item in the list is the field that doctor has choose,
            and selected item in choice_key will be extented to it's value
    """
    keys = []
    for field in form:
        if field.type =='BooleanField' and field.data == True:
            key = field.name
            if key in choice_key.keys():
                keys = keys + choice_key[key]
            elif key in complex_key or key in simple_key:
                keys.append(key)
    return keys

class observation_domain:
    def __init__(self,file,template,key = None,option = 'normal',attrs = 'norm',types = 'norm'):
        self.has_period = False
        self.has_comments = False
        self.multi = False
        self.sub_domain =[]
        self.value = None
        self.types = types
        self.has_sub_key = False
        self.is_value = False
        self.is_sub_multi = False
        self.seq = None
        self.attrs = attrs
        self.masked = False

        self.comments = None
        self.period = None
        self.multiple = False

        if key:
            self.key = key

        if option == 'multi':
            self.is_sub_multi = True
            if key == 'component':
                tmp = file.keys()
                self.key = 'multi_component'
                self.set_value_set(tmp,file)
                for key in tmp:
                    if key in template.keys():
                        new_domain = observation_domain(file[key],template[key],key)
                        self.sub_domain.append(new_domain)
            else:
                self.key = 'multi_'+key
                if not self.is_extend_value(file,template):
                    tmp = file.keys()
                    for key in tmp:
                        if key in template.keys():
                            new_domain = observation_domain(file[key],template[key],key)
                            self.sub_domain.append(new_domain)

        elif type(template) == list:

            self.multi = True
            if type(file) == list:
                for item in file:
                    new_domain = observation_domain(file=item,template=template[0],key=key,option='multi')
                    self.sub_domain.append(new_domain)
            elif type(file)==dict:
                new_domain = observation_domain(file = file,template=template[0],key=key,option='multi')
                self.sub_domain.append(new_domain)
            else:
                print 'component fault'

        elif type(template) == dict:
            for key in template.keys():
                if key in file.keys():
                    new_domain = observation_domain(file = file[key],template= template[key],key=key)
                    self.sub_domain\
                        .append(new_domain)



        elif type(template) == str or unicode:
            if type(file)==list and not template=='list':
                self.value = file[0]
                self.is_value = True
                self.types = type(file[0])
                print 'wanted '+template+' but get an list :',
                print file

            elif template == 'CodeableConcept':
                self.set_CodeableConcept(file)
            elif template == 'Reference':
                self.set_Reference(file)
            elif template == 'Period':
                self.set_Period(file)
            else:
                self.value = file
                self.is_value = True
                self.types = type(file)


    def multi_key(self):
        reserved_word = 'multi_'
        length = len(reserved_word)
        if self.key[:length]==reserved_word:
            return True
        else:
            return False


    def is_extend_value(self,file,template):
        if template == 'CodeableConcept':
            self.set_CodeableConcept(file)
            return True
        elif template == 'Reference':
            self.set_Reference(file)
            return True
        elif template == 'Period':
            self.set_Period(file)
            return True

        return False

    def set_id(self,id):
        self.id = id

    def set_Period(self,file):
        """
        Period has no self.value  self.is_value is false and has no self.sub_domain
        :param file:
        :return:
        """
        self.attrs = 'Period'
        self.period = file

    def set_Reference(self,file):
        self.attrs = 'Reference'
        for key in file.keys():
            if key in Reference_template.keys():
                new_domain = observation_domain(file = file[key],template=Reference_template[key],key=key)
                self.sub_domain.append(new_domain)

    def set_CodeableConcept(self,file):
        self.attrs = 'CodeableConcept'
        for key in file.keys():
            if key in CodeableConcept_template.keys():
                new_domain = observation_domain(file = file[key],template=CodeableConcept_template[key],key = key)
                self.sub_domain.append(new_domain)

    def set_seq(self,num):
        self.seq = num
        return num+1

    def mask_by_seq(self,seq):
        if self.seq == seq:
            print self.key
            print self.seq
            self.masked = True

    def set_value_set(self,keys,file):
        for key in keys:
            if key in observation_value_set.keys():
                new_domain = observation_domain(file[key],observation_value_set[key],key)
                self.sub_domain.append(new_domain)
                keys.remove(key)
                return True
        return False

    def dfs(self,num):
        self.seq = num
        num = num+1
        if self.sub_domain:
            for domain in self.sub_domain:
                num = domain.dfs(num)
        return num

    def dump(self,level):
        if self.multi_key():
            if self.sub_domain:
                for domain in self.sub_domain:
                    domain.dump(level)
        else:
            #print '\t'*level+self.key+'\t attr \t'+self.attrs
            if not self.is_value and  not self.attrs == 'Reference' and not self.attrs == 'CodeableConcept' and not self.attrs == 'Period' and not self.attrs=='norm':
                print '\t'*level+'!!!!!!!!'+self.attrs
            if self.has_comments:
                print '\t'*level+'comments: ',
                print self.comments

            if self.is_value:
                if self.types==list:
                    print '\t'*level+self.key+'\tlist\t',
                    print self.value
                elif self.types==dict:
                    print '\t'*level+self.key+'\tdict\t',
                    print self.value
                else:
                    print '\t'*level+self.key + '\t' + self.value
            else:
                print '\t'*level+self.key+'\t'+ self.attrs+'\t'+self.types
            if self.sub_domain:
                for domain in self.sub_domain:
                    domain.dump(level+1)

    def dfs(self,num):
        self.seq = num
        num = num+1
        if self.sub_domain:
            for domain in self.sub_domain:
                num = domain.dfs(num)
        return num

    def buttom(self):

        html_file = '<a href=# class="fake-button fake-button-small" >Hide</a>'
        html_file = '<button type="button" class="btn btn-success setting-btn" onclick="botton_toggle(this)" id="botton_'+str(self.seq)+'">Hide</button>'
        return html_file

    def class2html(self):

        if self.attrs == 'sequence':
            html_file = '<div class="title_row"><h3>'+self.buttom()+'</h3></div>'
            html_file = html_file + '<div class = "basic_layer" id = "basic_layer_'+str(self.seq)+'">'

            for domain in self.sub_domain:
                html_file = html_file + '<p>' + domain.class2html() + '</p>'

            html_file = html_file + '</div>'
            return html_file

        if self.types == 'basic_layer':
            html_file = '<div class="title_row"><h3>'+self.key+self.buttom()+'</h3></div>'
            html_file = html_file +'<div class = "basic_layer" id = "basic_layer_'+str(self.seq)+'">'

        else:
            html_file = ''

        if self.multi:
            html_file = html_file + '<div class="complex_layer">'
            for domain in self.sub_domain:
                html_file = html_file+domain.class2html()
            html_file = html_file + '</div>'
        elif self.is_sub_multi:
            if self.multi_key():
                html_key =''
            else:
                html_key = self.key
            html_file = html_file + '<div class="sub_title_row"><h4>'+html_key+'</h4></div>'
            html_file = html_file + '<div class="sub_layer">'
            for domain in self.sub_domain:
                html_file = html_file+'<p>'+ domain.class2html()+'</p>'
            html_file = html_file + '</div>'
        elif self.is_value:

            if self.types==list:
                html_file = '<div class="row"> <p  class="col-sm-3"  >'+self.key+'</p>'
                html_file = html_file + '<div class="col-sm-9">'
                for v in self.value:
                    html_file  = html_file+'<p>'+str(v)+'</p>'
                html_file = html_file + '</div></div>'
            else:
                html_file = '<div class="row"><p  class="col-sm-3"  >'+self.key+'</p>'+'<div class="col-sm-9">'+'<p>'+str(self.value)+'</p>'+'</div></div>'

        elif self.attrs == "CodeableConcept" or self.attrs == 'Reference':

            for domain in self.sub_domain:
                html_file = html_file+ domain.class2html()

        else:
            print self.attrs
            html_file = ''
            print 'unexcepted condition'

        if self.types == 'basic_layer':
            html_file = html_file + '</div>'
        return html_file

    def get_masked(self,option):
        if self.masked:
            if option=='key':
                return self.key,True
            elif option == 'id':
                return self.id,True
            else:
                print 'bad option'
        else:
            return None,False

class sequence_domain:
    def __init__(self,file,template,key = None,option = 'normal',attrs = 'norm',types = 'norm'):
        self.has_period = False
        self.has_comments = False
        self.multi = False
        self.sub_domain =[]
        self.value = None
        self.types = types
        self.has_sub_key = False
        self.is_value = False
        self.is_sub_multi = False
        self.seq = None
        self.attrs = attrs
        self.masked = False

        self.comments = None
        self.period = None
        self.multiple = False

        if key:
            self.key = key

        if option == 'multi':
            self.is_sub_multi = True
            if key == 'component':
                tmp = file.keys()
                self.key = 'multi_component'
                self.set_value_set(tmp,file)
                for key in tmp:
                    if key in template.keys():
                        new_domain = observation_domain(file[key],template[key],key)
                        self.sub_domain.append(new_domain)
            else:
                self.key = 'multi_'+key
                if not self.is_extend_value(file,template):
                    tmp = file.keys()
                    for key in tmp:
                        if key in template.keys():
                            new_domain = observation_domain(file[key],template[key],key)
                            self.sub_domain.append(new_domain)

        elif type(template) == list:

            self.multi = True
            if type(file) == list:
                for item in file:
                    new_domain = observation_domain(file=item,template=template[0],key=key,option='multi')
                    self.sub_domain.append(new_domain)
            elif type(file)==dict:
                new_domain = observation_domain(file = file,template=template[0],key=key,option='multi')
                self.sub_domain.append(new_domain)
            else:
                print 'component fault'


        elif type(template) == str or unicode:
            if type(file)==list and not template=='list':
                self.value = file[0]
                self.is_value = True
                self.types = type(file[0])
                print 'wanted '+template+' but get an list :',
                print file

            elif template == 'CodeableConcept':
                self.set_CodeableConcept(file)
            elif template == 'Reference':
                self.set_Reference(file)
            elif template == 'Period':
                self.set_Period(file)
            else:
                self.value = file
                self.is_value = True
                self.types = type(file)


    def multi_key(self):
        reserved_word = 'multi_'
        length = len(reserved_word)
        if self.key[:length]==reserved_word:
            return True
        else:
            return False

    def is_extend_value(self,file,template):
        if template == 'CodeableConcept':
            self.set_CodeableConcept(file)
            return True
        elif template == 'Reference':
            self.set_Reference(file)
            return True
        elif template == 'Period':
            self.set_Period(file)
            return True

        return False



    def set_Period(self,file):
        """
        Period has no self.value  self.is_value is false and has no self.sub_domain
        :param file:
        :return:
        """
        self.attrs = 'Period'
        self.period = file

    def set_Reference(self,file):
        self.attrs = 'Reference'
        for key in file.keys():
            if key in Reference_template.keys():
                new_domain = observation_domain(file = file[key],template=Reference_template[key],key=key)
                self.sub_domain.append(new_domain)

    def set_CodeableConcept(self,file):
        self.attrs = 'CodeableConcept'
        for key in file.keys():
            if key in CodeableConcept_template.keys():
                new_domain = observation_domain(file = file[key],template=CodeableConcept_template[key],key = key)
                self.sub_domain.append(new_domain)


    def set_value_set(self,keys,file):
        for key in keys:
            if key in observation_value_set.keys():
                new_domain = observation_domain(file[key],observation_value_set[key],key)
                self.sub_domain.append(new_domain)
                keys.remove(key)
                return True
        return False

    def dfs(self,num):
        self.seq = num
        num = num+1
        if self.sub_domain:
            for domain in self.sub_domain:
                num = domain.dfs(num)
        return num

    def dump(self,level):
        if self.multi_key():
            if self.sub_domain:
                for domain in self.sub_domain:
                    domain.dump(level)
        else:
            #print '\t'*level+self.key+'\t attr \t'+self.attrs
            if not self.is_value and  not self.attrs == 'Reference' and not self.attrs == 'CodeableConcept' and not self.attrs == 'Period' and not self.attrs=='norm':
                print '\t'*level+'!!!!!!!!'+self.attrs
            if self.has_comments:
                print '\t'*level+'comments: ',
                print self.comments

            if self.is_value:
                if self.types==list:
                    print '\t'*level+self.key+'\tlist\t',
                    print self.value
                elif self.types==dict:
                    print '\t'*level+self.key+'\tdict\t',
                    print self.value
                else:
                    print '\t'*level+self.key + '\t' + self.value
            else:
                print '\t'*level+self.key+'\t'+ self.attrs+'\t'+self.types
            if self.sub_domain:
                for domain in self.sub_domain:
                    domain.dump(level+1)

    def dfs(self,num):
        self.seq = num
        num = num+1
        if self.sub_domain:
            for domain in self.sub_domain:
                num = domain.dfs(num)
        return num

    def buttom(self):

        html_file = '<a href=# class="fake-button fake-button-small" >Hide</a>'
        html_file = '<button type="button" class="btn btn-success setting-btn" onclick="botton_toggle(this)" id="botton_'+str(self.seq)+'">Hide</button>'
        return html_file

    def class2html(self):

        if self.types == 'basic_layer':
            html_file = '<div class="title_row"><h3>'+self.key+self.buttom()+'</h3></div>'
            html_file = html_file +'<div class = "basic_layer" id = "basic_layer_'+str(self.seq)+'">'

        else:
            html_file = ''

        if self.multi:
            html_file = html_file + '<div class="complex_layer">'
            for domain in self.sub_domain:
                html_file = html_file+domain.class2html()
            html_file = html_file + '</div>'
        elif self.is_sub_multi:
            if self.multi_key():
                html_key =''
            else:
                html_key = self.key
            html_file = html_file + '<div class="sub_title_row"><h4>'+html_key+'</h4></div>'
            html_file = html_file + '<div class="sub_layer">'
            for domain in self.sub_domain:
                html_file = html_file+'<p>'+ domain.class2html()+'</p>'
            html_file = html_file + '</div>'
        elif self.is_value:

            if self.types==list:
                html_file = '<div class="row"> <p  class="col-sm-3"  >'+self.key+'</p>'
                html_file = html_file + '<div class="col-sm-9">'
                for v in self.value:
                    html_file  = html_file+'<p>'+str(v)+'</p>'
                html_file = html_file + '</div></div>'
            else:
                html_file = '<div class="row"><p  class="col-sm-3"  >'+self.key+'</p>'+'<div class="col-sm-9">'+'<p>'+str(self.value)+'</p>'+'</div></div>'

        elif self.attrs == "CodeableConcept" or self.attrs == 'Reference':

            for domain in self.sub_domain:
                html_file = html_file+ domain.class2html()

        else:
            print self.attrs
            html_file = ''
            print 'unexcepted condition'

        if self.types == 'basic_layer':
            html_file = html_file + '</div>'
        return html_file



class patient_info_domain:
    def __init__(self,file,template,key=None,option='normal',attrs='norm'):
        self.has_period = False
        self.has_comments = False
        self.multi = False
        self.sub_domain = []
        self.value = None
        self.type = 'norm'
        self.has_sub_key = False
        self.is_value = False
        self.is_sub_multi = False
        self.seq = None
        self.attrs = attrs
        self.masked = False

        self.comments = None
        self.period = None
        self.multiple = False
        #print key
        #print template
        #print file

        if key:
            '''
            multi item use the value of key 'use' as it's key, which hasn't been found yet
            '''
            self.key = key

        if option=='multi':
            self.is_sub_multi = True

            tmp = file.keys()

            if 'use' in file.keys():
                self.key = file['use']
                tmp.remove('use')
            else:
                self.key = 'multi_'+key

            tmp = self.set_period(file,tmp)
            tmp = self.set_comments(file, tmp)
            for key in tmp:
                if key in template.keys():
                    new_domain = patient_info_domain(file[key],template[key],key)
                    self.sub_domain.append(new_domain)

        elif type(template) == list:
            if self.attrs == 'complex_domain':
                attrs_option = 'basic_layer'
            else:
                attrs_option = 'norm'
            self.multi = True
            if type(file)==list:
                for item in file:
                    new_domain = patient_info_domain(file=item,template=template[0],key=key,option='multi',attrs=attrs_option)
                    self.sub_domain.append(new_domain)
            elif type(file)==dict:
                new_domain = patient_info_domain(file=file,template=template[0],key=key,option='multi',attrs = attrs_option)
                self.sub_domain.append(new_domain)
            else:
                print 'multi fault'

        elif type(template) == dict:
            print template
            self.type=dict
            tmp = file.keys()
            tmp = self.set_period(file,tmp)
            tmp = self.set_comments(file, tmp)
            for key in tmp:
                print key
                if key in template.keys():
                    print key
                    new_domain = patient_info_domain(file[key],template[key],key)
                    self.sub_domain.append(new_domain)


        elif type(template) == str or unicode:
            if type(file)==list and not template=='list':
                self.value = file[0]
                self.is_value = True
                self.type = type(file[0])
                print 'wanted '+template+' but get an list :',
                print file
                #print file[0]
            else:
                self.value = file
                self.is_value = True
                self.type = type(file)


    def set_period(self,file,key_list):
        if 'period' in key_list:
            self.has_period = True
            self.period = file['period']
            key_list.remove('period')

        return key_list

    def set_comments(self, file, key_list):
        if 'fhir_comments' in key_list:
            self.has_comments = True
            self.comments = file['fhir_comments']
            key_list.remove('fhir_comments')

        return key_list

    def inner_key(self):
        reserved_word = 'multi_'
        length = len(reserved_word)
        if self.key[:length]==reserved_word:
            return False
        else:
            return True

    def dfs(self,num):
        self.seq = num
        num = num+1
        if self.sub_domain:
            for domain in self.sub_domain:
                num = domain.dfs(num)
        return num

    def dump(self,level):
        print self.key+'\t attr \t'+self.attrs
        if not self.is_value and not self.multi and not self.is_sub_multi:
            print '\t'*level+'!!!!!!!!'
        if self.has_comments:
            print '\t'*level+'comments: ',
            print self.comments

        if self.has_period:
            print '\t'*level+'period: (',
            if self.period.has_key('start'):
                print self.period['start'],
            print ' - ',
            if self.period.has_key('end'):
                print self.period['end'],
            print ' )'

        if self.is_value:
            if self.type==list:
                print '\t'*level+self.key+'\tlist\t',
                print self.value
            elif self.type==dict:
                print '\t'*level+self.key+'\tdict\t',
                print self.value
            else:
                print '\t'*level+self.key + '\t' + self.value
        else:
            print '\t'*level+self.key
        if self.sub_domain:
            for domain in self.sub_domain:
                domain.dump(level+1)

    def class2html(self):
        if self.attrs=='simple_domain':
            html_file = '<div class="row simple_domain" id="fhir_value_'+str(self.seq)+'"> <p class="col-sm-4"> '+self.key+'</p>'
            html_file = html_file + '<div class="col-sm-5"">'+'<p>'+str(self.value)+'</p></div>'
            html_file = html_file + '<div class="col-sm-3">'+self.buttom()+'</div></div>'



        elif self.is_value:

            if self.type==list:
                html_file = '<div class="row"> <p  class="col-sm-3"  >'+self.key+'</p>'
                html_file = html_file + '<div class="col-sm-9">'
                for v in self.value:
                    html_file  = html_file+'<p>'+str(v)+'</p>'
                html_file = html_file + '</div></div>'
            else:
                html_file = '<div class="row"><p  class="col-sm-3"  >'+self.key+'</p>'+'<div class="col-sm-9">'+'<p>'+str(self.value)+'</p>'+'</div></div>'
        elif self.multi:
            html_file = '' #'<h3>'+self.key+'</h3>'
            for domain in self.sub_domain:
                html_file = html_file+domain.class2html()
        elif self.is_sub_multi:
            html_file =''
            if self.attrs=='basic_layer':
                if self.inner_key():
                    html_key = self.key
                else:
                    html_key = ''

                html_file = '<div class="title_row"><h3>'+html_key+self.period2html()+self.buttom()+'</h3></div>'


            html_file = html_file + '<div class = "basic_layer" id = "basic_layer_'+ str(self.seq)+'">'
            html_file = html_file + self.comments2html()

            for domain in self.sub_domain:
                html_file = html_file+'<p>' + domain.class2html()+'</p>'

            html_file = html_file + '</div>'

        else:
            html_file = ''
            print 'unexcepted condition'

        return html_file

    def buttom(self):

        html_file = '<a href=# class="fake-button fake-button-small" >Hide</a>'
        html_file = '<button type="button" class="btn btn-success setting-btn" onclick="botton_toggle(this)" id="botton_'+str(self.seq)+'">Hide</button>'
        return html_file

    def comments2html(self):
        if self.has_comments:
            html_file = '<comments>'
            for comment in self.comments:
                html_file = html_file + '<p>'+ comment+'</p>'
            html_file = html_file + '</comments>'
        else:
            html_file = ''
        return html_file

    def period2html(self):
        if self.has_period:
            html_file = '<period> ('
            if self.period.has_key('start'):
                html_file = html_file +self.period['start']
            html_file = html_file + ' - '
            if self.period.has_key('end'):
                html_file = html_file +self.period['end']
            html_file = html_file + ')</period>'
        else:
            html_file=''

        return html_file

    def class2json(self):
        json_file = ''

        if self.is_sub_multi:
            flag = True
            json_file = '{'
            if self.inner_key():
                json_file = json_file + ' "use": ' +'"' + self.key + '"'
                flag = False
            for domain in self.sub_domain:
                if flag:
                    flag = False
                else:
                    json_file = json_file + ','
                json_file = json_file + domain.class2json()
            json_file = json_file +  '}'
        elif self.is_value:
            flag = True
            json_file = '"'+self.key+'":'
            if self.type==list:
                json_file = json_file+'['
                for v in self.value:
                    if flag:
                        flag = False
                    else:
                        json_file = json_file + ','
                    json_file = json_file + '"' + v + '"'
                json_file = json_file +']'
            else:
                json_file = '"'+self.key+'":"' + str(self.value) +'"'
        elif self.multi:
            flag = True
            json_file = '"'+ self.key+'":['
            for domain in self.sub_domain:
                if flag:
                    flag = False
                else:
                    json_file = json_file +','
                json_file = json_file + domain.class2json()
            json_file = json_file+']'

        return json_file

    def retrive_json(self,profile=None):
        if profile:
            json_file = ''
            flag = True
            json_file = '"' + self.key +'":['
            for domain in self.sub_domain:
                if not domain.key in profile:
                    if flag:
                        flag = False
                    else:
                        json_file = json_file +','
                    json_file = json_file + domain.retrive_json()
            json_file = json_file + ']'
        else:
            json_file = self.class2json()

        return json_file



    def mask_by_seq(self,seq):
        if self.seq == seq:
            print self.key
            print self.seq
            self.masked = True
        elif self.sub_domain:
            for domain in self.sub_domain:
                domain.mask_by_seq(seq)

    def get_masked_sub_domain(self):
        if self.attrs == 'complex_domain':
            mask_domain = []
            all_masked = True
            for domain in self.sub_domain:
                if domain.masked:
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


class ob_info:

    def __init__(self,file):
        if file:
            if file.has_key('id'):
                self.id = file['id']
            else:
                print 'has no id'
            self.sub_domains = []
            self.sequences = []
            for key in observation_template.keys():
                if key in file.keys():
                    new_domain = observation_domain(file = file[key],template= observation_template[key],key=key,types='basic_layer')
                    self.sub_domains.append(new_domain)
            #self.init_seq()
        else:
            self.sub_domains = []
            self.sequences = []

    def add_sequence(self,file):
        seq_seq = len(self.sequences)
        new_domain = observation_domain(file=file, template = sequence_template,key = 'sequence_'+str(seq_seq),attrs = 'sequence')
        if file.has_key('id'):
            new_domain.set_id(file['id'])
        else:
            print 'has no id'
        self.sequences.append(new_domain)

    def mask_by_seq(self,seq):
        for domain in self.sub_domains:
            domain.mask_by_seq(seq)
        for s in self.sequences:
            s.mask_by_seq(seq)


    def init_seq(self,num):
        if self.sub_domains:
            for domain in self.sub_domains:
                num = domain.dfs(num)
        if self.sequences:
            for domain in self.sequences:
                num = domain.set_seq(num)
        self.field_num = num

    def dump(self):
        for domain in self.sub_domains:
            domain.dump(0)

    def class2json(self):
        flag = True
        json_file = '{'
        for domain in self.sub_domains:

            if flag:
                flag = False
            else:
                json_file = json_file + ','

            json_file = json_file + domain.class2html()

        json_file = json_file + '}'
        return json_file

    def get_masked(self):
        ob_maksed_raw = map(lambda domain:domain.get_masked(option='key'),self.sub_domains)
        ob_masked = list(key for key,value in ob_maksed_raw if value)
        if ob_masked:
            ob_masked = {self.id:ob_masked}
        else:
            ob_maksed = None

        se_maksed = map(lambda domain:domain.get_masked(option='id'),self.sequences)
        se_masked = list(key for key,value in se_maksed if value)

        return ob_masked,se_masked


class seq_info:

    def __init__(self,file):
        self.sub_domains = []
        for key in sequence_template.keys():
            if key in file.keys():
                new_domain = sequence_domain(file = file[key], template= sequence_template[key], key=key, types='basic_layer')
                self.sub_domains.append(new_domain)
        self.init_seq()



    def init_seq(self):
        num = 1
        for domain in self.sub_domains:
            num = domain.dfs(num)
        self.field_num = num

    def dump(self):
        for domain in self.sub_domains:
            domain.dump(0)

    def class2json(self):
        flag = True
        json_file = '{'
        for domain in self.sub_domains:

            if flag:
                flag = False
            else:
                json_file = json_file + ','

            json_file = json_file + domain.class2html()

        json_file = json_file + '}'
        return json_file

    def class2html(self):
        pass




class patient_info:

    def __init__(self,file):
        self.sub_domains = []
        for key in complex_key:
            if key in file.keys():
                new_domain = patient_info_domain(
                    file=file[key],template=patient_template[key],key=key,attrs='complex_domain')
                self.sub_domains.append(new_domain)
        for key in simple_key:
            if key in file.keys():
                new_domain = patient_info_domain(
                    file=file[key],template=patient_template[key],key=key,attrs='simple_domain')
                self.sub_domains.append(new_domain)
        self.init_seq()

    def has_simple_domain(self):
        for domain in self.sub_domains:
            if domain.attrs=='simple_domain':
                return True
        return False

    def init_seq(self):
        num = 1
        for domain in self.sub_domains:
            num = domain.dfs(num)
        self.field_num = num

    def dump(self):
        for domain in self.sub_domains:
            domain.dump(0)

    def class2json(self):
        flag = True
        json_file = '{'
        for domain in self.sub_domains:

            if flag:
                flag = False
            else:
                json_file = json_file + ','

            json_file = json_file + domain.class2json()

        json_file = json_file + '}'
        return json_file

    def retrive_json(self,profile,selected_keys):
        flag = True
        json_file = '{'
        for domain in self.sub_domains:
            key = domain.key
            if key in selected_keys:
                if flag:
                    flag = False
                else:
                    json_file = json_file + ','

                if key in profile.keys():
                    if profile[key] == 'fhir_mask':
                        json_file = json_file + '"'+domain.key+'":"mask"'
                    else:
                        json_file = json_file + domain.retrive_json(profile[key])
                else:
                    json_file = json_file + domain.retrive_json()
        json_file = json_file + '}'

        return json_file

    def mask_by_seq(self,seq):
        for domain in self.sub_domains:
            domain.mask_by_seq(seq)

    def get_masked(self):
        maksed = map(lambda domain:domain.get_masked_sub_domain(),self.sub_domains)
        masked = dict((key,value) for key,value in maksed if value)


        return masked

def get_private_profile(patient_form,patient_class,observation,patient_json):
    """
    based on the patient's info and patient's private setting get the private profile

    :param patient_form: Form submit from the private setting page
    :param patient_class: Patient_info class
    :param patient_json: str type json file get from server
    :return: str type json file to be seved in our private server
    """

    for field in patient_form:
        if field.type == 'BooleanField' and field.data == True:
            seq =  int(field.name[14:])
            patient_class.mask_by_seq(seq)
            observation.mask_by_seq(seq)


    masked_patient = patient_class.get_masked()
    masked_ob,masked_se = observation.get_masked()

    print masked_ob
    print masked_se


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


    #print json.dumps(new_dict,indent=4)

    #retrive_patient_info(simple_key+complex_key,json.dumps(new_dict),json.dumps(jp.w))

    print json.dumps(new_dict)

    return json.dumps(new_dict)





def retrive_patient_info(selected_keys, private_profile, raw_json_patient,raw_ob,raw_seq):
    """

    :param selected_keys: the item of patient's profile that the doctor want to knew about
    :param private_profile: private profile in our private server
    :param raw_json_patient: str type json file about patient's info we get from the server
    :return: str type json file of patient info that the doctor can see, if some filed has been hidden,
                the value of it will be 'mask'
    """
    patient = patient_info(json.loads(raw_json_patient))
    try:
        profile = json.loads(private_profile)['Policy']
        patient_json_file = patient.retrive_json(profile['Patient'],selected_keys)
    except:
        patient_json_file = patient.retrive_json({},selected_keys)

    ob = json.loads(raw_ob)
    ob_profile = json.loads(profile['Observation'])
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



def ob_test():
    e = jp.seq_ep
    o = jp.ob_ep
    print e
    ob = ob_info([])
    ob.add_sequence(e)
    for domain in ob.sequences:
        print domain.id
        print domain.class2html()


if __name__ =='__main__':
    ob_test()






