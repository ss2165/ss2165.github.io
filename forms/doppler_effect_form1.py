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
    default_colour = "#32a4dd"
    default_colour_wave = "#c63939"

    def txt_wave_change (self, **event_args):
        self.wav = float(self.txt_wave.text)
        for point in self.points:
            point.wavelength = self.wav

    def txt_spd_change (self, **event_args):
        self.spd = float(self.txt_spd.text)
        for point in self.points:
            point.speed = self.spd

    def btn_run_click (self, **event_args):

        # This method is called when the button is clicked
        if not self.running:
            self.running  = True
            self.reset = False
            self.btn_run.text = "Pause"

        else:
            self.running = False
            self.btn_run.text = "Run"


    def btn_reset_click (self, **event_args):
        # This method is called when the button is clicked
        self.running = False
        self.reset = True
        self.btn_run.text = "Run"
        self.initalize()
        self.init_pos(self.points)
        for point in self.points:
            point.wavefront = 0
        self.pulses = []
        self.t = 0
        self.draw_all()


    def draw_all(self):
        canvas = self.canvas
        draw.reset2(self.canvas, self.xu)
        draw.clear_canvas(self.canvas, "#fff")
        big = math.sqrt((self.cw/self.xu*1.0)**2 + (self.ch/self.xu*1.0)**2)


        for point in self.points:
            point.vel.x = self.spd_slider.value*0.1
            self.draw_source(point, self.canvas)
        for point in self.pulses:
            if point.wavefront >big:
                self.pulses.remove(point)
            else:
                self.draw_source(point, self.canvas, colour = "#fff")

    def draw_source(self,point, canvas, colour = default_colour, wave_colour = default_colour_wave, thickness = 0.003):
        xu = self.xu
        cw = self.cw
        ch = self.ch

        #point
        draw.circle(canvas, point.radius, x= point.pos.x, y = point.pos.y)
        canvas.fill_style = colour
        canvas.fill()

        big = math.sqrt((self.cw/xu*1.0)**2 + (self.ch/xu*1.0)**2)

        if point.wavefront + point.wavelength <big:
            rad = point.wavefront
            draw.circle(canvas, rad, x= point.pos.x, y = point.pos.y)
            canvas.stroke_style = wave_colour
            canvas.line_width = thickness
            canvas.stroke()



    def timer_tick (self, **event_args):
        canvas = self.canvas
        self.cw = canvas.get_width()
        self.ch = canvas.get_height()
        cw = self.cw
        ch = self.ch
        dt = self.dt

        if self.first:
            self.xu = self.cw
            self.initalize()
            self.init_pos(self.points)

            self.spd_slider = draw.slider(self.can_slid, mini= 0.1, maxi = 3, stepsize = 0.1, start=0.6, colour = self.default_colour_wave)
            self.spd_slider.indicator = True
            for point in self.points:
                point.vel.x = self.spd_slider.value*0.1
            self.spd_slider.draw()
            self.draw_all()
            self.first = False

        if self.running:
            for point in self.points:
                point.move(dt)
                gap = int(float(self.wav)/(self.spd*dt))

                #point.radiate(dt)
                if int(float(self.t)/dt) % gap ==0:
                    new = physics.point_source(radius = 0.0001, speed= self.spd, wavelength = self.wav)
                    new.pos = point.pos*1

                    self.pulses.append(new)
            for point in self.pulses:
                point.radiate(dt)
            self.draw_all()

        self.t += self.dt

    def init_pos(self,points):
        self.points[0].pos = physics.vector3(0.05, self.ch/(2.0*self.xu))
        #self.points[1].pos = physics.vector3(self.cw/(2.0*self.xu) + 0.05, self.ch/(2.0*self.xu))

    def initalize(self):
        self.spd = 0.1
        self.wav = float(self.txt_wave.text)
        self.point1 = physics.point_source(radius = 0.01, speed= 0, wavelength = self.wav)
        self.point1.vel = physics.vector3(0.1,0)
        self.points = [self.point1]
        for point in self.points:
            point.mousedown = False

    def __init__(self):
        # This sets up a variable for every component on this form.
        # For example, if we've drawn a button called "send_button", we can
        # refer to it as self.send_button:
        self.init_components()
        self.points = []
        self.pulses = []
        self.initalize()


        self.mouse = physics.vector3(0,0)
        self.moved = 0

        # Any code you write here will run when the form opens.
        #Uncomment as required.
        self.running= False
        self.reset = True
        self.dt = self.timer.interval
        self.first = True



        self.t = 0
        #SET SCALE (pixels per m, or unit used in code)


        #APPEND ALL PARAMETER BOXES
        self.param_boxes= []
