from anvil import *
import physics
import draw
import math
import google.drive
import re

from quant_entry import quant_entry


base_units =  ('kg', 'm', 'a', 'cd', 'k', 'mol','s')
functions = ('log', 'exp', 'sin', 'cos', 'tan')

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
        self.name = "[no name]"
        return self.name
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
        out = self.name + ": "
        for name, val in self.dict.items():
            if val !=0:
                if name =='a':
                    name = 'A'
                if name =='k':
                    name = 'K'
                out += name
                if val != 1:
                    out += "^"
                    if val%1 ==0:
                        out += str(int(val))
                    else:
                        out += str(val)
        return out


class Problem():
    def __init__(self, outbox, string):
        outbox.text= string
        outbox.visible = True

class Form1(Form1Template):

    def txt_filter_change (self, **event_args):
        if self.txt_filter.text =="":
            self.fill_table()

        else:
            self.lst_quants.clear()
            titles  = quant_entry("Name", ["Aliases"], {"Base Units":1})
            titles.lbl_name.bold = True
            titles.lbl_aliases.bold = True
            titles.lbl_dict.bold = True
            self.lst_quants.add_component(titles)

            for key, q in sorted(self.defs.items()):
                check_name = key.find(self.txt_filter.text) != -1

                if not check_name:
                    for i in q.aliases:
                        if not check_name:
                            check_name =  i.find(self.txt_filter.text) != -1
                if check_name:
                    entry  = quant_entry(q.name, q.aliases, q.dict)
                    self.lst_quants.add_component(entry)

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
        self.lbl_terms.visible = False
        self.lbl_match.visible = False
        st = self.txt_1.text.replace(" ", "")
        st2 =self.txt_2.text.replace(" ", "")

        ans = self.check(st)
        ans2 = self.check(st2)


        self.lbl_1.text = str(ans)
        self.lbl_2.text = str(ans2)

        if ans.dict == ans2.dict:
            self.lbl_match.visible = True

        print "\n"*5

    def print_quant(self, q):
        "Return a formatted string of quantity and "
        out = q.name + ": "
        for name, val in q.dict.items():
            if val !=0:
                if name =='a':
                    name = 'A'
                if name =='k':
                    name = 'K'
                out += name
                if val != 1:
                    out += "^"
                    if val%1 ==0:
                        out += str(int(val))
                    else:
                        out += str(val)
        return out

    def fill_table(self):
        self.lst_quants.clear()
        titles  = quant_entry("Name", ["Aliases"], {"Base Units":1})
        titles.lbl_name.bold = True
        titles.lbl_aliases.bold = True
        titles.lbl_dict.bold = True
        self.lst_quants.add_component(titles)

        for key, q in sorted(self.defs.items()):
            entry  = quant_entry(q.name, q.aliases, q.dict)
            self.lst_quants.add_component(entry)

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
        self.fill_table()



    def find_re(self, rst, st):
        """Return RegEx search result string, and span in one tuple"""
        a= re.search(rst, st)
        if a is not None:
            a = a.group(0)
            beg = st.find(a)
            end = beg + len(a) -1

            return (a, beg, end)
        else:
            return None

    def find_paran(self, st):
        """Return indices of highest level parantheses"""
        starts = 0
        startindex = 0
        ends = 0
        endindex = 0

        for i in range(len(st)):
            if st[i] == '(':
                starts +=1
                if starts ==1:
                    startindex = i
            elif st[i] == ')':
                ends += 1
                if ends > starts:
                    return None
                elif starts == ends:
                    endindex = i
                    return (startindex, endindex)
        return None

    def split_paran(self, st):
        br=self.find_paran(st)
        ne = None
        if isinstance(br, tuple):
            ne = self.find_paran(st[br[1]+1:])
        if isinstance(ne, tuple):
            new = st[br[1]+1:]
            print "Hit1", new
            plus = self.find_re('\+|-', new)
            if plus is not None:
                plus = plus[1]
                op = new.find('(')
                if plus < op:
                    print "Hit3"
                    return [st[:br[1]+1+plus]] + self.split_paran(st[br[1]+1+plus:])

        return [st]

    def check(self,st2):
        brackets = self.find_paran(st2)
        if isinstance(brackets, tuple) and brackets[0] == 0 and brackets[1] == len(st2)-1:
            st2 = st2[1:-1]
        ans = quant()

        a = re.findall(r'([^+-]*\(.*\)(\^\-?[\d.]*)?[\w/.*\^]*|[^+-]*\w+(\^\-?[\d.]*)?[\w/.*]*)', st2)
        for i in range(len(a)):
            if isinstance(a[i], tuple):
                store = a[i]
                del a[i]
                a.insert(i, store[0])
        print a
        if a == []:
            a = [""]
        for j in range(len(a)):
            if len(a[j])>0:
                newlist = self.split_paran(a[j])
                del a[j]
                k = j
                for i in newlist:
                    a.insert(k, i)
                    k += 1
        for i in a:
            if len(i)>0 and ( i[0] == '+' or i[0] == '-'):
                 i= i[1:]
            elif len(i)>0 and ( i[len(i)-1] == '+' or i[len(i)-1] == '-'):
                i = i[:-1]
        print a
        if len(a)==1:
            st = a[0]
            brackets = self.find_paran(st)
            if isinstance(brackets, tuple) and brackets[0] == 0 and brackets[1] == len(st)-1:
                st = st[1:-1]
            # if '(' in st2 and ')' in st2:
            #     paran= re.search(r'\([^(]*?\)', st2).group(0)
            #     beg = st2.find(paran)
            #     end = beg + len(paran) -1
            #     ans = self.add_check(st2[:beg])*self.add_check(paran[1:-1])*self.add_check(st2[end+1:])
            # else:

            # if '+' in st or '-' in st:
            #     a= re.search(r'\([^(]*?\)', st).group(0)
            #     beg = st.find(a)
            #     end = beg + len(a) -1
            #     if st[beg-1] =='/':
            #         ans = self.check(st[:beg-1])*self.check(st[end+1:])/self.check(a[1:-1])
            #     else:
            #         ans= self.check(st[:beg])*self.check(a[1:-1])*self.check(st[end+1:])

            if '(' in st and ')' in st:
                print "parantheses", st
                # a= re.search(r'\([^()]*?\)', st).group(0)
                # beg = st.find(a)
                # end = beg + len(a) -1
                brackets = self.find_paran(st)
                beg, end = brackets
                a = st[beg:end+1]
                inside = self.check(a[1:-1])

                if len(st[:beg])>2:
                    prev = st[beg-3:beg]

                    if prev in functions:
                        if inside.name != "dimensionless":
                            text = "ERROR: Expression inside " + prev + "() is not dimensionless\n"#TODO raise error
                            text += a[1:-1] + " has dimensions of " + inside.name
                            raise Problem(self.lbl_terms,text)
                            return self.defs['dimensionless']

                        else:
                            beg -=3

                if beg>0 and st[beg-1] =='/':
                    inside = inside**-1
                    beg -=1
                if end + 2 <len(st) and st[end+1] == '^':
                    find = self.find_re(r'-?[\d.]+', st[end+2:])
                    end += 2+find[2]
                    inside = inside**float(find[0])

                ans = self.check(st[:beg])*inside*self.check(st[end+1:])

            elif '^' in st:
                #print "power", st
                find = self.find_re(r'\w*\^-?[\d.]+', st)
                a = find[0]
                beg = find[1]
                end = find[2]

                split = a.split('^')
                dim = split[0]

                power = float(split[1])
                if st[beg-1] =='/':
                    inside = self.check(dim)**(-power)
                    beg -=1
                else:
                    inside = self.check(dim)**(power)
                ans = self.check(st[:beg])*inside*self.check(st[end+1:])

            elif '/' in st:
                print "div", st
                st = st.replace("(", "")
                st = st.replace(")", "")
                a = re.search(r'[/](\([^)(]*?\)|\w+)[\^\w.]*', st).group(0)
                beg = st.find(a)
                end = beg + len(a) -1
                ans = self.check(st[:beg])*self.check(st[end+1:])/self.check(a[1:])

            elif '*' in st:
                #print "mult", st
                st = st.replace("(", "")
                st = st.replace(")", "")
                beg = st.find('*')
                ans = self.check(st[:beg])*self.check(st[beg+1:])

            else:

                if st in self.defs:
                    ans = self.defs[st]**1

                else:
                    found = False
                    for q in self.defs:
                        if not found:
                            if st in self.defs[q].aliases:
                                ans = self.defs[q]**1
                                found = True
                    if not found and st != "" and st != " " and not re.match(r'[\d.]+', st):
                        text = "Syntax error\n"  + st
                        raise Problem(self.lbl_terms,text)


        elif len(a)>1:
            print "terms:", a
            q= self.check(a[0])
            compatible_terms = True
            for i in a[1:]:
                curr = self.check(i)
                if curr.dict != q.dict and compatible_terms:
                    compatible_terms = False#TODO raise error
                    text = "ERROR: Term dimensions mismatch\n"+ a[0]+ " and "+ i+ " do not have the same dimensions\n"
                    text += a[0]+ " has dimension of: "+ q.name+ "\n"+ i+ " has dimension of: "+ curr.name
                    raise Problem(self.lbl_terms,text)
            if compatible_terms:
                ans = q


        if ans.find_name(self.defs) == "[no name]":
            ans.name = st2
        print ans.name
        return ans

    def __init__(self):

        self.init_components()

        self.f = google.drive.app_files.unit_database
        self.data = self.f.worksheets[0]

        self.update_defs()
