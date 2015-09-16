# Copyright 2015 Seyon Sivarajah
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License
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
    """A dimensional quantity, with name, aliases, associated keywords and base unit dictionary"""
    def __init__(self, dicto = None):
        self.dict = {}
        #if initialized with dictionary, fill it in
        if isinstance(dicto, dict):
            for key in dicto:
                self.dict[key] = dicto[key]

        #if not provided, assume dimensions are 0
        for unit in base_units:
            if unit not in self.dict:
                self.dict[unit] = 0.0

        self.aliases = []
        self.keywords = []
        self.name = ""

    def find_name(self, dic):
        """search dictionary for match and name self if found, then return formatted name"""
        for q in dic:
            if self.dict == dic[q].dict:
                name = q.replace("_", " ").title()
                self.name = name
                return name
        self.name = "[no name]"
        return self.name

    def __pow__(self, value):
        """raise dimensions to a power"""
        newdict  = {}
        for unit in self.dict:
            newdict[unit] = self.dict[unit]*value
        return quant(newdict)

    def __mul__(self, other):
        """multiply dimensions together (add unit powers) and return result"""
        newdict  = {}
        for key in self.dict:
             newdict[key] =  self.dict[key] + other.dict[key]
        return quant(newdict)

    def __imul__(self, other):
        """multiply dimensions together (add unit powers) and return result"""
        for key in self.dict:
            self.dict[key] =  self.dict[key] + other.dict[key]
        return self

    def __div__(self, other):
        """divide dimensions (take away unit powers) and return result"""
        newdict  = {}
        for key in self.dict:
             newdict[key]=  self.dict[key] - other.dict[key]
        return quant(newdict)

    def __idiv__(self, other):
        """divide dimensions (take away unit powers) and return result"""
        for key in self.dict:
            self.dict[key] =  self.dict[key] - other.dict[key]
        return self

    def __str__(self):
        """Return string of quantity as [name]: [base_units]"""
        out = self.name + ": "
        for name in base_units:
            val = self.dict[name]
            #only include non zero powers
            if val !=0:
                #capitalize amps and kelvin
                if name =='a':
                    name = 'A'
                if name =='k':
                    name = 'K'
                out += name
                #only include power for non unitary
                if val != 1:
                    out += "^"
                    if val%1 ==0:
                        out += str(int(val))
                    else:
                        out += str(val)
        return out


class Problem():
    """Exception: Fills error box with error string"""
    def __init__(self, outbox, string):
        outbox.text= string
        outbox.visible = True

class Form1(Form1Template):

    def txt_filter_change (self, **event_args):
        """Filter list of quantities by name, alias, keywords, return results"""

        self.fill_table()


    def check_dev_change (self, **event_args):
        """Enable database entry form"""
        self.txt_new.visible = self.check_dev.checked
        self.btn_new.visible = self.check_dev.checked

    def btn_new_click (self, **event_args):
        """Submit new datbase entry. Entry should be name followed by comma separated aliases"""
        #remove whitespace
        st = self.txt_1.text.replace(" ", "")
        namee = self.txt_new.text
        #find quantity
        ans = self.check(st)
        isin = False

        #check if quantity already in database
        for name, quantity in self.defs.items():
            if quantity.dict == ans.dict:
                isin = True

        if not isin:
            #separate name and aliases
            info = namee.split(',', 1)
            ans.name = info[0]
            if ans.name == "" or ans.name == " ":
                raise "Provide new quantity name"
            aliases = ""
            if len(info)>1:
                aliases = info[1]
            row = self.data.add_row(name=info[0],aliases = aliases)
            #fill in each unit
            for unit in ans.dict:
                row[unit] = ans.dict[unit]

        #read in new database
        self.update_defs()

    def button_1_click (self, **event_args):
        #clear error box
        self.lbl_terms.visible = False

        #read in input string and remove whitespace
        st = self.txt_1.text.replace(" ", "")

        #check both strings
        ans = self.check(st)

        #return values
        self.lbl_1.text = str(ans)



        #clear Output
        print "\n"*5



    def fill_table(self):
        """Fill quantity list with all in database"""
        #clear table
        self.lst_quants.clear()
        #fill title row
        titles  = quant_entry("Name", ["Aliases"], {"Base Units":1})
        titles.lbl_name.bold = True
        titles.lbl_aliases.bold = True
        titles.lbl_dict.bold = True
        titles.btn.visible = False
        self.lst_quants.add_component(titles)

        #fill in quantities in alphabetical order
        check_name = True
        filt = self.txt_filter.text.replace(" ", "").lower()
        for key, q in sorted(self.defs.items()):
            if filt != "":
                #check name, case insensitive
                check_name = key.lower().find(filt) != -1
                #check aliases
                if not check_name:
                    for i in q.aliases:
                        if not check_name:
                            check_name =  i.lower().find(filt) != -1
                #check keywords
                if not check_name:
                    for i in q.keywords:
                        if not check_name:
                            check_name =  i.lower().find(filt) != -1
            #if found, fill entry
            if check_name:
                entry  = quant_entry(q.name, q.aliases, q.dict,self.txt_1)
                self.lst_quants.add_component(entry)

    def update_defs(self):
        """Read in database of definitions and fill table with them"""
        #list for all aliases, to check for duplicates
        all_aliases = []

        #dictionary of all quantities
        self.defs = {}
        for row in self.data.rows:
            quantity = quant()
            for unit in base_units:
                quantity.dict[unit] =  float(row[unit])
            #remove whitespace and extract comma separated aliases and keywords
            aliases = row['aliases'].replace(" ", "").split(",")
            keywords = row['keywords'].replace(" ", "").split(",")
            if "" not in aliases:
                quantity.aliases = aliases
            if "" not in keywords:
                quantity.keywords = keywords
            quantity.name = row['name']

            #Raise error if duplicate alias found
            for alias in quantity.aliases:
                if alias in all_aliases and alias !=  "" and alias != " ":
                    text = "Duplicate alias: quantity-" +  row['name'] + " alias- " +  alias
                    raise text
                else:
                    all_aliases.append(alias)

            #fill dictionary
            self.defs[row['name']] = quantity
        #fill database table
        self.fill_table()



    def find_re(self, rst, st):
        """Return RegEx search result string and span of result in one tuple. If not found, return None"""
        a= re.search(rst, st)

        if a is not None:
            a = a.group(0)
            beg = st.find(a)
            end = beg + len(a) -1
            return (a, beg, end)
        else:
            return None

    def find_paran(self, st):
        """Return indices of highest level parantheses in string. If unbalanced, return None."""
        starts = 0
        startindex = 0
        ends = 0
        endindex = 0

        for i in range(len(st)):
            if st[i] == '(':
                starts +=1
                if starts ==1:
                    #record if first open parantheses
                    startindex = i
            elif st[i] == ')':
                ends += 1
                if ends > starts:
                    #more closing than opening, invalid
                    return None
                elif starts == ends:
                    #balanced parantheses, return indices
                    endindex = i
                    return (startindex, endindex)
        return None

    def split_paran(self, st):
        """Split string into additive terms inside parantheses and return list, recursively."""
        #find first set of balanced, highest level parantheses
        br=self.find_paran(st)
        ne = None

        if isinstance(br, tuple):
            #if first set found, look for another set in remaining string
            ne = self.find_paran(st[br[1]+1:])

        if isinstance(ne, tuple):
            #if there is another set, check if split by addition or subtraction
            new = st[br[1]+1:]

            #check if there is a + or -, if not return whole string
            plus = self.find_re('\+|-', new)
            if plus is not None:
                #if there is a + or -, check it comes before parantheses before splitting
                plus = plus[1]
                op = new.find('(')
                if plus < op:
                    #return string before +- plus the remaining string split
                    return [st[:br[1]+1+plus]] + self.split_paran(st[br[1]+2+plus:])
        #if no more to split, return current string in list
        return [st]

    def check(self,st2):
        """Recursive checking function.

        Split in to highest level additive terms. Compare terms for same dimensions.
        For each term, evaluate parantheses then non parantheses."""

        #if whole string is enclosed in parantheses, remove them
        brackets = self.find_paran(st2)
        if isinstance(brackets, tuple) and brackets[0] == 0 and brackets[1] == len(st2)-1:
            st2 = st2[1:-1]

        #empty answer quant
        ans = quant()

        a = st2.split('=')
        #Find terms split by +- terms or terms between opening and closing parantheses
        for  i in range(len(a)):
            a = a[:i]+ re.findall(r'([^+-]*\(.*\)(\^\-?[\d.]*)?[\w/.*\^]*|[^+-]*\w+(\^\-?[\d.]*)?[\w/.*]*)', a[i])+ a[i+1:]
        #RegEx string: +- then parantheses followed by string(power/division/mult) or +- then non-parantheses terms

        #findall returns list of tuples, take only first value of tuple
        for i in range(len(a)):
            if isinstance(a[i], tuple):
                store = a[i]
                del a[i]
                a.insert(i, store[0])
        print a

        #if empty list, include empty string
        if a == []:
            a = [""]

        #split terms like (x+ y) + (a+(b+c))  in to terms, i.e. ["x+y", "(a+(b+c))" ]
        for j in range(len(a)):
            if len(a[j])>0:
                #split in to parantheses, remove old entry, add new list
                newlist = self.split_paran(a[j])
                del a[j]
                k = j
                for i in newlist:
                    a.insert(k, i)
                    k += 1
        print a

        #remove trailing +- symbols
        for j in range(len(a)):
            i = a[j]
            if len(i)>0 and ( i[0] == '+' or i[0] == '-'):
                new = i[1:]
                del a[j]
                a.insert(j, new)
            elif len(i)>0 and ( i[len(i)-1] == '+' or i[len(i)-1] == '-'):
                new = i[:-1]
                del a[j]
                a.insert(j, new)

        #if only one additive term, check it
        if len(a)==1:
            st = a[0]
            #if enclosed within parantheses, remove them
            brackets = self.find_paran(st)
            if isinstance(brackets, tuple) and brackets[0] == 0 and brackets[1] == len(st)-1:
                st = st[1:-1]

            #compute parantheses first
            if '(' in st and ')' in st:
                print "parantheses", st
                #find highest level of paran
                brackets = self.find_paran(st)
                try:
                    beg, end = brackets
                except TypeError:
                    raise Problem(self.lbl_terms, "Syntax Error: Check parantheses are balanced")

                a = st[beg:end+1]
                #check inside parantheses
                inside = self.check(a[1:-1])

                if len(st[:beg])>2:
                    prev = st[beg-3:beg]

                    #check for functions which should have dimensionless arguments
                    if prev in functions:
                        if inside.name.lower() != "dimensionless":
                            text = "ERROR: Expression inside " + prev + "() is not dimensionless\n"
                            try:
                                text += a[1:-1] + " has dimensions of " + inside.name
                            except TypeError:
                                raise Problem(self.lbl_terms, "Syntax Error")
                            raise Problem(self.lbl_terms,text)
                            return self.defs['dimensionless']

                        else:
                            #ignore processed text
                            beg -=3

                if beg>0 and st[beg-1] =='/':
                    #check if parantheses are being divided
                    inside = inside**-1
                    beg -=1
                if end + 2 <len(st) and st[end+1] == '^':
                    #check if parantheses are being raised to a power
                    find = self.find_re(r'-?[\d.]+', st[end+2:])
                    end += 2+find[2]
                    inside = inside**float(find[0])

                #process rest of string
                ans = self.check(st[:beg])*inside*self.check(st[end+1:])

            #non parantheses terms
            elif '^' in st:
                #check if raised to a power
                find = self.find_re(r'\w*\^-?[\d.]+', st)
                #RegEx find alphanumeric followed by power
                a = find[0]
                beg = find[1]
                end = find[2]

                #split by ^
                split = a.split('^')
                dim = split[0]

                power = float(split[1])
                if st[beg-1] =='/':
                    #check if term is being divided
                    inside = self.check(dim)**(-power)
                    beg -=1
                else:
                    inside = self.check(dim)**(power)
                #process rest of string
                ans = self.check(st[:beg])*inside*self.check(st[end+1:])

            elif '/' in st:
                #check for division
                st = st.replace("(", "")
                st = st.replace(")", "")
                try:
                    find = self.find_re(r'[/]\w+[\^\d.]*', st)
                    a = find[0]
                    #RegEx divide followed by alphanumeric
                except TypeError:
                    raise Problem(self.lbl_terms, "Syntax Error")

                beg = find[1]
                end = find[2]
                ans = self.check(st[:beg])*self.check(st[end+1:])/self.check(a[1:])

            elif '*' in st:
                #check for multiplication
                st = st.replace("(", "")
                st = st.replace(")", "")
                beg = st.find('*')
                ans = self.check(st[:beg])*self.check(st[beg+1:])

            else:
                #if no operators
                if st in self.defs:
                    #if in definitions, return that quatn
                    ans = self.defs[st]**1

                else:
                    #check for aliases as long as not found
                    found = False
                    for q in self.defs:
                        if not found:
                            if st in self.defs[q].aliases:
                                ans = self.defs[q]**1
                                found = True
                    #if not found, not empty and not a number, throw syntax error
                    if not found and st != "" and st != " " and not re.match(r'[\d.]+', st):
                        text = "Syntax error\n"  + st
                        raise Problem(self.lbl_terms,text)


        elif len(a)>1:
            #if multiple terms, check for same dimensions
            q= self.check(a[0])
            compatible_terms = True
            for i in a[1:]:
                curr = self.check(i)
                if curr.dict != q.dict and compatible_terms:
                    #if any do not match, throw mismatch error
                    compatible_terms = False
                    text = "ERROR: Term dimensions mismatch\n"+ a[0]+ " and "+ i+ " do not have the same dimensions\n"
                    text += a[0]+ " has dimension of: "+ q.name+ "\n"+ i+ " has dimension of: "+ curr.name
                    raise Problem(self.lbl_terms,text)
            if compatible_terms:
                #all match, record dimension
                ans = q


        if ans.find_name(self.defs) == "[no name]":
            #unnamed expression, lablelled with input
            ans.name = st2
        print ans.name
        return ans

    def __init__(self):

        self.init_components()

        #load database sheet
        self.f = google.drive.app_files.unit_database
        self.data = self.f.worksheets[0]

        #read in definitions
        self.update_defs()
