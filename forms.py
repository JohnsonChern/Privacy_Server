from flask.ext.wtf import Form
from wtforms import StringField, BooleanField,PasswordField
from wtforms.validators import DataRequired
import private_extrace as pe

class SubmitForm(Form):
    identifier              = StringField('identifier', validators=[DataRequired(message=u'You must input patient\'s ID')])
    active                  = BooleanField('active',default=False)
    name                    = BooleanField('name',default=False)
    telecom                 = BooleanField('telecom',default=False)
    gender                  = BooleanField('gender',default=False)
    birthDate               = BooleanField('birthDate',default=False)
    address                 = BooleanField('address',default=False)
    maritalStatus           = BooleanField('maritalStatus',default=False)
    photo                   = BooleanField('address',default=False)
    contact_relationship    = BooleanField('contact_relationship',default=False)
    contact_name            = BooleanField('contact_name',default=False)
    remember_me             = BooleanField('address', default=False)

class AuthenticationForm(Form):
    identifier = StringField('identifier', validators=[DataRequired(message=u'You must input patient\'s ID')])

class SubmitDictForm():
    """docstring for SubmitDictForm"""

    def __init__(self, key, content):
        if type(content) is dict:
            self.key = key
            self.formtype = "dict"
            self.form = BooleanField(key, default=False)
            self.content = []
            for item in content:
                if type(content[item]) is list:
                    self.content.append(SubmitDictForm("", content[item]))
                else:
                    self.content.append(SubmitDictForm(item, content[item]))
        elif type(content) is list:
            self.key = key
            self.formtype = "list"
            self.form = BooleanField(key, default=False)
            self.content = SubmitDictForm("", content[0])
        else:
            self.key = key
            self.formtype = "normal"
            self.content = content
            self.form = BooleanField(key, default=False)


class UserLoginForm(Form):

    user_id = StringField('user id',validators = [DataRequired(message=u"You must imput user ID")])
    password = PasswordField('password', validators=[DataRequired(message=u"You must input password")])



class Patient_from(Form):
    """
    Field will be initialized by func set_patient_from_and_class
    """
    pass


class LoginForm(Form):
    """
    Field will be initialize by func set_query_form
    """
    identifier= StringField('identifier', validators=[DataRequired(message=u'You must input patient\'s ID')])
    disease = StringField('disease')

    #remember_me = BooleanField('address', default=False)


def set_relative_info(patient,observation,sequences):
    patient_info = pe.patient_info(patient)

    observation = pe.ob_info(observation)
    for se in sequences:
        observation.add_sequence(se)

    num = patient_info.field_num

    observation.init_seq(num)

    for i in range(observation.field_num):
        fieldkey=  "boolean_field_"+str(i)
        setattr(Patient_from,fieldkey,BooleanField(fieldkey,default=False))

    form = Patient_from()
    return form,patient_info,observation

def set_query_form():
    patient_info_key = pe.get_option()
    for i in range(len(patient_info_key)):
        setattr(LoginForm,patient_info_key[i],BooleanField(patient_info_key[i],default=False))

    form = LoginForm(csrf_enabled=False)
    return form



