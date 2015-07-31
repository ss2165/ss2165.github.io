from anvil import *
import physics
import draw
import math

class Form1(Form1Template):
    default_colour = "#32a4dd"
    default_colour_wave = "#c63939"

    def canvas_mouse_move (self, x, y, **event_args):
        pass
        # This method is called when the mouse cursor moves over this component
        #record mouse pos
        # self.mouse.x = x/(self.xu*1.0)
        # self.mouse.y = (self.ch-y)/(self.xu*1.0)
        #
        # #change text box value based on where mouse is
        # for point in self.points:
        #     if point.mousedown:
        #         point.pos += self.mouse - point.pos
        # self.draw_all()
    def canvas_mouse_up (self, x, y, button, **event_args):
    # This method is called when a mouse button is released on this component
        for point in self.points:
            point.mousedown = False

        self.draw_all()

    def canvas_mouse_down (self, x, y, button, **event_args):
        # This method is called when a mouse button is pressed on this component
        self.mouse.x = x/(self.xu*1.0)
        self.mouse.y = (self.ch-y)/(self.xu*1.0)

        detect = False
        #if mouse is within a ball, record it
        for point in self.points:
            if (self.mouse - point.pos).mag()<point.radius:
                detect = True
                point.mousedown = True
                self.points.remove(point)
        if not detect:
            newpoint = physics.point_source(radius = 0.01, speed= 0.5, wavelength = 0.1)
            newpoint.pos = self.mouse*1.0
            self.points.append(newpoint)

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


    def btn_reset_click (self, **event_args):
        # This method is called when the button is clicked
        self.running = False
        self.reset = True
        self.btn_run.text = "Run"
        self.initalize()
        self.init_pos(self.points)

        self.draw_all()


    def draw_all(self):
        draw.reset2(self.canvas, self.xu)
        draw.clear_canvas(self.canvas, "#fff")
        for point in self.points:
            self.draw_source(point, self.canvas)
    def draw_source(self,point, canvas, colour = default_colour, wave_colour = default_colour_wave, thickness = 0.003):
        xu = self.xu
        cw = self.cw
        ch = self.ch

        #point
        draw.circle(canvas, point.radius, x= point.pos.x, y = point.pos.y)
        canvas.fill_style = colour
        canvas.fill()

        big = math.sqrt(self.cw**2 + self.ch**2)


        rad = point.wavefront
        while rad>0:
            if rad*self.xu<big:
                draw.circle(canvas, rad, x= point.pos.x, y = point.pos.y)
                canvas.stroke_style = wave_colour
                canvas.line_width = thickness
                canvas.stroke()
            rad -=point.wavelength


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
            self.draw_all()
            self.first = False

        if self.running:
            for point in self.points:
                point.move(dt)
                point.radiate(dt)
            self.draw_all()


    def init_pos(self,points):
        self.points[0].pos = physics.vector3(self.cw/(2.0*self.xu) - 0.15, self.ch/(2.0*self.xu))
        self.points[1].pos = physics.vector3(self.cw/(2.0*self.xu) + 0.15, self.ch/(2.0*self.xu))

    def initalize(self):

        self.point1 = physics.point_source(radius = 0.01, speed= 0.5, wavelength = 0.1)
        self.point2 = physics.point_source(radius = 0.01, speed= 0.5, wavelength = 0.1)
        self.points = [self.point1, self.point2]
        for point in self.points:
            point.mousedown = False

    def __init__(self):
        # This sets up a variable for every component on this form.
        # For example, if we've drawn a button called "send_button", we can
        # refer to it as self.send_button:
        self.init_components()
        self.initalize()


        self.mouse = physics.vector3(0,0)

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
