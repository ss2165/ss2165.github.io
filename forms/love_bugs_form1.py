from anvil import *
import physics
import draw
import math

class Form1(Form1Template):
    line_width = 0.001
    bugradius = 0.003
    def timer_tick (self, **event_args):
        # This method is called Every [interval] seconds
        self.cw = self.canvas.get_width()
        self.ch  =self.canvas.get_height()
        ch = self.ch

        canvas = self.canvas

        L = self.L
        v = self.v
        a = self.a
        #distance from centre to middle of one side
        self.d = float(L)*math.sqrt((1+math.cos(a))/(1-math.cos(a)))/2
        d = self.d
        if self.reset and not self.zoom:
            self.xu  =self.give_xu(self.ch, self.d)
            self.newxu = self.give_xu(self.ch, self.d)
        xu = self.xu
        if self.reset:
            self.initial(canvas)

        if self.running:
            self.move_bug(self.bug)
            self.draw_bugs(canvas, self.bug.pos)
            draw.reset2(canvas, xu)

            if self.bug.pos.mag() <= self.bugradius:
                self.running = False
                self.btn_run.text = "Run"
                #self.initial(canvas)

        if -0.1 <= self.xu - self.newxu <= 0.1:
            self.zoom = False
        if self.zoom:
            self.xu += self.step

    def initial(self, canvas):
        draw.reset2(canvas, self.xu)
        draw.clear_canvas(canvas, "#fff")
        self.draw_polygon(canvas, self.N, self.L)
        self.bug.pos = physics.vector3(-self.L/2, self.d, 0)
        draw.reset2(canvas, self.xu)
        self.draw_bugs(canvas, self.bug.pos)
        draw.reset2(canvas, self.xu)

    def txt_change (self, **event_args):
        if len(self.txt_N.text)>0 and len(self.txt_L.text)>0 and len(self.txt_v.text)>0:
            if  30 >= int(self.txt_N.text)>2:
                self.N  =  int(self.txt_N.text)
            if 1>=float(self.txt_L.text)>=0.01:
                self.L = float(self.txt_L.text)
            if 1>=float(self.txt_v.text)>=0:
                self.v = float(self.txt_v.text)
            self.zoom = True
            self.a = 2*math.pi/self.N

            self.oldxu = self.xu
            self.d = float(self.L)*math.sqrt((1+math.cos(self.a))/(1-math.cos(self.a)))/2
            self.newxu = self.give_xu(self.ch, self.d)
            self.step = (self.newxu-self.oldxu)/20
    def give_xu(self, ch, d):
        return (ch/0.5)*(0.12/d)
    def draw_bugs(self, canvas, pos):
        canvas.translate(self.cw/(2.0*self.xu), self.ch/(2.0*self.xu))
        for i in range(self.N):
            canvas.rotate(self.a)
            canvas.translate(pos.x, pos.y)
            draw.circle(canvas, self.bug.radius)
            canvas.fill_style = "#00f"
            canvas.fill()
            canvas.translate(-pos.x, -pos.y)

    def move_bug(self, bug):
        aim = (bug.pos.phi_rotate(-self.a, physics.vector3(0,0,0)) - bug.pos).norm()
        bug.vel = aim*self.v
        bug.pos = bug.pos + bug.vel*self.dt
        self.t += self.dt
        self.lbl_t.text = "t = {0}s".format(repr(self.t))

    def draw_polygon(self,canvas, N, L):
        canvas.translate(self.cw/(2.0*self.xu), self.ch/(2.0*self.xu))
        draw.polygon(canvas, N, L)
        canvas.stroke_style = "#000"
        canvas.line_width = self.line_width
        canvas.stroke()


    def btn_run_click (self, **event_args):
        # This method is called when the button is clicked
        draw.btn_run_click(self)

        #make parameters only editable while reset
        for box in self.param_boxes:
            box.enabled = self.reset

    def btn_reset_click (self, **event_args):
        # This method is called when the button is clicked
        draw.btn_reset_click(self)
        self.t = 0
        self.lbl_t.text = "t = {0}s".format(repr(self.t))
        #make parameters only editable while reset
        for box in self.param_boxes:
            box.enabled = self.reset


    def __init__(self):
        # This sets up a variable for every component on this form.
        # For example, if we've drawn a button called "send_button", we can
        # refer to it as self.send_button:
        self.init_components()
        # Any code you write here will run when the form opens.
        #Uncomment as required.
        self.running= False
        self.reset = True
        self.zoom = False
        self.bug  = physics.ball(1, self.bugradius)

        self.N  =  int(self.txt_N.text)
        self.L = float(self.txt_L.text)
        self.v = float(self.txt_v.text)
        self.a = 2*math.pi/self.N

        self.dt = self.timer.interval
        self.t = 0
        #list of parameter inputs
        self.param_boxes = []

        self.param_boxes.append(self.txt_N)
        self.param_boxes.append(self.txt_L)
        self.param_boxes.append(self.txt_v)
