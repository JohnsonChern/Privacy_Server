import jsonexample as jp
import jsondump as jd
from flask.ext.wtf import Form
from wtforms import StringField, BooleanField
from wtforms.validators import DataRequired
import copy
import json

#reserved_word = 'test_fhir'

class private_Form(Form):
    pass





class json_struct:
    def __init__(self,key,type,value):
        self.type = type
        self.key = key
        self.value = value

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

    def set_level(self,level):

        if self.type == 'temp':
            self.level = level
            if self.value:
                map(lambda x:x.set_level(level+1),self.value)
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

    def append_to_list(self,class_list):
        if self.value:
            for item in self.value:
                class_list.append(item)
                item.append_to_list(class_list)


    def set_list(self,templist):
        templist.append(self.key)
        self.pos_list = copy.deepcopy(templist)
        if self.value:
            for item in self.value:
                item.set_list(templist)
        templist.pop()


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

def built(target):
    if type(target) == str or type(target) == unicode:
        return target
    elif type(target) == dict:
        li = []
        for key in target:
            li.append(json_struct(key,str(type(target[key])).split('\'')[1],build(target[key])))
        return li
    elif type(target) == list:
        li = []
        for item in target:
            if type(item) == str or type(item) == unicode:
                li.append(item)
            else:
                li.append(json_struct('None','list',build(item)))
        return li




def get_struct(target,reserved_word):
    output = json_struct('main','main',[])
    for line in target:
        build(line,output)
    return output


def build(target,body):
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
        item.append_to_list(class_list)



    return li,class_list



def strcture_json(json_file,reserved_word,fieldname):
    li = jd.json2list(json_file,reserved_word)
    output = get_struct(li,reserved_word)

    if output.value:
        map(lambda x:x.init_type(reserved_word),output.value)

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
        fieldkey=  fieldname+str(i)
        setattr(private_Form,fieldkey,BooleanField(fieldkey,default=False))



    form = private_Form()

    for item in class_list:
        print '\t'*item.get_level()+item.get_key()

    for item in class_list:
        print str(item.get_level())+'\t'+str(item.get_pred())




    return class_list,class_dict,form


def is_prefix(list1,list2):
    for i in range(len(list1)):
        if not list1[i]==list2[i]:
            return False
    return True


def set_mask(form,json_file,reserved_word,fieldname):
    length = len(fieldname)
    json_list,json_class = get_list_and_class(json_file, reserved_word)
    for field in form:
        if field.type == "BooleanField" and field.data == True:
            templist = json_class[int(str(field.id)[length:])].get_pos_list()
            for item in json_list:
                if is_prefix(templist,item):
                    item[-1] = 'mask'

    j = jd.list2json(json_list,reserved_word)

    print json.dumps(j)


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

