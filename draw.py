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
            self.txt_1.text = "{0}".format(int(self.[slider_name].value))
        def [canvas_name]_mouse_up (self, x, y, button, **event_args):
            self.[slider_name].mouse_up(x, y)
        def [canvas_name]_mouse_down (self, x, y, button, **event_args):
            self.[slider_name].mouse_down(x, y)
    """

    default_colour = "#318fdb"
    def __init__(self, canvas, mini, maxi, stepsize, start = 0, colour = default_colour):
        self.mini = mini
        self.maxi = maxi
        self.stepsize = stepsize
        self.canvas = canvas

        self.cw = canvas.get_width()
        self.ch = canvas.get_height()

        self.range = maxi - mini
        self.scale = float(self.cw) / self.range

        self.value = start

        self.mousedown = False

        self.base_colour = colour
        self.colour = colour

        self.indicator  = False
        self.maxmin = False

        self.grabber_side =15
        self.enabled = True

    def draw(self):
        canvas = self.canvas
        self.cw = canvas.get_width()
        self.ch = canvas.get_height()
        self.scale = float(self.cw) / self.range
        scale = self.scale
        reset2(self.canvas, 1)
        clear_canvas(canvas, "#fff")
        self.centre = self.ch - self.grabber_side/2 -5
        centre = self.centre

        #line
        canvas.begin_path()
        canvas.move_to(0, centre)
        canvas.line_width = 4
        canvas.line_cap = "round"
        canvas.line_to(self.cw, centre)
        canvas.shadow_blur = 0
        canvas.stroke_style = "#404040"
        canvas.stroke()

        #grabber
        grabber_side = self.grabber_side
        triangle_centre = centre - grabber_side*(1+1/math.sqrt(3))/2
        polygon(canvas, 3, grabber_side, (self.value - self.mini)*self.scale, triangle_centre)
        canvas.fill_style = self.colour
        canvas.fill()
        reset2(self.canvas, 1)
        polygon(canvas, 4, grabber_side, (self.value - self.mini)*self.scale, centre)
        canvas.shadow_blur = 2 if self.mousedown else 5
        canvas.shadow_color = "black"
        canvas.fill_style = self.colour
        canvas.fill()
        reset2(self.canvas, 1)

        #indicator
        if self.indicator:
            value_str = "{0}".format(repr(self.value))
            font_size = 14
            canvas.font = "{0}px sans-serif".format(font_size)
            text_width = canvas.measure_text(value_str)['width']

            canvas.fill_style = "#000"
            canvas.shadow_blur = 0
            height_offset = self.grabber_side*0.5*(1+math.sqrt(3)) + 1.1*font_size
            canvas.translate((self.value - self.mini)*self.scale - text_width/2, centre - height_offset)
            canvas.scale(1, -1)
            canvas.fill_text(value_str, 0, 0)
            reset2(canvas, 1)

        #maxmin labels
        if self.maxmin:
            mini_str = "{}".format(repr(self.mini))
            maxi_str = "{}".format(repr(self.maxi))

            font_size = 14
            canvas.font = "{0}px sans-serif".format(font_size)

            canvas.fill_style = "#000"
            canvas.shadow_blur = 0
            height_offset = self.grabber_side*0.5*(1+math.sqrt(3)) + 1.1*font_size
            canvas.translate(0, centre - height_offset)
            canvas.scale(1, -1)
            canvas.fill_text(mini_str, 0, 0)
            reset2(canvas, 1)

            canvas.translate(self.cw - canvas.measure_text(maxi_str)['width'], centre - height_offset)
            canvas.scale(1, -1)
            canvas.fill_text(maxi_str, 0, 0)
            reset2(canvas, 1)


    def mouse_down(self, x, y):
        if self.enabled:
            self.mousedown = True
            self.value = int((x /self.scale + self.mini)/self.stepsize)*self.stepsize
            self.draw()

    def mouse_move(self, x, y):
        y=self.ch-y
        if self.enabled:
            xcheck = abs(x - (self.value - self.mini)*self.scale) <= self.grabber_side
            ycheck = abs(self.centre - y)<=self.grabber_side
            if xcheck and ycheck:
                self.colour = "#{0:x}".format(int(self.base_colour[1:], 16)+0x202020)
            else:
                self.colour = self.base_colour

            if self.mousedown:
                self.value = int((x /self.scale + self.mini)/self.stepsize)*self.stepsize

            self.draw()

    def mouse_up(self, x, y):
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
    canvas.rotate(math.pi/6)
    canvas.scale(10*line_width, 10*line_width)
    canvas.begin_path()
    dashed_line(canvas, 0.2, 1,0)
    canvas.line_width = 0.06
    canvas.stroke()
    canvas.scale(0.1/line_width, 0.1/line_width)
    arrow(canvas, vector.z*arrow_scale, 1.5*line_width)
    canvas.fill_style = colours['z']
    canvas.fill()
    canvas.rotate(-math.pi/6)

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

def clear_canvas(canvas, colour):
    canvas.fill_style= colour
    canvas.fill_rect(0, 0, canvas.get_width(), canvas.get_height())

def border(canvas, thickness, colour, xu):
    canvas.begin_path()
    canvas.line_width = thickness/xu
    canvas.stroke_style = colour
    canvas.stroke_rect(0, 0, canvas.get_width()/xu, canvas.get_height()/xu)
