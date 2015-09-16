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
"""Anvil form for optical bench simulation."""
from anvil import *
import physics
import draw
import math
import graphs

from slits import slits
from single import single
from grating import grating

class Form1(Form1Template):
    R = 6
    W = 0.3
    x_stp = 0.0005
    line_width = 0.001
    W

    def btn_reset_click (self, **event_args):
        # This method is called when the button is clicked
            #self.running = False
        self.reset = True



    def change(self, **event_args):
        self.wav = self.wav_slider.value*1e-9
        self.wav_slider.draw()
        self.draw_all()

    def draw_all(self):
        draw.reset2(self.canvas, self.xu)
        draw.clear_canvas(self.canvas, "#fff")
        N = int(self.slits.N_slider.value)
        d = float(self.slits.d_slider.value)
        a = float(self.single.a_slider.value)
        n = float(self.grating.n_slider.value)

        if self.aperture == "slits":
            if self.rad_int.selected:
                self.draw_slit_int(N,d,a, self.wav)
            elif self.rad_pat.selected:
                self.draw_slit_pat(N,d,a, self.wav)
        elif self.aperture == "single":
            if self.rad_int.selected:
                self.draw_slit_int(N,d,a, self.wav, "single")
            elif self.rad_pat.selected:
                self.draw_slit_pat(N,d,a, self.wav, "single")

        elif self.aperture == "grating":
            self.draw_grating(n, self.wav)

    def timer_tick (self, **event_args):
        canvas = self.canvas
        self.cw = canvas.get_width()
        self.ch = canvas.get_height()
        cw = self.cw
        ch = self.ch
        dt = self.dt

        if self.first:
            self.xu = float(self.cw)/self.W
            self.wav_slider = draw.slider(self.can_slid, mini= 400, maxi = 700, stepsize = 1, start=510)
            self.wav_slider.maxmin = True
            self.wav = self.wav_slider.value*1e-9
            self.wav_slider.draw()
            self.draw_all()

            self.first = False
        self.change()
        self.slits.N_slider.draw()
        self.slits.d_slider.draw()
        self.single.a_slider.draw()
        self.grating.n_slider.draw()

    def draw_grating(self, n, wav):
        canvas = self.canvas

        draw.reset2(canvas, 1)
        canvas.translate(float(self.cw)/2, 0)
        col = draw.wavelength_to_rgb(self.wav*1e9)

        canvas.line_width = 5
        step = self.wav*n*self.R
        x = 0
        canvas.begin_path()
        while x*self.xu<float(self.cw)/2:
            xt = x*self.xu

            canvas.move_to(xt,0)
            canvas.line_to(xt, float(self.ch))
            canvas.move_to(-xt,0)
            canvas.line_to(-xt, float(self.ch))
            x+=step

        canvas.stroke_style = "rgb({0}, {1}, {2})".format(col[0],col[1],col[2])
        canvas.stroke()
        draw.reset2(canvas, self.xu)


    def draw_slit_pat(self, N,d,a, wav, choice = "slits"):
        canvas = self.canvas
        x_stp = self.x_stp

        canvas.scale(1/self.xu, 1/self.xu)
        col = draw.wavelength_to_rgb(self.wav*1e9)

        canvas.line_width = 2
        for i in range(0,int(self.cw),2):
            canvas.begin_path()
            x = i/self.xu - float(self.W)/2
            ang = math.asin(x/self.R)
            if choice == "slits":
                I = self.slit_int(N,d,wav,ang)
                ma = self.slit_int(N,d,wav,0)
            else:
                I = self.single_int(a,wav,ang)
                ma = 1

            x +=float(self.W)/2
            canvas.move_to(x*self.xu+1,0)
            canvas.line_to(x*self.xu+1, float(self.ch))
            canvas.stroke_style = "rgba({0}, {1}, {2}, {3})".format(col[0],col[1],col[2],math.sqrt(float(I/ma)))
            canvas.stroke()

        canvas.scale(self.xu, self.xu)


    def draw_slit_int(self, N, d, a, wav, choice = "slits"):
        canvas = self.canvas
        x_stp = self.x_stp
        x = []
        fx = []
        for i in range(int(float(self.W)/x_stp)):
            x.append(i*x_stp- float(self.W)/2)
            ang = math.asin((x[i] )/self.R)
            if choice =="slits":
                fx.append(self.slit_int(N,d,wav,ang))
            else:
                fx.append(self.single_int(a,wav,ang))

        graph = graphs.graph_plot(canvas,zip(x,fx))
        graph.yrange[0] = 0
        graph.xlabel = "x/m"
        graph.ylabel = "I"
        graph.axes_enabled = False
        graph.plot()
        draw.reset2(canvas, self.xu)


    def slit_int(self, N, d, wav, theta):
        dl = 2*math.pi*math.sin(theta)*d/wav
        if dl == 0:
             dl += self.x_stp

        y = math.sin(0.5*N*dl)/math.sin(0.5*dl)

        return y**2

    def single_int(self,a, wav, theta):
        dl = math.pi*math.sin(theta)*a/wav
        if dl == 0:
             dl += self.x_stp

        y = math.sin(dl)/dl

        return y**2

    def btn_single_click(self, **event_args):
        self.grid_opt.clear()
        self.single = single()
        self.grid_opt.add_component(self.single)
        self.aperture = "single"
        self.rad_int.enabled = True
        self.change()
        #self.slits.a_slider.draw()
    def btn_grating_click(self, **event_args):
        self.grid_opt.clear()
        self.grating = grating()
        self.grid_opt.add_component(self.grating)
        self.aperture = "grating"
        self.rad_int.enabled = False
        self.rad_pat.selected = True
        self.change()
        #self.slits.n_slider.draw()
    def btn_slits_click(self, **event_args):
        self.grid_opt.clear()
        self.grid_opt.add_component(self.slits)
        self.aperture = "slits"
        self.rad_int.enabled = True
        self.change()
        self.slits.N_slider.draw()
        self.slits.d_slider.draw()


    def __init__(self):
        # This sets up a variable for every component on this form.
        # For example, if we've drawn a button called "send_button", we can
        # refer to it as self.send_button:
        self.init_components()
        #self.mouse = physics.vector3(0,0)
        self.slits = slits()
        # self.slits.txt_N.set_event_handler("pressed_enter", self.change)
        # self.slits.txt_d.set_event_handler("pressed_enter", self.change)
        self.grid_opt.add_component(self.slits)
        self.aperture = "slits"

        self.grating = grating()
        self.single = single()
        #self.single.txt_a.set_event_handler("pressed_enter", self.change)


        #self.grating.txt_n.set_event_handler("pressed_enter", self.change)

        # Any code you write here will run when the form opens.
        #Uncomment as required.
        #self.running= False
        self.reset = True
        self.dt = self.timer.interval
        self.first = True

        #self.t = 0
        #SET SCALE (pixels per m, or unit used in code)
        self.xu = 1

        self.ang_range = 2*math.asin(float(self.W)/(2*self.R))
        #APPEND ALL PARAMETER BOXES
        #self.param_boxes= []
