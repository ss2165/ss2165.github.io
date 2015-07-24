from anvil import *
import physics
import draw
import math
import google.drive
import re

base_units =  ('s', 'a', 'cd', 'k', 'kg', 'm', 'mol')

class quant():
    def __init__(self, dicto = None):
        self.dict = {}
        if isinstance(dicto, dict):
            for key in dicto:
                self.dict[key] = dicto[key]

        for unit in base_units:
            if unit not in self.dict:
                self.dict[unit] = 0

        self.aliases = []
        self.name = ""
        self.st = ""

    def __pow__(self, value):
        for unit in self.dict:
            self.dict[unit] *= value
        return self

    def __mul__(self, other):
        newdict  = {}
        for key in self.dict:
             newdict[key] =  self.dict[key] + other.dict[key]
        return quant(newdict)

    def __imul__(self, other):
        for key in self.dict:
            self.dict[key] =  self.dict[key] + other.dict[key]
        return self

    def __div__(self, other):
        newdict  = {}
        for key in self.dict:
             newdict[key]=  self.dict[key] - other.dict[key]
        return quant(newdict)

    def __idiv__(self, other):
        for key in self.dict:
            self.dict[key] =  self.dict[key] - other.dict[key]
        return self

    def __str__(self):
        return self.name + ' :' + str(self.dict)


class Form1(Form1Template):

    def button_1_click (self, **event_args):
        # self.lbl.text = ""
        # args = self.txt.text.split('*')
        # result = quant()
        # for q in args:
        #     result *= self.defs[q]#TODO __iadd__
        # for i, val in result.dict.items():
        #     if val != 0:
        #         self.lbl.text += " {0}: {1}".format(i, val)


        print self.check(self.txt.text.replace(" ", ""))



    def check(self,st):
        qs = []
        if '(' in st:
            a= re.findall('\([^(]*?\)', st)
            for i in a:

                beg= st.find(i)
                end = beg + len(i) - 1
                qs.append((self.check(i[1:-1]), beg, end))
        elif '^' in st:
            a = re.findall('\w*?\^\d+\.?\d*', st)
            for i in a:
                beg= st.find(i)
                end = beg + len(i) - 1
                split = i.split('^')
                dim = split[0]
                power = float(split[1])
                qs.append((self.check(dim)[0][0]**power, beg, end))
        else:
            qs.append((self.defs[st], 0, len(st)-1))

        return qs

    def run(self,st):
        st = st.replace(" ", "")


        while '(' in st:
            st = self.parcheck(st)


    def mult(self, quant_list):
        result = quant()
        for quant in quant_list:
            result *= quant
        return result

    def parcheck(self, st):
        a= re.findall('\([^(]*?\)', st)

        for i in a:

            i2 = self.addcheck(i[1:-1])
            st = st.replace (i , i2)
        return st

    def powcheck(self, st):
        a = re.findall('\w*?\^\d+\.?\d*', st)

        for i in a:
            dim, power = i.split('^')


    def addcheck(self, st):
        a = re.split('\+|-', st)
        terms = []
        for i in a:
            print i
        return st

    def muldiv(self, st):
        pass


    def __init__(self):

        self.init_components()


        self.f = google.drive.app_files.unit_database
        self.data = self.f.worksheets[0]

        all_aliases = []

        self.defs = {}
        for row in self.data.rows:
            quantity = quant()
            for unit in base_units:
                quantity.dict[unit] =  float(row[unit])
            quantity.aliases = row['aliases'].replace(" ", "").split(",")
            quantity.name = row['name']

            #DUPLICATE CHECK DO NOT DELETE
            # for alias in quantity.aliases:
            #     if alias in all_aliases:
            #         print "Duplicate:", row['name'], alias
            #     else:
            #         all_aliases.append(alias)

            self.defs[row['name']] = quantity
