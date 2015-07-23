from anvil import *
import physics
import draw
import math
import google.drive

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

    def __mul__(self, other):
        newdict  = {}
        for key in self.dict:
             newdict[key] =  self.dict[key] + other.dict[key]
        return quant(newdict)
    def __div__(self, other):
        newdict  = {}
        for key in self.dict:
             newdict[key]=  self.dict[key] - other.dict[key]
        return quant(newdict)


class Form1(Form1Template):

    def button_1_click (self, **event_args):
        self.lbl.text = ""
        args = self.txt.text.split('*')
        result = quant()
        for q in args:
            result = result * self.defs[q]#TODO __iadd__
        for i, val in result.dict.items():
            if val != 0:
                self.lbl.text += " {0}: {1}".format(i, val)

    def __init__(self):

        self.init_components()


        self.f = google.drive.app_files.unit_database
        self.data = self.f.worksheets[0]

        self.defs = {}
        for row in self.data.rows:
            quantity = quant()
            for unit in base_units:
                quantity.dict[unit] =  int(row[unit])

            self.defs[row['name']] = quantity
        # for name, item in self.defs.items():
        #     print name,  item.dict
