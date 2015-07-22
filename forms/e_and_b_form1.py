from anvil import *
import physics
import draw
import math

class Form1(Form1Template):
    radius = 0.1
    e = 1.602e-19
    me = 9.11e-31
    mp = 1.67e-27
    v = 2.3e7
    line_width = 0.03
    arrow_scale = 1e-7

    def txt_zoom_change (self, **event_args):
        # This method is called when the text in this text box is edited
        if self.reset:
            scale = float(self.txt_zoom.text)
            if 0.1<=scale<=4 :
                self.oldxu  = 1.0*self.xu
                self.newxu = self.cw/10.0*scale
                self.zoom = True

    def canvas_mouse_move (self, x, y, **event_args):
        # This method is called when the mouse cursor moves over this component
        #record mouse pos
        self.mouse.x = x/self.xu
        self.mouse.y = (self.ch-y)/self.xu

        #change text box value based on where mouse is
        if self.mousedown:
            self.ball.pos += self.mouse - self.ball.pos


    def canvas_mouse_up (self, x, y, button, **event_args):
    # This method is called when a mouse button is released on this component
        self.mousedown = False

    def canvas_mouse_down (self, x, y, button, **event_args):
        # This method is called when a mouse button is pressed on this component
        self.mouse.x = x/self.xu
        self.mouse.y = (self.ch-y)/self.xu
        #if mouse is within a ball, record it
        if (self.ball.pos - self.mouse).mag() <=self.ball.radius and self.reset:
            self.mousedown= True
        #arrow detect
        # for i in range(2):
        #    if (0.9*self.arrow_scale*self.balls[i].vel + self.balls[i].pos - self.mouse).mag()<= self.bigrad/3 and self.check_vel.checked:
        #        self.mousedown[i+4] = True

    def timer_tick (self, **event_args):
        canvas = self.canvas
        self.cw = canvas.get_width()
        self.ch = canvas.get_height()
        cw = self.cw
        ch = self.ch
        dt = self.dt

        self.grid_custom.visible = self.custom.selected

        if self.first:
            self.xu = cw/10.0
            self.initialize()
            self.init_pos()
            self.first = False

        ball = self.ball
        if self.running:
            dtt = dt/30
            for i in range(30):
                ball.vel += dtt*(self.E + ball.vel.cross(self.B))*ball.charge/ball.mass
            ball.move(dt)
            if int(self.t/self.dt) %6 ==0:
                self.cur_path.append(self.ball.pos)
            self.t += dt

        if self.zoom:
            self.xu += (self.newxu-self.oldxu)/20
            self.init_pos()
            if -0.05 <=(self.xu - self.newxu) <= 0.05:
                self.zoom = False

        self.draw_all()

    def btn_path_click (self, **event_args):
        self.paths= []

    def btn_run_click (self, **event_args):
        # This method is called when the button is clicked
        if not self.running:
            self.running  = True
            if self.reset:
                self.initialize()
                #self.init_pos()
            self.reset = False
            self.btn_run.text = "Pause"

        else:
            self.running = False
            self.btn_run.text = "Run"

        #self.cur_path = []
        self.paths.append(self.cur_path)

        #make parameters only editable while reset
        for box in self.param_boxes:
            box.enabled = self.reset


    def btn_reset_click (self, **event_args):
        # This method is called when the button is clicked
        self.running = False
        self.reset = True
        self.btn_run.text = "Run"

        self.t = 0
        self.cur_path = []
        #make parameters only editable while reset
        for box in self.param_boxes:
            box.enabled = self.reset

        self.initialize()
        self.init_pos()

    def draw_all(self):
        canvas = self.canvas
        xu = self.xu
        canvas.xu  = xu
        ball = self.ball
        draw.reset2(canvas, xu)
        draw.clear_canvas(canvas, "#fff")

        #ball
        drawrad = ball.radius*(1/(1+ball.pos.z/3))
        if 0.01>drawrad or drawrad>10:
            self.running = False
            self.btn_run.text = "Run"
        else:
            draw.circle(canvas, drawrad, ball.pos.x, ball.pos.y)
        canvas.fill_style = "rgb(32, 226, 252)"
        canvas.fill()

        #paths
        if not self.running:
            draw.paths(canvas,self.paths, self.line_width, "#000")

        #arrows
        if not self.running:
            draw.vel_arrows(canvas, self.ball, self.line_width, self.arrow_scale)


            draw.reset2(canvas, xu)


        #frame
        draw.border(canvas,5/self.xu, "#000", xu)

    def init_pos(self):
        self.ball.pos.x = self.canvas.get_width()/(2.0*self.xu)
        self.ball.pos.y = self.canvas.get_height()/(2.0*self.xu)
        self.ball.pos.z = 0

    def initialize(self):
        #particles
        index = 0
        for i, button in enumerate(self.buttons):
            if button.selected:
                index = i
        if index == len(self.particle_options):
            mass = 0.1
            Charge = 0
            if float(self.txt_mass.text)>0:
                mass = float(self.txt_mass.text)
            if len(self.txt_charge.text)>0:
                charge = float(self.txt_charge.text)
            self.ball = physics.ball(mass, self.radius, self.ball.pos.x, self.ball.pos.y)
            self.ball.name = self.txt_name.text
            self.ball.charge = charge
        else:
            self.ball = self.particle_options[index]


        v = physics.vector3(self.v, 0)
        if len(self.txt_xsp.text)>0 and len(self.txt_ysp.text)>0:
            v = physics.vector3(float(self.txt_xsp.text), float(self.txt_ysp.text))
        self.ball.vel = v

        #fields
        self.E = physics.vector3(float(self.txt_E_x.text),float(self.txt_E_y.text), float(self.txt_E_z.text))
        self.B = physics.vector3(float(self.txt_B_x.text),float(self.txt_B_y.text), float(self.txt_B_z.text))



    def __init__(self):
        # This sets up a variable for every component on this form.
        # For example, if we've drawn a button called "send_button", we can
        # refer to it as self.send_button:
        self.init_components()

        # Any code you write here will run when the form opens.
        #Uncomment as required.
        self.running= False
        self.reset = True
        self.dt = self.timer.interval/(1e7)
        self.first = True
        self.zoom = False

        self.t = 0
        #SET SCALE (pixels per m, or unit used in code)
        self.xu =5

        self.paths = []
        self.cur_path = []
        self.mousedown = False
        self.mouse = physics.vector3(0,0)

        electron = physics.ball(self.me, self.radius)
        electron.charge  = -self.e
        electron.name = "Electron"

        positron = physics.ball(self.me, self.radius)
        positron.charge = self.e
        positron.name = "Positron"

        alpha = physics.ball(4*self.mp, self.radius)
        alpha.charge = 2*self.e
        alpha.name = "Alpha Particle"

        self.particle_options = [electron, positron, alpha]
        self.buttons = []

        for index, particle in enumerate(self.particle_options):
            button = RadioButton(text= particle.name, value = index, group_name = "radio_particles")
            self.buttons.append(button)
            if index == 0:
                button.selected = True
            self.grid_particles.add_component(button, row = "A", col_xs = 2*index + 1, width_xs = 2)

        self.custom = RadioButton(text = "Custom", value = len(self.particle_options), group_name = "radio_particles")
        self.grid_particles.add_component(self.custom, row ="A", col_xs = 2*len(self.particle_options) + 1, width_xs =2)
        self.buttons.append(self.custom)

        self.param_boxes = self.buttons + self.grid_custom.get_components() + self.grid_fields.get_components()
