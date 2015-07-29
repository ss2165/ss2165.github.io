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

    def find_name(self, dic):
        for q in dic:
            if self.dict == dic[q].dict:
                self.name = q
                return q
        return ""
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

    def check_dev_change (self, **event_args):
        self.txt_new.visible = self.check_dev.checked
        self.btn_new.visible = self.check_dev.checked
    def btn_new_click (self, **event_args):
        st = self.txt_1.text.replace(" ", "")
        namee = self.txt_new.text
        ans = self.check(st)
        isin = False

        for name, quantity in self.defs.items():
            if quantity.dict == ans.dict:
                isin = True

        if not isin:
            info = namee.split(',', 1)
            ans.name = info[0]
            if ans.name == "" or ans.name == " ":
                print "Provide new quantity name"
            aliases = ""
            if len(info)>1:
                aliases = info[1]
            row = self.data.add_row(name=info[0],aliases = aliases)
            for unit in ans.dict:
                row[unit] = ans.dict[unit]

        self.update_defs()

    def button_1_click (self, **event_args):
        self.lbl_terms.text = ""
        self.lbl_match.visible = False
        st = self.txt_1.text.replace(" ", "")
        st2 =self.txt_2.text.replace(" ", "")

        ans = self.check(st)
        ans2 = self.check(st2)


        self.lbl_1.text = str(ans)
        self.lbl_2.text = str(ans2)

        if ans.dict == ans2.dict:
            self.lbl_match.visible = True


    def update_defs(self):
        all_aliases = []

        self.defs = {}
        for row in self.data.rows:
            quantity = quant()
            for unit in base_units:
                quantity.dict[unit] =  float(row[unit])
            aliases = row['aliases'].replace(" ", "").split(",")
            if "" not in aliases:
                quantity.aliases = aliases
            quantity.name = row['name']

            #DUPLICATE CHECK DO NOT DELETE
            for alias in quantity.aliases:
                if alias in all_aliases and alias !=  "" and alias != " ":
                    print "Duplicate alias: quantity-", row['name'], "alias-", alias
                else:
                    all_aliases.append(alias)

            self.defs[row['name']] = quantity

    def add_check(self,st):
        ans = quant()
        a = re.findall(r'[^+-]*\(*[^)(]*\)+[\^\w/.*]*|\w+[^+-]*', st)
        if a == []:
            a = [""]

        if len(a)==1:
            st2 = a[0]
            if '(' in st2 and ')' in st2:
                paran= re.search(r'\([^(]*?\)', st2).group(0)
                beg = st2.find(paran)
                end = beg + len(paran) -1
                ans = self.add_check(st2[:beg])*self.add_check(paran[1:-1])*self.add_check(st2[end+1:])
            else:
                ans =  self.check(st2)

        elif len(a)>1:
            q= self.add_check(a[0])
            compatible_terms = True
            for i in a[1:]:
                curr = self.add_check(i)
                if curr.dict != q.dict and compatible_terms:
                    compatible_terms = False
                    self.lbl_terms.text = "Term dimensions mismatch\n"+ a[0]+ " and "+ i+ " do not have the same dimensions\n"
                    self.lbl_terms.text += a[0]+ " has dimension of: "+ q.name+ "\n"+ i+ " has dimension of: "+ curr.name
            if compatible_terms:
                ans = q
        ans.find_name(self.defs)
        return ans

    def check(self,st2):
        if len(st2)>0:
            if st2[0] == '(' and st2[-1] == ')':
                st2 = st2[1:-1]
        ans = quant()
        a = re.findall(r'[^+-]*\(*[^)(]*\)+[\^\w/.*]*|\w+[^+-]*', st2)
        if a == []:
            a = [""]
        print a
        if len(a)==1:
            st = a[0]
            if len(st)>0:
                if st[0] == '(' and st[-1] == ')':
                    st = st[1:-1]
            # if '(' in st2 and ')' in st2:
            #     paran= re.search(r'\([^(]*?\)', st2).group(0)
            #     beg = st2.find(paran)
            #     end = beg + len(paran) -1
            #     ans = self.add_check(st2[:beg])*self.add_check(paran[1:-1])*self.add_check(st2[end+1:])
            # else:
            if '/' in st:
                a = re.search(r'/[\w\d^.]*(\(?[^)(]*?\)|\w+)[\^\w.]*', st).group(0)
                beg = st.find(a)
                end = beg + len(a) -1
                ans *= self.check(st[:beg])*self.check(st[end+1:])/self.check(a[1:])

            elif '^' in st:
                a = re.search(r'\^-?[\d.]+', st).group(0)
                #a = re.search(r'(\(?[^)^(]*?\)|\w+)?\^[\d\.-]*', st).group(0)
                beg = st.find(a)
                end = beg + len(a) -1
                # split = a.split('^')
                # dim = split[0]
                power = float(a[1:])
                ans *= (self.check(st[:beg])**power)*self.check(st[end+1:])


            elif '(' in st and ')' in st:
                a= re.search(r'\([^(]*?\)', st).group(0)
                beg = st.find(a)
                end = beg + len(a) -1
                ans *= self.check(st[:beg])*self.check(a[1:-1])*self.check(st[end+1:])

            elif '*' in st:
                st = st.replace("(", "")
                st = st.replace(")", "")
                beg = st.find('*')
                ans *= self.check(st[:beg])*self.check(st[beg+1:])

            else:

                if st in self.defs:
                    ans = self.defs[st]**1

                else:
                    for q in self.defs:
                        if st in self.defs[q].aliases:
                            ans = self.defs[q]**1


        elif len(a)>1:
            q= self.check(a[0])
            compatible_terms = True
            for i in a[1:]:
                curr = self.check(i)
                if curr.dict != q.dict and compatible_terms:
                    compatible_terms = False
                    self.lbl_terms.text = "Term dimensions mismatch\n"+ a[0]+ " and "+ i+ " do not have the same dimensions\n"
                    self.lbl_terms.text += a[0]+ " has dimension of: "+ q.name+ "\n"+ i+ " has dimension of: "+ curr.name
            if compatible_terms:
                ans = q


        ans.find_name(self.defs)
        return ans

    def __init__(self):

        self.init_components()


        self.f = google.drive.app_files.unit_database
        self.data = self.f.worksheets[0]

        self.update_defs()
