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
# limitations under the License.

import math

class slider():
    """Canvas slider object

    Create a slider between mini and maxi with indicator of given colour which can take values in steps of stepsize.
    The starting position is given by start.
    Current value is given in the value attribute.
    Default colour is blue. Optional colour must be given in hex string form.
    Minimum canvas height 40px for standard, 50px with indicators.

    Attributes:
        mini --
        maxi --
        stepsize --
        value --
        mousedown --
        indicator --
        maxmin --
        base_colour --
        enabled --

    *Code template*
    Mouse canvas links:
        def [canvas_name]_mouse_move (self, x, y, **event_args):
            self.[slider_name].mouse_move(x, y)
            self.[slider_name].draw()
        def [canvas_name]_mouse_up (self, x, y, button, **event_args):
            self.[slider_name].mouse_up(x, y)
            self.[slider_name].draw()
        def [canvas_name]_mouse_down (self, x, y, button, **event_args):
            self.[slider_name].mouse_down(x, y)
            self.[slider_name].draw()
    """

    default_colour = "#318fdb"
    def __init__(self, canvas, mini, maxi, stepsize, start = 0, colour = default_colour, change_event = None):
        if not mini <= start <= maxi:
            raise "Start value not within range specified."
        self.mini = mini
        self.maxi = maxi
        self.stepsize = stepsize
        self.canvas = canvas
        self.change_event = change_event

        self.cw = canvas.get_width()
        self.ch = canvas.get_height()

        self.range = maxi - mini
        self.scale = float(self.cw) / self.range

        self.value = start

        self.mousedown = False

        self.base_colour = colour
        self.colour = colour

        self.indicator  = True
        self.maxmin = True

        self.grabber_side =15
        self.enabled = True

        self.map_mouse()
        self.draw()

    def draw(self):
        canvas = self.canvas
        self.cw = canvas.get_width()
        self.ch = canvas.get_height()
        reset2(self.canvas, 1)
        clear_canvas(canvas, "#fff")
        self.centre = self.ch - self.grabber_side/2 -5
        centre = self.centre
        font_size = 14
        font = "{0}px sans-serif".format(int(font_size))

        if self.maxmin:
            mini_str = "{}".format(repr(self.mini))
            maxi_str = "{}".format(repr(self.maxi))

            mini_size = canvas.measure_text(mini_str)
            maxi_size = canvas.measure_text(maxi_str)
            if mini_size > maxi_size:
                mini_size, maxi_size = maxi_size, mini_size
            self.horpad = maxi_size + 5
        else:
            self.horpad = 10

        horpad = self.horpad
        self.scale = (float(self.cw) - 2*horpad)/ self.range

        #line
        canvas.begin_path()
        canvas.move_to(horpad, centre)
        canvas.line_width = 4
        canvas.line_cap = "round"
        canvas.line_to(self.cw-horpad, centre)
        canvas.shadow_blur = 0
        canvas.stroke_style = "#404040"
        canvas.stroke()

        #grabber
        grabber_side = self.grabber_side
        triangle_centre = centre - grabber_side*(1+1/math.sqrt(3))/2
        polygon(canvas, 3, grabber_side, (self.value - self.mini)*self.scale+ horpad, triangle_centre)
        canvas.fill_style = self.colour
        canvas.fill()
        reset2(self.canvas, 1)
        polygon(canvas, 4, grabber_side, (self.value - self.mini)*self.scale + horpad, centre)
        canvas.shadow_blur = 2 if self.mousedown else 5
        canvas.shadow_color = "black"
        canvas.fill_style = self.colour
        canvas.fill()
        reset2(self.canvas, 1)

        #indicator
        if self.indicator:
            value_str = "{0}".format(repr(self.value))

            canvas.font = font
            text_width = canvas.measure_text(value_str)

            canvas.fill_style = "#000"
            canvas.shadow_blur = 0
            height_offset = self.grabber_side*0.5*(1+math.sqrt(3)) + 1.1*font_size
            canvas.translate((self.value - self.mini)*self.scale - text_width/2 + horpad, centre - height_offset)
            canvas.scale(1, -1)
            canvas.fill_text(value_str, 0, 0)
            reset2(canvas, 1)

        #maxmin labels
        if self.maxmin:
            canvas.font = font

            #min
            canvas.fill_style = "#000"
            canvas.shadow_blur = 0
            height_offset = float(font_size)/2 - 2
            canvas.translate(0, centre- height_offset)
            canvas.scale(1, -1)
            canvas.fill_text(mini_str, 0, 0)
            reset2(canvas, 1)

            canvas.translate(self.cw - horpad + 5, centre - height_offset)
            canvas.scale(1, -1)
            canvas.fill_text(maxi_str, 0, 0)
            reset2(canvas, 1)

    def map_mouse(self):
        canvas = self.canvas
        canvas.set_event_handler("mouse_up", self.mouse_up)
        canvas.set_event_handler("mouse_leave", self.mouse_leave)
        canvas.set_event_handler("mouse_down", self.mouse_down)
        canvas.set_event_handler("mouse_move", self.mouse_move)

    def mouse_down(self, x, y, button, **event_args):
        if self.enabled and self.horpad < x <self.cw- self.horpad:
            self.mousedown = True
            if x<self.cw/2:
                self.value = int(((x -self.horpad)/self.scale + self.mini)/self.stepsize)*self.stepsize
            else:
                self.value = int(1+((x -self.horpad)/self.scale + self.mini)/self.stepsize)*self.stepsize
            self.draw()

    def mouse_move(self, x, y, **event_args):
        y=self.ch-y
        if self.enabled:
            xcheck = abs((x -self.horpad) - (self.value - self.mini)*self.scale) <= self.grabber_side
            ycheck = abs(self.centre - y)<=self.grabber_side
            if xcheck and ycheck:
                self.colour = "#{0:x}".format(int(self.base_colour[1:], 16)+0x202020)
            else:
                self.colour = self.base_colour

            if self.mousedown and self.horpad < x <self.cw- self.horpad:
                if x<self.cw/2:
                    self.value = int(((x -self.horpad)/self.scale + self.mini)/self.stepsize)*self.stepsize
                else:
                    self.value = int(1+((x -self.horpad)/self.scale + self.mini)/self.stepsize)*self.stepsize

            self.draw()

    def mouse_up(self, x, y, button, **event_args):
        self.mousedown = False
        self.draw()

    def mouse_leave(self, x, y,**event_args):
        self.mousedown = False
        self.draw()



def eq_triangle(canvas, side, x= 0, y= 0):
    #draws upward equilateral triangle with bottom left corner at origin
    canvas.translate(x,y)
    canvas.begin_path()
    canvas.move_to(0,0)
    canvas.line_to(float(side), 0)
    canvas.line_to(float(side)/2, math.sqrt(3))
    canvas.close_path()
    canvas.translate(-x,-y)

def circle(canvas, radius, x= 0, y= 0):
    #draw circle of radius
    canvas.begin_path()
    canvas.arc(x, y, float(radius), 0, 2*math.pi)
    canvas.close_path()

def arrow(canvas, length, width, x= 0, y= 0):
    #draws horizontal arrow of length and width starting at middle of base
    canvas.translate(x,y+ width/2)
    canvas.begin_path()
    canvas.move_to(0,0)
    canvas.line_to(0.8*length, 0)
    canvas.line_to(0.8*length, 1.5*width/2)
    canvas.line_to(length, -width/2)
    canvas.line_to(0.8*length, -3.5*width/2)
    canvas.line_to(0.8*length, -width)
    canvas.line_to(0, -width)
    canvas.close_path()
    canvas.translate(-x,-y-width/2)

def polygon(canvas, sides, length, x= 0, y= 0):
    canvas.translate(x,y)
    N = sides
    l = length
    a = 2*math.pi/N
    #distance from centre to middle of one side
    d = float(l)*math.sqrt((1+math.cos(a))/(1-math.cos(a)))/2
    canvas.begin_path()
    canvas.move_to(-l/2, d)
    for i in range(N):
        canvas.rotate(a)
        canvas.line_to(-l/2, d)
    canvas.close_path()
    canvas.translate(-x,-y)

def dashed_line(canvas, dashlength, x2, y2, x=0, y= 0):
    length = math.sqrt((x2-x)**2 + (y2-y)**2)
    no = int(length/dashlength)
    if no>0:
        dx= float(x2-x)/no
        dy = float(y2-y)/no

        factor = 0.8

        canvas.move_to(x,y)

        for i in range(no):
            canvas.line_to(x+(i+factor)*dx, y+(i+factor)*dy)
            canvas.move_to(x + (i+1)*dx, y + (i+1)*dy)
    else:
        pass

def paths(canvas, paths, thickness, colour):
    canvas.begin_path()
    for path in paths:
        if len(path)>2:
            for i in range(len(path)-1):
                canvas.move_to(path[i].x, path[i].y)
                diff = path[i+1] - path[i]
                new  = path[i] + diff*0.8
                canvas.line_to(new.x, new.y)

    canvas.line_width = thickness
    canvas.stroke_style = colour
    canvas.stroke()

def vel_arrows(canvas, ball, line_width, arrow_scale = 0.15):
    #x component
    arrow(canvas, ball.vel.x*arrow_scale, 2*line_width, ball.pos.x, ball.pos.y)
    canvas.fill_style = "#333333"
    canvas.fill()

    #y component
    canvas.translate(ball.pos.x, ball.pos.y)
    canvas.rotate(math.pi/2)
    arrow(canvas, ball.vel.y*arrow_scale, 2*line_width)
    canvas.fill()
    canvas.rotate(-math.pi/2)

    #velocity vector

    if ball.vel.y>0:
        canvas.rotate(ball.vel.phi())
    else:
        canvas.rotate(-ball.vel.phi())
    arrow(canvas, ball.vel.mag()*arrow_scale, 4*line_width)
    canvas.fill_style = "#49902a"
    canvas.fill()


def cart_arrows(canvas, vector, line_width, arrow_scale = 0.15, colours = {'x':"#444242",'y':"#444242",'z':"#444242"}, x= 0, y=0 ):
    #z component
    canvas.shadow_blur = 4
    canvas.translate(x, y)
    canvas.rotate(math.pi/6 + math.pi)
    canvas.scale(10*line_width, 10*line_width)
    canvas.begin_path()
    dashed_line(canvas, 0.2, 1,0)
    canvas.line_width = 0.06
    canvas.stroke()
    canvas.scale(0.1/line_width, 0.1/line_width)
    arrow(canvas, vector.z*arrow_scale, 1.5*line_width)
    canvas.fill_style = colours['z']
    canvas.fill()
    canvas.rotate(-math.pi/6- math.pi)

    #x component
    canvas.scale(10*line_width, 10*line_width)
    canvas.begin_path()
    dashed_line(canvas, 0.2,1.0 ,0)
    canvas.stroke()
    canvas.scale(0.1/line_width, 0.1/line_width)
    arrow(canvas, vector.x*arrow_scale, 2*line_width)
    canvas.fill_style = colours['x']
    canvas.fill()

    #y component
    canvas.translate(line_width,0)
    canvas.rotate(math.pi/2)
    canvas.scale(10*line_width, 10*line_width)
    canvas.begin_path()
    dashed_line(canvas, 0.2,1.0 ,0)
    canvas.stroke()
    canvas.scale(0.1/line_width, 0.1/line_width)
    arrow(canvas, vector.y*arrow_scale, 2*line_width)
    canvas.fill_style = colours['y']
    canvas.fill()
    canvas.rotate(-math.pi/2)
    canvas.translate(-line_width,0)

    canvas.translate(-x,-y)


def btn_run_click(self):
    #standard switching run button
    if not self.running:
        self.running  = True
        self.reset = False
        self.btn_run.text = "Pause"

    else:
        self.running = False
        self.btn_run.text = "Run"

def btn_reset_click (self):
    #called when reset button is clicked
    self.running = False
    self.reset = True
    self.btn_run.text = "Run"

def reset2(canvas, xu):
    #custom reset function, scales to metres (xu = pixels per m), and places origin at bottom left
    canvas.reset_transform()
    canvas.translate(0, canvas.get_height())
    canvas.scale(xu,-xu)

def clear_canvas(canvas, colour = "#fff"):
    canvas.fill_style= colour
    canvas.fill_rect(0, 0, canvas.get_width(), canvas.get_height())

def border(canvas, thickness, colour, xu):
    canvas.begin_path()
    canvas.line_width = thickness/xu
    canvas.stroke_style = colour
    canvas.stroke_rect(0, 0, canvas.get_width()/xu, canvas.get_height()/xu)

def wavelength_to_rgb(wavelength, gamma=0.8):
    '''This converts a given wavelength of light to an
    approximate RGB color value. The wavelength must be given
    in nanometers in the range from 380 nm through 750 nm
    (789 THz through 400 THz).

    Based on code by Dan Bruton
    http://www.physics.sfasu.edu/astro/color/spectra.html
    '''

    wavelength = float(wavelength)
    if wavelength >= 380 and wavelength <= 440:
        attenuation = 0.3 + 0.7 * (wavelength - 380) / (440 - 380)
        R = ((-(wavelength - 440) / (440 - 380)) * attenuation) ** gamma
        G = 0.0
        B = (1.0 * attenuation) ** gamma
    elif wavelength >= 440 and wavelength <= 490:
        R = 0.0
        G = ((wavelength - 440) / (490 - 440)) ** gamma
        B = 1.0
    elif wavelength >= 490 and wavelength <= 510:
        R = 0.0
        G = 1.0
        B = (-(wavelength - 510) / (510 - 490)) ** gamma
    elif wavelength >= 510 and wavelength <= 580:
        R = ((wavelength - 510) / (580 - 510)) ** gamma
        G = 1.0
        B = 0.0
    elif wavelength >= 580 and wavelength <= 645:
        R = 1.0
        G = (-(wavelength - 645) / (645 - 580)) ** gamma
        B = 0.0
    elif wavelength >= 645 and wavelength <= 750:
        attenuation = 0.3 + 0.7 * (750 - wavelength) / (750 - 645)
        R = (1.0 * attenuation) ** gamma
        G = 0.0
        B = 0.0
    else:
        R = 0.0
        G = 0.0
        B = 0.0
    R *= 255
    G *= 255
    B *= 255
    return (int(R), int(G), int(B))

class graph_plot():

    def __init__(self, canvas, values):
        self.canvas = canvas
        self.x = []
        self.fx = []
        for value in values:
            self.x.append(value[0])
            self.fx.append(value[1])

        self.yrange = [min(self.fx), max(self.fx)]
        self.xrange = [min(self.x), max(self.x)]

        self.line_width = 2

        self.axes_enabled = True
        self.markers_enabled = True
        self.gridlines_enabled = True
        self.axes_width = 4

        self.xlabel = ""
        self.ylabel = ""

    def func(self,values):
        self.x = []
        self.fx = []
        for value in values:
            self.x.append(value[0])
            self.fx.append(value[1])

    def transform(self):
        canvas = self.canvas
        cw = canvas.get_width()
        ch = canvas.get_height()

        self.font_size = 14
        font_size = self.font_size
        self.font = "{0}px sans-serif".format(font_size)
        font = self.font
        canvas.font = font

        if self.xlabel != "":
            label_size = canvas.measure_text(self.xlabel)
            self.horpad = label_size + 15 + self.axes_width
        else:
            self.horpad = 10

        if self.ylabel != "":
            label_size = font_size
            self.verpad = label_size + 15 + self.axes_width
        else:
            self.verpad = 10

        horpad = self.horpad
        verpad = self.verpad

        self.xu = float(cw - 2*horpad)/(self.xrange[1]- self.xrange[0])
        self.yu = float(ch - 2*verpad)/(self.yrange[1]- self.yrange[0])
        canvas.scale(self.xu, self.yu)
        canvas.translate(-self.xrange[0] + horpad/self.xu, -self.yrange[0] + verpad/self.yu)

    def axes_transform(self):
        canvas = self.canvas
        cw = canvas.get_width()
        ch = canvas.get_height()


    def plot(self, colour = "#198dbf", xmarker = None, ymarker = None):
        canvas = self.canvas
        x = self.x
        fx = self.fx
        cw = canvas.get_width()
        ch = canvas.get_height()
        reset2(canvas, 1)
        #clear_canvas(canvas, "#fff")
        self.transform()

        canvas.begin_path()

        for i in range(len(self.x)):

            if i ==0:
                canvas.move_to(x[i], fx[i])
            xcheck = self.xrange[0] <= x[i] <=self.xrange[1]
            ycheck = self.yrange[0] <= fx[i] <=self.yrange[1]
            if xcheck and ycheck:
                xcheck2 =abs(x[i] - x[i-1]) <= 100/self.xu
                ycheck2 = abs(fx[i] - fx[i-1]) <=100/self.yu

                if xcheck2 and ycheck2:
                    canvas.line_to(x[i], fx[i])
                else:
                    canvas.move_to(x[i], fx[i])
            else:
                canvas.move_to(x[i], fx[i])


        canvas.stroke_style = colour
        reset2(canvas, 1)
        canvas.line_width = self.line_width
        canvas.stroke()

        minus = 1

        canvas.translate(self.horpad, self.verpad)
        cw -= self.horpad*2
        ch -= self.verpad*2

        if self.axes_enabled:
            xr = [self.xrange[0]*self.xu, self.xrange[1]*self.xu]
            yr = [self.yrange[0]*self.yu, self.yrange[1]*self.yu]

            yzero = -xr[0]
            xzero = -yr[0]

            if not xr[0] <= 0 <= xr[1]:
                if xr[0]>0:
                    yzero = 0
                else:
                    minus = -1
                    yzero = cw
            if not yr[0] <= 0 <= yr[1]:
                if yr[0]>0:
                    xzero = 0
                else:
                    xzero = ch
            self.xzero = xzero
            self.yzero = yzero

            canvas.begin_path()
            canvas.move_to(yzero, 0)
            canvas.line_to(yzero, (yr[1]-yr[0]))
            canvas.move_to(0, xzero)
            canvas.line_to((xr[1]- xr[0]), xzero)

            canvas.stroke_style = "#444444"
            canvas.line_width = self.axes_width
            canvas.stroke()

            canvas.fill_style = "#000"

            if self.xlabel != "":
                canvas.translate((xr[1]  - xr[0]) +  15, xzero- self.axes_width )
                canvas.scale(1, -1)
                canvas.fill_text(self.xlabel, 0, 0)
                reset2(canvas, 1)
                canvas.translate(self.horpad, self.verpad)
            if self.ylabel != "":
                canvas.translate(yzero- canvas.measure_text(self.ylabel)/2, (yr[1]- yr[0]) + 15 )
                canvas.scale(1, -1)
                canvas.fill_text(self.ylabel, 0, 0)
            reset2(canvas, 1)
            canvas.translate(self.horpad, self.verpad)


                #markers

            if xmarker != None:
                self.xmarker = float(xmarker*self.xu)
            else:
                self.xmarker = (xr[1] - xr[0])/10

            if ymarker != None:
                self.ymarker = float(ymarker*self.yu)
            else:
                self.ymarker = (yr[1] - yr[0])/10



            if self.gridlines_enabled:
                x = self.xmarker
                y = self.ymarker

                canvas.begin_path()
                while -1 <= -x + yzero  or x + yzero <= cw+1:
                    if x + yzero <= cw+1:
                        canvas.move_to((x + yzero), ch)
                        canvas.line_to((x+ yzero), 0)
                    if -1 <= -x + yzero:
                        canvas.move_to((-x+ yzero), ch)
                        canvas.line_to((-x+ yzero), 0)
                    x += self.xmarker

                while -1 <= -y + xzero  or y + xzero <= ch+1:
                    if y + xzero <= ch+1:
                        canvas.move_to(0, (y + xzero))
                        canvas.line_to(cw, (y + xzero))
                    if  -1 <= -y + xzero:
                        canvas.move_to(0, -y + xzero)
                        canvas.line_to(cw, -y + xzero)
                    y += self.ymarker

                canvas.line_width = int(self.axes_width/4)
                canvas.stroke_style = "#969696"
                canvas.stroke()

            if self.markers_enabled:
                x = 0
                y = 0
                canvas.translate(yzero, xzero)
                canvas.begin_path()
                while -1 <= -x + yzero  or x + yzero <= cw+1:
                    if x + yzero <= cw+1:
                        canvas.move_to((x), 5)
                        canvas.line_to((x), - 5)
                    if -1 <= -x + yzero:
                        canvas.move_to(-(x), 5)
                        canvas.line_to(-(x), - 5)
                    font_size = self.font_size - 4
                    canvas.font = "{0}px sans-serif".format(font_size)

                    num = (x + xr[0] + yzero)/self.xu
                    if xr[0] <=0 <= xr[1]:
                        num +=0
                    elif xr[0] < 0:
                        num -= 2*xr[1]/self.xu

                    if x + yzero <= cw+1:
                        canvas.translate((x), - 2 +font_size)
                        canvas.scale(1, -1)
                        st = self.num_string(num)
                        canvas.fill_text(st, 0, 0)
                        canvas.scale(1,-1)
                        canvas.translate(-(x), 2 - font_size)
                    if -1 <= -x + yzero:
                        canvas.translate(-(x),  - 2 +font_size)
                        canvas.scale(1,-1)
                        st = self.num_string(-num)
                        canvas.fill_text(st, 0, 0)
                        canvas.scale(1,-1)
                        canvas.translate((x), 2 - font_size)

                    x += self.xmarker

                while -1 <= -y + xzero  or y + xzero <= ch+1:
                    if y + xzero <= ch+1:
                        canvas.move_to(-5, (y))
                        canvas.line_to(5, (y))
                    if  -1 <= -y + xzero:
                        canvas.move_to(-5, -(y))
                        canvas.line_to(5, -(y))
                    font_size = self.font_size - 4
                    canvas.font = "{0}px sans-serif".format(font_size)

                    num = (y + yr[0] + xzero)/self.yu
                    if yr[0] <=0 <= yr[1]:
                        num +=0
                    elif yr[0] < 0:
                        num -= 2*yr[1]/self.yu

                    if y + xzero <= ch+1:
                        canvas.translate(7, (y) )
                        canvas.scale(1, -1)
                        st = self.num_string(num)
                        canvas.fill_text(st, 0, 0)
                        canvas.scale(1,-1)
                        canvas.translate(-7, -(y) )
                    if  -1 <= -y + xzero:
                        canvas.translate(7, -(y))
                        canvas.scale(1, -1)
                        st = self.num_string(-num)
                        canvas.fill_text(st, 0, 0)
                        canvas.scale(1,-1)
                        canvas.translate(-7, (y) )

                    y += self.ymarker
                canvas.line_width = int(self.axes_width/2)
                canvas.stroke_style = "#444444"
                canvas.stroke()
        reset2(canvas, 1)

    def num_string(self,n):
        if n == 0:
            return "0"
        elif abs(n) < 1e-3:
            return "{:.3e}".format(n)
        elif abs(n)<1:
            return "{:.3g}".format(n)
        elif 1<=abs(n)<=100:
            return "{:g}".format(round(n, 2))
        elif abs(n) < 1e4:
            return "{}".format(round(int(n), 3))
        else:
            return "%3.3e" % n

    def circle_points(self, points, colour, pointlabels = None, pointoffset = 0):
        canvas = self.canvas

        self.transform()

        canvas.begin_path()

        for i in range(len(points)):
            x,y = points[i]
            canvas.translate(x, y)

            canvas.scale(1/self.xu, 1/self.yu)
            canvas.move_to(self.line_width*5, 0)
            canvas.arc(0, 0, self.line_width*4, 0, 2*math.pi)
            canvas.scale(1, -1)
            text = ""
            if pointlabels != None:
                text = pointlabels[i]
            else:
                text = chr(i+65 + pointoffset)

            canvas.fill_text(text, 15, 15)
            canvas.scale(self.xu, -self.yu)
            canvas.translate(-x, -y)

        canvas.stroke_style = colour
        reset2(canvas, 1)
        canvas.line_width = self.line_width*2
        canvas.stroke()
