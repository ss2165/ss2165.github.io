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
    line_width = 0.001
    bugradius = 0.003
    def timer_tick (self, **event_args):
        # This method is called Every [interval] seconds
        self.cw = self.canvas.get_width()
        self.ch  =self.canvas.get_height()
        ch = self.ch

        canvas = self.canvas
        if self.first:
            self.slid_N = draw.slider(self.can_N, 3, 30, stepsize = 1, start = 4)
            self.slid_v = draw.slider(self.can_v, 0, 1, stepsize = 0.01, start = 0.01)
            self.slid_L = draw.slider(self.can_L, 0.01, 1, stepsize = 0.01, start = 0.1)
            self.L = self.slid_L.value
            self.v =self.slid_v.value
            self.N =self.slid_N.value
            self.param_boxes += [self.slid_N, self.slid_L, self.slid_v]
            self.a = 2*math.pi/self.N
            self.first = False

        L = self.L
        v = self.v
        self.a = 2*math.pi/self.N
        a = self.a
        #distance from centre to middle of one side
        self.d = float(L)*math.sqrt((1+math.cos(a))/(1-math.cos(a)))/2
        d = self.d

        self.xu  =self.give_xu(self.ch, self.d)
        xu = self.xu
        #if self.reset:
        self.initial(canvas)

        draw.reset2(canvas, self.xu)
        self.draw_path(canvas, self.path)

        if self.running:
            self.move_bug(self.bug)
            #self.draw_bugs(canvas, self.bug.pos, "#2a2ac7")
            draw.reset2(canvas, xu)

            if self.bug.pos.mag() <= self.bugradius:
                self.running = False
                self.btn_run.text = "Run"
                #self.initial(canvas)

        # if -0.1 <= self.xu - self.newxu <= 0.1:
        #     self.zoom = False
        # if self.zoom:
        #     self.xu += self.step
        if self.counter %5 == 0:
            self.slid_N.draw()
            self.slid_v.draw()
            self.slid_L.draw()
        self.counter += 1

    def initial(self, canvas):
        draw.reset2(canvas, self.xu)
        draw.clear_canvas(canvas, "#fff")

        self.N  =  self.slid_N.value
        self.L = self.slid_L.value
        self.v = self.slid_v.value

        self.draw_polygon(canvas, self.N, self.L)
        if self.reset:
            self.bug.pos = physics.vector3(-self.L/2, self.d, 0)
            self.path  = [self.bug.pos, self.bug.pos]
        draw.reset2(canvas, self.xu)
        self.draw_bugs(canvas, self.bug.pos, "#2a2ac7")
        # for i in range(len(self.path)-1):
        #     canvas.begin_path()
        #     canvas.move_to(self.path[i].x, self.path[i].y)
        #     canvas.line_to(self.path[i+1].x, self.path[i+1].y)
        #     canvas.stroke()

        draw.reset2(canvas, self.xu)

    def draw_path(self, canvas, poses):
        canvas.translate(self.cw/(2.0*self.xu), self.ch/(2.0*self.xu))
        for i in range(self.N):
            canvas.rotate(self.a)

            canvas.begin_path()
            for j in range(1,len(poses)-1):
                canvas.move_to(poses[j].x, poses[j].y)
                diff = poses[j+1] - poses[j]
                canvas.line_to((poses[j]+0.8*diff).x, (poses[j]+0.8*diff).y)
            if i%2 ==0:
                canvas.stroke_style = "rgb(148, 76, 190)"
            else:
                canvas.stroke_style = "rgb(80, 158, 46)"
            canvas.stroke()


    # def txt_change (self, **event_args):
    #     if len(self.txt_N.text)>0 and len(self.txt_L.text)>0 and len(self.txt_v.text)>0:
    #         if  30 >= int(self.txt_N.text)>2:
    #             self.N  =  int(self.txt_N.text)
    #         if 1>=float(self.txt_L.text)>=0.01:
    #             self.L = float(self.txt_L.text)
    #         if 1>=float(self.txt_v.text)>=0:
    #             self.v = float(self.txt_v.text)
    #         self.zoom = True
    #         self.a = 2*math.pi/self.N
    #
    #         self.oldxu = self.xu
    #         self.d = float(self.L)*math.sqrt((1+math.cos(self.a))/(1-math.cos(self.a)))/2
    #         self.newxu = self.give_xu(self.ch, self.d)
    #         self.step = (self.newxu-self.oldxu)/20
    def give_xu(self, ch, d):
        return (ch/0.5)*(0.12/d)
    def draw_bugs(self, canvas, pos, colour):
        canvas.translate(self.cw/(2.0*self.xu), self.ch/(2.0*self.xu))
        for i in range(self.N):
            canvas.rotate(self.a)
            canvas.translate(pos.x, pos.y)
            draw.circle(canvas, self.bug.radius)
            if i%2 ==0:
                canvas.fill_style = "rgb(148, 76, 190)"
            else:
                canvas.fill_style = "rgb(80, 158, 46)"
            canvas.fill()
            canvas.translate(-pos.x, -pos.y)


    def move_bug(self, bug):
        aim = (bug.pos.phi_rotate(-self.a, physics.vector3(0,0,0)) - bug.pos).norm()
        bug.vel = aim*self.v
        if self.counter % int(1/self.v) ==0:
            self.path.append(bug.pos)
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

        #called when reset button is clicked
        self.running = False
        self.reset = True
        self.btn_run.text = "Run"

        self.t = 0
        self.lbl_t.text = "t = {0}s".format(repr(self.t))
        #make parameters only editable while reset
        for box in self.param_boxes:
            box.enabled = self.reset

        self.counter = 0


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
        self.path  = [self.bug.pos, self.bug.pos]
        self.counter = 0

        self.first = True


        self.dt = self.timer.interval
        self.t = 0
        #list of parameter inputs
        self.param_boxes = []
