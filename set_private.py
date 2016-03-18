import jsonexample as jp
import jsondump as jd
from flask.ext.wtf import Form
from wtforms import StringField, BooleanField
from wtforms.validators import DataRequired
import copy
import json

#reserved_word = 'test_fhir'

class private_Form(Form):
    """
    WTForms for private profile, which will be init in strcture_json()
    """
    pass


class json_struct:

    def __init__(self,key,type,value):
        self.type = type
        self.key = key
        self.value = value
        self.attr = None
        self.carry_data = False
        self.data = None

    def dump(self,level):
        if self.type == 'value':
            #print ' '*level+str(self.type)
            print ' '*level+self.key
        elif self.type == 'temp':
            #print '\n'
            if self.value:
                map(lambda x:x.dump(level+4),self.value)
        else:
            print ' '*level+self.key
            if self.value:
                map(lambda x:x.dump(level+4),self.value)

    def find_by_key(self,key):
        if self.value:
            for item in self.value:
                if item.key == key:
                    return item
            return self
        return self

    def set_by_key(self,key):
        if self.value:
            for item  in self.value:
                if item.key == key:
                    return item
            self.value.append(json_struct(key,'None',[]))
            return self.value[-1]
        self.value = []
        self.value.append(json_struct(key,'None',[]))
        return self.value[-1]

    def init_type(self,reserved_word):
        if self.key[:len(reserved_word)] == reserved_word:
            self.type = 'temp'
            if self.value:
                map(lambda x:x.init_type(reserved_word),self.value)
        elif not self.value:
            self.type = 'value'
        else:
            self.type = 'key'
            if self.value:
                map(lambda x:x.init_type(reserved_word),self.value)

    def init_attr(self):
        if self.value:
            map(lambda x:x.init_attr(),self.value)
        if self.type == 'value':
            self.attr = 'value'
            self.carry_data = True
            self.data = self.key
        elif self.type == 'temp':
            if self.key_of_value() or len(self.value)==1:
                self.attr = 'hidden_temp_layer'
            else:
                self.attr = 'show_temp_layer'

        elif self.key_of_value():
            self.attr = 'key_of_value'
        else:
            self.attr = 'fold'
            self.hiden_layer_reduce()


    def hiden_layer_reduce(self):
        if len(self.value)==1 and self.value[0].type=='temp':
            self.value[0].attr = 'hidden_temp_layer'





    def key_of_value(self):
        if not self.value:
            return False
        else:
            for item in self.value:
                if not item.carry_data:
                    print "doesn't carry data"
                    item.dump(0)
                    return False

        tmp = []
        for item in self.value:
            if len(item.data)==1 and type(item.data)==list:
                tmp.append(item.data[0])
            else:
                tmp.append(item.data)

        if self.type=='temp':
            self.carry_data = True
        self.data = tmp
        return True


    def set_level(self,level):

        if self.attr == 'hidden_temp_layer':
            self.level = level
            if self.value:
                map(lambda x:x.set_level(level),self.value)
        else:
            self.level = level
            if self.value:
                self.level = level
                map(lambda x:x.set_level(level+1),self.value)

    def dump_level(self):
        print self.level
        if self.value:
            map(lambda x:x.dump_level(),self.value)

    def dfs(self,num):
        self.seq = num
        num = num+1
        if self.value:
            for item in self.value:
                num = item.dfs(num)
        return num

    def append_to_list(self,class_list,recude=True):
        if self.value:
            if recude==True:
                for item in self.value:
                    if not (item.attr=='hidden_temp_layer' or item.type=='value'):
                        class_list.append(item)
                    item.append_to_list(class_list)
            else:
                for item in self.value:
                    class_list.append(item)
                    item.append_to_list(class_list,False)

    def set_list(self,templist):
        templist.append(self.key)
        self.pos_list = copy.deepcopy(templist)
        if self.value:
            for item in self.value:
                item.set_list(templist)
        templist.pop()


    def dump_html(self):
        pass


    def get_seq(self):
        return self.seq

    def get_level(self):
        return self.level

    def get_key(self):
        return self.key

    def set_pred(self,level):
        self.pred = level

    def set_succ(self,level):
        self.succ = level

    def get_pred(self):
        return self.pred

    def get_succ(self):
        return self.succ

    def get_pos_list(self):
        return self.pos_list

    def get_type(self):
        return self.type

    def set_attr(self,attr):
        self.attr = attr

    def get_attr(self):
        return self.attr

    def set_content(self,content):
        self.content = content

    def get_content(self):
        return self.content




def get_struct(target,reserved_word):
    """
    build main json_struct class from input dict
    :param target: dict, the result of json.loads
    :param reserved_word:mid-layer:
    :return:json_struct class
    """
    output = json_struct('main','main',[])
    for line in target:
        build(line,output)
    return output


def build(target,body):
    """
    set the value in target by its keys into json_struct class
    :param target: list,[key_0,key_1,...,key_n,value]
    :param body:json_struct class
    :return:
    """
    item = reduce(lambda x,y: x.set_by_key(y),target,body)
    item.value = None


def get_list_and_class(json_file, reserved_word):
    li = jd.json2list(json_file,reserved_word)
    output = get_struct(li,reserved_word)

    if output.value:
        map(lambda x:x.init_type(reserved_word),output.value)

    map(lambda x:x.set_level(0),output.value)

    num = 0
    for item in output.value:
        num = item.dfs(num)


    templist = []
    for item in output.value:
        item.set_list(templist)

    class_list = []
    for item in output.value:
        class_list.append(item)
        item.append_to_list(class_list,False)



    return li,class_list


def strcture_json(json_file,reserved_word,fieldname):
    li = jd.json2list(json_file,reserved_word)
    output = get_struct(li,reserved_word)

    if output.value:
        map(lambda x:x.init_type(reserved_word),output.value)
        map(lambda x:x.init_attr(),output.value)

    map(lambda x:x.set_level(0),output.value)


    num = 0
    for item in output.value:
        num = item.dfs(num)



    class_list = []
    for item in output.value:
        class_list.append(item)
        item.append_to_list(class_list)

    dict_temp = []
    for item in class_list:
        dict_temp.append([item.get_key(),item])


    class_dict = dict((key,value) for key, value in dict_temp)


    class_list[len(class_list)-1].set_succ(-1)
    for i in range(0,len(class_list)-1):
        class_list[i].set_succ(class_list[i+1].get_level())


    class_list[0].set_pred(-1)
    for i in range(1,len(class_list)):
        class_list[i].set_pred(class_list[i-1].get_level())



    for i in range(len(class_list)):
        fieldkey=  fieldname+str(class_list[i].get_seq())
        setattr(private_Form,fieldkey,BooleanField(fieldkey,default=False))



    form = private_Form()

   # for item in class_list:
   #    print '\t'*item.get_level()+item.get_key()

   # for item in class_list:
   #     print str(item.get_level())+'\t'+str(item.get_pred())




    return class_list,class_dict,form


def is_prefix(list1,list2):
    for i in range(len(list1)):
        if not list1[i]==list2[i]:
            return False
    return True


def package(json_file,masked_part):
    """

    :param json_file: json.loads(raw_json file)
    :param masked_part: masked part of user profile in the form of python dict obj
    :return: packaged private profile in the form of json
    """

    masked = json.dumps(masked_part)
    new_dict = {}
    if 'id' in json_file :
        new_dict['id'] = json_file['id']

    if 'resourceType' in json_file:
        new_dict['resourceType'] = json_file['resourceType']

    if 'resourceID' in json_file:
        new_dict['resourceID'] = json_file['resourceID']

    new_dict['Policy'] = masked_part

    return json.dumps(new_dict)


def set_mask(form,json_file,reserved_word,fieldname):
    """

    :param form: Contains item which user wanted to hind
    :param json_file: Original json file
    :param reserved_word: reserved word in json_file mark middle layer
    :param fieldname: reserved word in form
    :return:
    """

    length = len(fieldname)
    json_list,json_class = get_list_and_class(json_file, reserved_word)
    masked_list = []
    for field in form:
        if field.type == "BooleanField" and field.data == True:
            templist = json_class[int(str(field.id)[length:])].get_pos_list()
            for item in json_list:
                if is_prefix(templist,item):
                    item[-1] = 'mask'
                    if not item in masked_list:
                        masked_list.append(item)


    j = jd.list2json(json_list,reserved_word)

    print reserved_word
    for line in masked_list:
        print line
    masked_part = jd.list2json(masked_list,reserved_word)
    print masked_part


    final_file = package(json_file,masked_part)

    print json.dumps(masked_part,indent=4)



reserved_word = 'test'

if __name__ == '__main__':

    e = jp.s
    li = jd.json2list(e,reserved_word)
    output = get_struct(li,reserved_word)
    if output.value:
        map(lambda x:x.init_type(reserved_word),output.value)

    map(lambda x:x.dump(0),output.value)

    map(lambda x:x.set_level(0),output.value)

    num = 0
    for item in output.value:
        num = item.dfs(num)

    #map(lambda x:x.dump_level(), output.value)

    class_list = []
    for item in output.value:
        class_list.append(item)
        item.append_to_list(class_list)

    for item in class_list:
        print item.get_level(),
        print '\t',
        print item.get_seq()


   # di,li,form = strcture_json(e,reserved_word)



    #li = []
    #for key in e:
    #    li.append(json_struct(key,str(type(e[key])).split('\'')[1],build(e[key])))


    #profile = json_struct('main',list,li)
    #print str(type(profile))

    #print profile.value
    #profile.dump(0)

