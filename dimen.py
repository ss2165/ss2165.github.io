
base_units =  ('s', 'A', 'cd', 'K', 'kg', 'm', 'mol')
class quant(dict):
    def __init__(self, dicto = None):
        if isinstance(dicto, dict):
            for key in dicto:
                self[key] = dicto[key]

        for unit in base_units:
            if unit not in self::
                self[unit] = 0

    def __mul__(self, other):
        newdict  = quant()
        for key in self:
             newdict[key] =  self[key] + other[key]
        return newdict
    def __div__(self, other):
        newdict  = quant()
        for key in self:
             newdict[key]=  self[key] - other[key]
        return newdict
