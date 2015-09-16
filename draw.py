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
"""Anvil service module for drawing objects and methods, used with the canvas component.

Classes:
slider -- canvas based slider object for anvil apps.

Functions:
reset2 -- scale canvas and move origin to bottom left.
clear_canvas -- clear the canvas.
border -- draw border on canvas.
eq_triangle -- draw equilateral triangle.
circle -- draw a circle.
arrow -- draw standard arrow.
polygon -- draw a regular polygon.
dashed_line -- draw a dashed line.
paths -- draw dashed lines joining list of points.
vel_arrows -- draw velocity arrow on ball object.
cart_arrows -- draw cartesian component arrows of a vector.
wavelength_to_rgb -- convert wavelength to rgb values.
"""
import math

class slider():
    """Anvil Canvas slider object.

    Create a slider between mini and maxi with indicator of given colour which can take values in steps of stepsize.
    The starting position is given by start.
    Current value is given in the value attribute.
    Default colour is blue (#318fdb). Optional colour must be given in hex string form.
    Minimum canvas height 40px for standard, 50px with indicators.

    Attributes:
    mini (float)-- minimum value of slider.
    maxi (float)-- maximum values of slider.
    stepsize (float)-- steps to move slider by.
    value (float)-- user accesible, current value of slider.
    mousedown (bool)-- is mouse pressed on slider.
    indicator (bool)-- show value under slider.
    maxmin (bool)-- show maximum and minimum values.
    base_colour (string)-- hex colour string of slider.
    enabled (bool)-- is interaction enabled.

    Methods:
    draw -- draw slider on canvas.
    map_mouse -- map canvas mouse events to slider object mouse events.
    mouse_down -- move slider to click position.
    mouse_move -- move slider with mouse if mouse down.
    mouse_up -- stop interaction when mouse up.
    mouse_leave -- stop mouse interaction when mouse leave.

    """

    default_colour = "#318fdb"
    def __init__(self, canvas, mini, maxi, stepsize, start = 0, colour = default_colour):
        """Initialize slider object.

        Parameters:
        canvas (Canvas)-- anvil canvas component to draw on.
        mini (float)-- minimum value of slider.
        maxi (float)-- maximum values of slider.
        stepsize (float)-- steps to move slider by.
        start (float)-- value to start slider at.
        colour (string)-- MUST BE HEX STRING colour of slider.
        """
        if not mini <= start <= maxi:
            raise "Start value not within range specified."
        self.mini = mini
        self.maxi = maxi
        self.stepsize = stepsize
        self.canvas = canvas

        self.cw = canvas.get_width()
        self.ch = canvas.get_height()

        self.range = maxi - mini
        #scale drawing by range of slider and canvas width
        self.scale = float(self.cw) / self.range

        self.value = start

        self.mousedown = False

        self.base_colour = colour
        self.colour = colour

        self.indicator  = True
        self.maxmin = True

        #size of grabber
        self.grabber_side =15
        self.enabled = True

        #map canvas mouse events
        self.map_mouse()
        #first draw
        self.draw()

    def draw(self):
        canvas = self.canvas
        self.cw = canvas.get_width()
        self.ch = canvas.get_height()
        #reset canvas transforms
        reset2(self.canvas, 1)
        clear_canvas(canvas, "#fff")
        #vertical placement of slider line, with top padding of 5 pixels.
        self.centre = self.ch - self.grabber_side/2 -5
        centre = self.centre
        #slider text font
        font_size = 14
        font = "{0}px sans-serif".format(int(font_size))

        #if maximum minimum labels enabled
        if self.maxmin:
            mini_str = "{}".format(repr(self.mini))
            maxi_str = "{}".format(repr(self.maxi))

            #find text widths
            mini_size = canvas.measure_text(mini_str)
            maxi_size = canvas.measure_text(maxi_str)
            #find the bigger text and store it in maxi_size
            if mini_size > maxi_size:
                mini_size, maxi_size = maxi_size, mini_size
            #set horizontal padding to maximum text size + 5
            self.horpad = maxi_size + 5
        else:
            #default side padding of 10px
            self.horpad = 10

        horpad = self.horpad
        #rescale with horizontal padding
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
        #find centre of triangle in grabber
        triangle_centre = centre - grabber_side*(1+1/math.sqrt(3))/2
        #draw triangle at value
        polygon(canvas, 3, grabber_side, (self.value - self.mini)*self.scale+ horpad, triangle_centre)
        canvas.fill_style = self.colour
        canvas.fill()
        #reset transforms
        reset2(self.canvas, 1)
        #draw square
        polygon(canvas, 4, grabber_side, (self.value - self.mini)*self.scale + horpad, centre)
        #reduce shadow if mouse pressed
        canvas.shadow_blur = 2 if self.mousedown else 5
        canvas.shadow_color = "black"
        canvas.fill_style = self.colour
        canvas.fill()
        reset2(self.canvas, 1)

        #indicator
        if self.indicator:
            value_str = "{0}".format(repr(self.value))

            canvas.font = font
            #measure text of value to centre it under grabber
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

def reset2(canvas, xu):
    """Custom canvas reset function. Scales to xu, and places origin at bottom left."""
    canvas.reset_transform()
    canvas.translate(0, canvas.get_height())
    canvas.scale(xu,-xu)

def clear_canvas(canvas, colour = "#fff"):
    """Fill canvas with colour."""
    canvas.fill_style= colour
    canvas.fill_rect(0, 0, canvas.get_width(), canvas.get_height())

def border(canvas, thickness, colour, xu=1):
    """Draw border of thickness and colour on canvas which has been scaled by xu."""
    canvas.begin_path()
    canvas.line_width = thickness/xu
    canvas.stroke_style = colour
    canvas.stroke_rect(0, 0, canvas.get_width()/xu, canvas.get_height()/xu)

def eq_triangle(canvas, side, x= 0, y= 0):
    """Draw upward equilateral triangle with bottom left corner at x, y."""

    canvas.translate(x,y)
    canvas.begin_path()
    canvas.move_to(0,0)
    canvas.line_to(float(side), 0)
    canvas.line_to(float(side)/2, math.sqrt(3))
    canvas.close_path()
    canvas.translate(-x,-y)

def circle(canvas, radius, x= 0, y= 0):
    """Draw circle of radius at x, y."""

    canvas.begin_path()
    canvas.arc(x, y, float(radius), 0, 2*math.pi)
    canvas.close_path()

def arrow(canvas, length, width, x= 0, y= 0):
    """Draw horizontal arrow of length and width starting at middle of base at x,y."""
    #move to corner
    canvas.translate(x,y+ width/2)
    canvas.begin_path()
    canvas.move_to(0,0)
    #horizontal line
    canvas.line_to(0.8*length, 0)
    #up on arrow head
    canvas.line_to(0.8*length, 1.5*width/2)
    #to tip
    canvas.line_to(length, -width/2)
    #back
    canvas.line_to(0.8*length, -3.5*width/2)
    #finish head
    canvas.line_to(0.8*length, -width)
    #back to base
    canvas.line_to(0, -width)
    canvas.close_path()
    #negate translation
    canvas.translate(-x,-y-width/2)

def polygon(canvas, sides, length, x= 0, y= 0):
    """Draw regular polygon with sides of length, at x, y."""

    canvas.translate(x,y)
    N = sides
    l = length
    #interior angle
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
    """Draw dashed line from x, y to x2, y2, each segment of length dashlength.

    Emulates "line_to" behaviour of canvas, i.e does not begin or close path.
    """
    #total length of line
    length = math.sqrt((x2-x)**2 + (y2-y)**2)
    #number of dashes.
    no = int(length/dashlength)
    if no>0:
        #x length
        dx= float(x2-x)/no
        #y  length
        dy = float(y2-y)/no
        #fraction of segment to draw (dash size)
        factor = 0.8

        canvas.move_to(x,y)

        for i in range(no):
            canvas.line_to(x+(i+factor)*dx, y+(i+factor)*dy)
            canvas.move_to(x + (i+1)*dx, y + (i+1)*dy)
    else:
        pass

def paths(canvas, paths, thickness, colour):
    """Draw dashed line of colour and thickness joining list of paths.

    Each list in paths must be a list of physics.vector3 types."""
    canvas.begin_path()
    #for each path
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
    """Draw x, y components and velocity arrow of physics.ball object."""
    #arrow_scale converts velocity values to pixels.
    #x component
    arrow(canvas, ball.vel.x*arrow_scale, 2*line_width, ball.pos.x, ball.pos.y)
    canvas.fill_style = "#333333"
    canvas.fill()

    #y component
    canvas.translate(ball.pos.x, ball.pos.y)
    canvas.rotate(math.pi/2)
    #use arrow function
    arrow(canvas, ball.vel.y*arrow_scale, 2*line_width)
    canvas.fill()
    canvas.rotate(-math.pi/2)

    #velocity vector
    canvas.rotate(ball.vel.phi())
    arrow(canvas, ball.vel.mag()*arrow_scale, 4*line_width)
    canvas.fill_style = "#49902a"
    canvas.fill()


def cart_arrows(canvas, vector, line_width, arrow_scale = 0.15, colours = {'x':"#444242",'y':"#444242",'z':"#444242"}, x= 0, y=0 ):
    """Draw cartesian components of vector (physics.vector3 type) with colours."""
    #z component
    canvas.shadow_blur = 4
    canvas.translate(x, y)
    canvas.rotate(math.pi/6 + math.pi)
    canvas.scale(10*line_width, 10*line_width)
    canvas.begin_path()
    #dashed axes
    dashed_line(canvas, 0.2, 1,0)
    canvas.line_width = 0.06
    canvas.stroke()
    canvas.scale(0.1/line_width, 0.1/line_width)
    #component arrow
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


# def btn_run_click(self):
#     #standard switching run button
#     if not self.running:
#         self.running  = True
#         self.reset = False
#         self.btn_run.text = "Pause"
#
#     else:
#         self.running = False
#         self.btn_run.text = "Run"
#
# def btn_reset_click (self):
#     #called when reset button is clicked
#     self.running = False
#     self.reset = True
#     self.btn_run.text = "Run"


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
