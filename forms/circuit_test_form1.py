from anvil import *
import physics
import draw
import circuits
import math

class Form1(Form1Template):
    def canvas_mouse_move (self, x, y, **event_args):

        # This method is called when the mouse cursor moves over this component
        #record mouse pos
        #   self.mouse.x = x/(self.xu*1.0)
        #   self.mouse.y = (self.ch-y)/(self.xu*1.0)
        pass

    def canvas_mouse_up (self, x, y, button, **event_args):
        # This method is called when a mouse button is released on this component
        #   self.mouse.x = x/(self.xu*1.0)
        #   self.mouse.y = (self.ch-y)/(self.xu*1.0)
        pass


    def canvas_mouse_down (self, x, y, button, **event_args):
        # This method is called when a mouse button is pressed on this component
        #   self.mouse.x = x/(self.xu*1.0)
        #   self.mouse.y = (self.ch-y)/(self.xu*1.0)
        pass

    def btn_run_click (self, **event_args):
        # This method is called when the button is clicked
          #if not self.running:
            #  self.running  = True
            #  self.reset = False
            #  self.btn_run.text = "Pause"

        #else:
        #  self.running = False
        #  self.btn_run.text = "Run"
        pass


    def btn_reset_click (self, **event_args):
        # This method is called when the button is clicked
        #self.running = False
        #self.reset = True
        #self.btn_run.text = "Run"
        pass

    def txt_V_pressed_enter (self, **event_args):
        self.cell.outV = float(self.txt_V.text)
        self.circuit.update()
        self.circuit.draw()

    def timer_tick (self, **event_args):
        canvas = self.canvas
        self.cw = canvas.get_width()
        self.ch = canvas.get_height()
        cw = self.cw
        ch = self.ch
        dt = self.dt
        if self.first:
            self.circuit = circuits.circuit(canvas)
            circuit = self.circuit
            self.cell = circuits.cell(x= 200, y= 100, V = float(self.txt_V.text))
            cell = self.cell
            cell2 = circuits.cell(x= 220, y= 100, V = 6)
            circuit.component_add(cell)
            circuit.component_add(cell2)
            res = circuits.resistor( x= 250, y= 200, R = 10)
            res.hor_flip()
            circuit.component_add(res)
            bulb  = circuits.bulb( x= 300, y= 100)
            circuit.component_add(bulb)
            cell.out_connect_to(cell2)
            cell2.out_connect_to(bulb)
            bulb.out_connect_to(res)
            res.out_connect_to(cell)
            circuit.update()
            circuit.draw()
            print cell.I, cell.inV, cell.outV
            print "\n"*3
            print bulb.I, bulb.inV, bulb.outV
            print "\n"*3
            print res.I, res.inV, res.outV
            self.first = False
        self.t += self.dt


    def __init__(self):
        # This sets up a variable for every component on this form.
        # For example, if we've drawn a button called "send_button", we can
        # refer to it as self.send_button:
        self.init_components()
        #self.mouse = physics.vector3(0,0)

        # Any code you write here will run when the form opens.
        #Uncomment as required.
        self.running= False
        self.reset = True
        self.dt = self.timer.interval
        self.first = True

        self.t = 0
        #SET SCALE (pixels per m, or unit used in code)
        #self.xu = 1

        #APPEND ALL PARAMETER BOXES
        #self.param_boxes= []
