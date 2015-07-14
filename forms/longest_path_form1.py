from anvil import *
import physics
import draw
import math

class Form1(Form1Template):
    #acceleration vector
    g = physics.vector3(0, -9.81)
    floor_height = 0.05
    def btn_run_click (self, **event_args):
        # This method is called when the button is clicked
        if not self.running:
            if self.reset:
                self.init_ball()
            self.running  = True
            self.reset = False
            self.btn_run.text = "Pause"

        else:
            self.running = False
            self.btn_run.text = "Run"
        #make parameters only editable while reset
        for box in self.param_boxes:
            box.enabled = self.reset

    def btn_reset_click (self, **event_args):
        #This method is called when the button is clicked
        self.running = False
        self.init_ball()
        #self.draw_floor()
        self.reset = True
        self.btn_run.enabled = True
        self.btn_run.text = "Run"
        self.t = 0
        #make parameters only editable while reset
        for box in self.param_boxes:
            box.enabled = self.reset

    def timer_tick (self, **event_args):
        # This method is called Every [interval] seconds
        dt = self.dt
        canvas = self.canvas
        self.cw  = canvas.get_width()
        self.ch = canvas.get_height()
        cw= self.cw
        ch = self.ch
        xu = self.xu

        if self.first:
            self.init_ball()
            d = self.v**2/self.g.mag()
            if d>0:
                self.xu  = cw/(d+4*self.ball.radius)
            canvas.height = "{0}".format(round(self.xu*(d/2)))
            self.first  = False

        if self.running:
            if self.ball.pos.y-self.ball.radius -self.floor_height<=0.001 and self.t>0:
                self.ball.pos.y = self.ball.radius+self.floor_height
                self.t = 0
                self.running = False
                self.btn_run.text = "Run"
                self.btn_run.enabled = False

            else:
                self.ball.move(dt)
                self.ball.vel = self.ball.vel + self.g*dt
                self.path += dt*self.ball.vel.mag()
                self.t += dt

            self.lbl_path.text = "Path = {0:.2f}m".format(self.path)
        self.draw_all()

    def draw_all(self):
        canvas = self.canvas
        self.cw  = canvas.get_width()
        self.ch = canvas.get_height()
        cw= self.cw
        ch = self.ch
        xu = self.xu
        ball= self.ball

        draw.reset2(canvas, xu)
        draw.clear_canvas(canvas, "#fff")

        canvas.fill_style = "#000"
        canvas.fill_rect(0, 0, cw, self.floor_height)

        draw.circle(canvas, ball.radius, ball.pos.x, ball.pos.y)
        canvas.fill_style= "#3683f3"
        canvas.fill()

    def init_ball(self):
        xsp = 0
        ysp = 0
        self.v = 0
        ang = round(float(self.txt_ang.text))*math.pi/180
        v = float(self.txt_v.text)
        if 20>=v>0:
            self.v = v
        if ang>0:
            xsp = self.v*math.cos(ang)
            ysp = self.v*math.sin(ang)
        self.ball = physics.ball(1, 0.1)
        self.ball.pos = physics.vector3(self.ball.radius, self.ball.radius+self.floor_height)
        self.ball.vel = physics.vector3(xsp, ysp)

        self.d = self.v**2/self.g.mag()
        d =self.d
        if d>0:
            self.xu  = self.cw/(d+3*self.ball.radius)

        self.path = 0
    def __init__(self):
        # This sets up a variable for every component on this form.
        # For example, if we've drawn a button called "send_button", we can
        # refer to it as self.send_button:
        self.init_components()

        # Any code you write here will run when the form opens.
        #Uncomment as required.
        self.running= False
        self.reset = True
        self.first = True
        self.dt = self.timer.interval

        self.t = 0
        #SET SCALE (pixels per m, or unit used in code)
        self.xu = 6
        self.v = 0

        #APPEND ALL PARAMETER BOXES
        self.param_boxes= []
        self.param_boxes.append(self.txt_v)
        self.param_boxes.append(self.txt_ang)
