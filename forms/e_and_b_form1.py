# Copyright 2015 Seyon Sivarajah
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License
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
    line_width = 0.02
    arrow_scale = 0.5e-7
    trail_buffer = 20

    def check_paths_change(self, **event_args):
        self.draw_all()
    def check_trail_change(self, **event_args):
        self.draw_all()
    def txt_change(self, **event_args):
        Ex  = self.txt_E_x.text
        Ey  = self.txt_E_y.text
        Ez  = self.txt_E_z.text
        Bx  = self.txt_B_x.text
        By  = self.txt_B_y.text
        Bz  = self.txt_B_z.text
        if len(Ex)>0 and len(Ey)>0 and len(Ez)>0:
            self.E = physics.vector3(float(self.txt_E_x.text),float(self.txt_E_y.text), float(self.txt_E_z.text))
        if len(Bx)>0 and len(By)>0 and len(Ez)>0:
            self.B = physics.vector3(float(self.txt_B_x.text),float(self.txt_B_y.text), float(self.txt_B_z.text))
        self.draw_all()

    def canvas_mouse_move(self, x, y, **event_args):
        # This method is called when the mouse cursor moves over this component
        #record mouse pos
        self.mouse.x = x/self.xu
        self.mouse.y = (self.ch-y)/self.xu

        #change text box value based on where mouse is
        if self.mousedown:
            self.ball.pos += self.mouse - self.ball.pos
            self.draw_all()

        if self.arrowdown:
            newvel = (self.mouse - self.ball.pos)/self.arrow_scale
            self.txt_xsp.text = "{:.3g}".format(newvel.x)
            self.txt_ysp.text = "{:.3g}".format(newvel.y)

            self.ball.vel.x = float(self.txt_xsp.text)
            self.ball.vel.y = float(self.txt_ysp.text)

            self.draw_all()
    def canvas_mouse_up(self, x, y, button, **event_args):
    # This method is called when a mouse button is released on this component
        self.mousedown = False
        self.arrowdown = False
        self.draw_all()

    def canvas_mouse_down(self, x, y, button, **event_args):
        # This method is called when a mouse button is pressed on this component
        self.mouse.x = x/self.xu
        self.mouse.y = (self.ch-y)/self.xu
        #if mouse is within a ball, record it
        if (self.ball.pos - self.mouse).mag() <=self.ball.radius and self.reset:
            self.mousedown= True
            self.draw_all()

        if (self.mouse - self.ball.pos - 0.9*self.arrow_scale*self.ball.vel).mag()<= 0.2*(self.arrow_scale*self.ball.vel).mag() and self.reset:
            self.arrowdown = True
            self.draw_all()

    def accel(self, t, y):
        return (self.E + y.cross(self.B))*self.ball.charge/self.ball.mass

    def timer_tick(self, **event_args):
        canvas = self.canvas
        self.cw = canvas.get_width()
        self.ch = canvas.get_height()
        cw = self.cw
        ch = self.ch
        dt = self.dt
        old = self.old
        self.grid_custom.visible = self.custom.selected

        if self.first:
            self.xu = cw/10.0
            self.initialize()
            self.init_pos()
            self.slider1 = draw.slider(self.can_slid, mini= 0.1, maxi = 4, stepsize = 0.1, start=1)
            self.slider1.maxmin = True
            self.slider1.draw()
            self.param_boxes.append(self.slider1)
            self.first = False
            self.draw_all()


        ball = self.ball
        if self.running:
            #dtt = dt/30
            # for i in range(30):
            #     ball.vel += dtt*(self.E + ball.vel.cross(self.B))*ball.charge/ball.mass
            # ball.move(dt)
            ball.vel = physics.runge_kutta4(ball.vel, self.accel, self.t, dt)
            ball.move(dt)
            if int(self.t/self.dt) %6 ==0:
                self.cur_path.append(self.ball.pos)
            self.trail.append(self.ball.pos)
            if len(self.trail)>self.trail_buffer:
                self.trail = self.trail[1:]
            self.t += dt
            self.draw_all()

        new = self.slider1.value

        if new != old:
            scale = self.slider1.value
            #self.oldxu  = 1.0*self.xu
            self.xu = self.cw/10.0*scale
            # self.xu += (self.newxu-self.oldxu)/20
            #self.init_pos()
            # if -0.05 <=(self.xu - self.newxu) <= 0.05:
            #     self.zoom = False

            self.draw_all()
        self.slider1.draw()
        old = new*1

    def btn_path_click(self, **event_args):
        self.paths= []
        self.draw_all()

    def btn_run_click(self, **event_args):
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

        self.draw_all()

    def btn_reset_click(self, **event_args):
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

        self.draw_all()

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
        canvas.fill_style = "rgb(30, 96, 139)"
        canvas.fill()

        if self.running and self.check_trail.checked:
            b = len(self.trail)
            canvas.begin_path()
            canvas.move_to(self.trail[0].x, self.trail[0].y)
            canvas.quadratic_curve_to(self.trail[int(b/2)].x, self.trail[int(b/2)].y, self.trail[-1].x, self.trail[-1].y)
            canvas.line_width = 0.03
            canvas.stroke()

        #paths
        if not self.running and self.check_paths.checked:
            draw.paths(canvas,self.paths, self.line_width, "#000")

        #arrows
        if not self.running:
            draw.vel_arrows(canvas, self.ball, self.line_width, self.arrow_scale)
            draw.reset2(canvas, xu)

        #field arrows
        canvas.scale(1.0/self.xu, 1.0/self.xu)
        draw.cart_arrows(canvas, self.E, 3, 100/((self.E.mag()+1)), x = 30, y = 50)
        B2 = self.B*10e3
        draw.cart_arrows(canvas, B2, 3, 100/((B2.mag()+1)), x = (self.cw - 80), y = 50)
        canvas.scale(1,-1)
        canvas.font= "20px sans-serif"
        canvas.fill_text("E",50, -30 )
        canvas.fill_text("B",(self.cw - 60), -30 )
        canvas.scale(self.xu, -self.xu)


        #frame
        draw.border(canvas,5, "#000", xu)

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

        self.trail = [self.ball.pos]
        self.draw_all()

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
        self.old = 1
        self.paths = []
        self.cur_path = []
        self.trail= []
        self.mousedown = False
        self.arrowdown = False
        self.mouse = physics.vector3(0,0)

        electron = physics.ball(self.me, self.radius)
        electron.charge  = -self.e
        electron.name = "Electron"
        electron.E = physics.vector3(0, 1e3, 0)
        electron.B = physics.vector3(0, 0, 5e-3)

        positron = physics.ball(self.me, self.radius)
        positron.charge = self.e
        positron.name = "Positron"
        positron.E = physics.vector3(0, 1e3, 0)
        positron.B = physics.vector3(0, 0, 5e-3)

        alpha = physics.ball(4*self.mp, self.radius)
        alpha.charge = 2*self.e
        alpha.name = "Alpha Particle"
        alpha.E = physics.vector3(0, 1e5, 0)
        alpha.B = physics.vector3(0, 0, 5e-1)

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

        self.param_boxes = self.buttons + self.grid_custom.get_components() + self.grid_fields.get_components() + self.grid_vel.get_components()
