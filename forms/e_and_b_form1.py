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
            self.first = False

        ball = self.ball
        if self.running:
            ball.vel += dt*(self.E + ball.vel.cross(self.B))*ball.charge/ball.mass
            ball.move(dt)
        self.draw_all()

    def btn_run_click (self, **event_args):
        # This method is called when the button is clicked
        if not self.running:
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
        # This method is called when the button is clicked
        self.running = False
        self.reset = True
        self.btn_run.text = "Run"

        #make parameters only editable while reset
        for box in self.param_boxes:
            box.enabled = self.reset

        self.initialize()

    def draw_all(self):
        canvas = self.canvas
        xu = self.xu
        ball = self.ball
        draw.reset2(canvas, xu)
        draw.clear_canvas(canvas, "#fff")

        #ball
        draw.circle(canvas, ball.radius, ball.pos.x, ball.pos.y)
        canvas.fill_style = "rgb(32, 226, 252)"
        canvas.fill()
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
            self.ball = physics.ball(mass, self.radius)
            self.ball.name = self.txt_name.text
            self.ball.chage = charge
        else:
            self.ball = self.particle_options[index]

        self.ball.pos.x=self.ball.radius
        self.ball.pos.y = self.canvas.get_height()/(2.0*self.xu)
        self.ball.vel.x = self.v
        self.ball.vel.y = 0

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

        self.t = 0
        #SET SCALE (pixels per m, or unit used in code)
        self.xu =5



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
