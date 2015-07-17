from anvil import *
import physics
import draw
import math

class Form1(Form1Template):
    #acceleration vector
    g = physics.vector3(0, -9.81)
    floor_height = 0.05
    arrow_scale = 0.05
    linewidth = 0.01
    def txt_change (self, **event_args):
        self.init_ball()

    def canvas_mouse_move (self, x, y, **event_args):
        # This method is called when the mouse cursor moves over this component
        #record mouse pos
        self.mouse.x = x/self.xu
        self.mouse.y = (self.ch-y)/self.xu

        #change text box value based on where mouse is
        if self.mousedown:
            x = ((self.mouse - self.ball.pos).x)
            y = ((self.mouse - self.ball.pos).y)
            ang = math.atan(y/x)
            if 0<=ang<=math.pi/2:
                self.txt_ang.text = "{0}".format(int(ang*180/math.pi))
                self.ball.vel = physics.vector3(self.v*math.cos(ang), self.v*math.sin(ang))



    def canvas_mouse_up (self, x, y, button, **event_args):
        # This method is called when a mouse button is released on this component
        self.mousedown = False

    def canvas_mouse_down (self, x, y, button, **event_args):
        # This method is called when a mouse button is pressed on this component
        self.mouse.x = x/self.xu
        self.mouse.y = (self.ch-y)/self.xu

        #arrow detect
        if (0.9*self.arrow_scale*self.ball.vel + self.ball.pos - self.mouse).mag()<= self.ball.radius/3:
            self.mousedown= True

    def btn_path_click (self, **event_args):
        self.paths= []

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

        self.cur_path = []
        self.paths.append(self.cur_path)
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
                if int(self.t/self.dt) %3 ==0:
                    self.cur_path.append(self.ball.pos)
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

        #arrow
        if not self.running:
            ball = self.ball
            #velocity vector
            canvas.translate(ball.pos.x, ball.pos.y)
            if ball.vel.y>0:
                canvas.rotate(ball.vel.phi())
            else:
                canvas.rotate(-ball.vel.phi())
            draw.arrow(canvas, ball.vel.mag()*self.arrow_scale, 4*self.linewidth)
            canvas.fill_style = "#49902a"
            canvas.fill()
            draw.reset2(canvas, xu)

        #dashes
        canvas.begin_path()
        if not self.running:
            for path in self.paths:
                if len(path)>2:
                    for i in range(len(path)-1):
                        canvas.move_to(path[i].x, path[i].y)
                        diff = path[i+1] - path[i]
                        new  = path[i] + diff*0.8
                        canvas.line_to(new.x, new.y)

            canvas.line_width = 0.01
            canvas.stroke()
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

        self.mousedown = False
        self.mouse = physics.vector3(0,0,0)

        self.t = 0
        self.paths = []
        #SET SCALE (pixels per m, or unit used in code)
        self.xu = 6
        self.v = 0

        #APPEND ALL PARAMETER BOXES
        self.param_boxes= []
        self.param_boxes.append(self.txt_v)
        self.param_boxes.append(self.txt_ang)
