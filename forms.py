from flask.ext.wtf import Form
from wtforms import StringField, BooleanField
from wtforms.validators import DataRequired

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

class SubmitDictForm(Form):
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
        