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

        aliases = []

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

 a= re.search('\([^(]*?\)', '(a+B*(A+B)+2*(A+C) + c*(B-D*A)')
    print a.span()
