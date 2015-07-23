from anvil import *
import physics
import draw
import math

class Form1(Form1Template):

    def can_slid_mouse_move (self, x, y, **event_args):
        self.slider1.mouse_move(x, y)
        self.txt_1.text = "{0}".format(int(self.slider1.value))
    def can_slid_mouse_up (self, x, y, button, **event_args):
        self.slider1.mouse_up(x, y)
    def can_slid_mouse_down (self, x, y, button, **event_args):
        self.slider1.mouse_down(x, y)



    def can_slid_2_mouse_move (self, x, y, **event_args):
        self.slider2.mouse_move(x, y)
    def can_slid_2_mouse_up (self, x, y, button, **event_args):
        self.slider2.mouse_up(x, y)
    def can_slid_2_mouse_down (self, x, y, button, **event_args):
        self.slider2.mouse_down(x, y)

    def timer_1_tick (self, **event_args):
        if self.first:
            self.slider1 = draw.slider(self.can_slid, mini= 0, maxi = 100, stepsize = 1, start=4, colour = "#c17e27")
            self.slider1.indicator = True
            self.slider1.draw()
            self.slider2 = draw.slider(self.can_slid_2, mini= -10, maxi = 10, stepsize = 0.1, start=0)
            self.slider2.maxmin =True
            self.slider2.draw()
            self.first = False


    def txt_1_change (self, **event_args):
        if len(self.txt_1.text)>0:
            self.slider.value = float(self.txt_1.text)
            self.slider.draw()
    def __init__(self):
        # This sets up a variable for every component on this form.
        # For example, if we've drawn a button called "send_button", we can
        # refer to it as self.send_button:
        self.init_components()
        self.first = True

        # Any code you write here will run when the form opens.
