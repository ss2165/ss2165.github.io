from anvil import *

class quant_entry (quant_entryTemplate):
  def __init__(self,name, aliases, dicto):
    self.init_components()
    self.lbl_name.text = name

    for i in aliases:
      self.lbl_aliases.text += " " + i + ","
    self.lbl_aliases.text = self.lbl_aliases.text[:-1]

    for key,val in dicto.items():
      if val !=0:
        if key =='a':
          key = 'A'
        if key =='k':
          key = 'K'
        self.lbl_dict.text += key
        if val != 1:
          self.lbl_dict.text += "^"
          if val%1 ==0:
            self.lbl_dict.text += str(int(val))
          else:
            self.lbl_dict.text += val

    
