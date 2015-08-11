from anvil import *
base_units =  ('kg', 'm', 'a', 'cd', 'k', 'mol','s')

class quant_entry (quant_entryTemplate):
    def btn_click (self, **event_args):
        # This method is called when the button is clicked
        if self.box != None:
            self.box.text+=self.lbl_name.text

    def __init__(self,name, aliases, dicto, box = None):
        self.init_components()
        self.lbl_name.text = name
        self.box = box
        for i in aliases:
            self.lbl_aliases.text += " " + i + ","
        self.lbl_aliases.text = self.lbl_aliases.text[:-1]

        for key in base_units:
            if key in dicto:
              val = dicto[key]
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

        if self.lbl_dict.text == "":
            for key in dicto:
                self.lbl_dict.text += key
