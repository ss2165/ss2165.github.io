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
                self.dict[unit] = 0.0

        self.aliases = []
        self.name = ""
        self.st = ""

    def __pow__(self, value):
        newdict  = {}
        for unit in self.dict:
            newdict[unit] = self.dict[unit]*value
        return quant(newdict)

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

    def btn_new_click (self, **event_args):
        st = self.txt_1.text.replace(" ", "")
        namee = self.txt_new.text
        ans = self.check(st)
        isin = False
        for name, quantity in self.defs.items():
            if quantity.dict == ans.dict:
                isin = True


        if not isin:
            ans.name = namee
            s= ans.dict['s']
            a = ans.dict['a']
            cd = ans.dict['cd']
            k = ans.dict['k']
            kg = ans.dict['kg']
            m = ans.dict['m']
            mol = ans.dict['mol']
            row = self.data.add_row(name=namee, s= s, a= a, cd = cd, k =k, kg = kg, m = m, mol = mol)


    def button_1_click (self, **event_args):
        # self.lbl.text = ""
        # args = self.txt.text.split('*')
        # result = quant()
        # for q in args:
        #     result *= self.defs[q]#TODO __iadd__
        # for i, val in result.dict.items():
        #     if val != 0:
        #         self.lbl.text += " {0}: {1}".format(i, val)

        self.lbl_match.visible = False
        st = self.txt_1.text.replace(" ", "")
        st2 =self.txt_2.text.replace(" ", "")

        self.results = []
        ans = self.check(st)
        ans2 = self.check(st2)
        ans.name = st
        ans2.name = st2
        for name, quantity in self.defs.items():
            if quantity.dict == ans.dict:
                ans.name = name
            if quantity.dict == ans2.dict:
                ans2.name = name

        self.lbl_1.text = str(ans)
        self.lbl_2.text = str(ans2)

        if ans.dict == ans2.dict:
            self.lbl_match.visible = True


    def check(self,st):
        ans = quant()
        if '^' in st:
            a = re.search('(\(?[^)^(]*?\)|\w+)?\^[\d\.-]*', st).group(0)
            beg = st.find(a)
            end = beg + len(a) -1
            split = a.split('^')
            dim = split[0]
            power = float(split[1])
            ans *= self.check(st[:beg])*(self.check(dim)**power)*self.check(st[end+1:])

        elif '(' in st and ')' in st:
            a= re.search('\([^(]*?\)', st).group(0)
            beg = st.find(a)
            end = beg + len(a) -1
            ans *= self.check(st[:beg])*self.check(a[1:-1])*self.check(st[end+1:])

        elif '/' in st:
            st = st.replace("(", "")
            st = st.replace(")", "")
            a = re.search('\/[\w\d^.]*', st).group(0)
            beg = st.find(a)
            end = beg + len(a) -1
            ans *= self.check(st[:beg])*self.check(st[end+1:-1])/self.check(a[1:])

        elif '*' in st:
            st = st.replace("(", "")
            st = st.replace(")", "")
            beg = st.find('*')
            ans *= self.check(st[:beg])*self.check(st[beg+1:])
        else:
            if st in self.defs:
                ans = self.defs[st]**1


        return ans

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
