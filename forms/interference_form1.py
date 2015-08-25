from anvil import *
import physics
import draw
import math

class Form1(Form1Template):
    default_colour = "#32a4dd"
    default_colour_wave = "#c63939"

    def canvas_mouse_move (self, x, y, **event_args):

        # This method is called when the mouse cursor moves over this component
        #record mouse pos
        self.mouse.x = x/(self.xu*1.0)
        self.mouse.y = (self.ch-y)/(self.xu*1.0)
        #
        # #change text box value based on where mouse is
        for point in self.points:
            if point.mousedown:
                point.pos += self.mouse - point.pos
                self.draw_all()

                self.moved +=1
    def canvas_mouse_up (self, x, y, button, **event_args):
    # This method is called when a mouse button is released on this component
        self.mouse.x = x/(self.xu*1.0)
        self.mouse.y = (self.ch-y)/(self.xu*1.0)

        for point in self.points:
            point.mousedown = False

        detect = False
        #if mouse is within a ball, record it
        for point in self.points:
            if (self.mouse - point.pos).mag()<point.radius:
                detect = True
                if self.moved <=2:
                    self.points.remove(point)
        if not detect:
            newpoint = physics.point_source(radius = 0.01, speed= self.spd, wavelength =self.wav)
            newpoint.pos = self.mouse*1.0
            self.points.append(newpoint)


        self.draw_all()

    def canvas_mouse_down (self, x, y, button, **event_args):
        # This method is called when a mouse button is pressed on this component
        self.mouse.x = x/(self.xu*1.0)
        self.mouse.y = (self.ch-y)/(self.xu*1.0)

        for point in self.points:
            if (self.mouse - point.pos).mag()<point.radius:
                point.mousedown = True

        self.moved = 0
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
        #self.initalize()
        #self.init_pos(self.points)
        for point in self.points:
            point.wavefront = 0
        self.t = 0
        self.draw_all()


    def draw_all(self):
        canvas = self.canvas
        draw.reset2(self.canvas, self.xu)
        draw.clear_canvas(self.canvas, "#fff")
        self.wav = self.slid_wav.value
        # div = self.cw/(self.xu*10.0)
        # canvas.begin_path()
        # for i in range(10):
        #     canvas.move_to(i*div, 0)
        #     canvas.line_to(i*div, self.ch/(self.xu*1.0))
        #
        # canvas.line_width = 0.003
        # canvas.stroke()
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

        big = math.sqrt((self.cw/xu*1.0)**2 + (self.ch/xu*1.0)**2)
        if point.wavefront + point.wavelength >big:
            point.wavefront -= point.wavelength

        rad = point.wavefront
        while rad>0:
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
            self.slid_wav = draw.slider(self.can_slid, 0.001, 0.1, stepsize = 0.001, start = 0.01)
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
        self.points[0].pos = physics.vector3(self.cw/(2.0*self.xu) - 0.05, self.ch/(2.0*self.xu))
        self.points[1].pos = physics.vector3(self.cw/(2.0*self.xu) + 0.05, self.ch/(2.0*self.xu))

    def initalize(self):
        self.spd = 0.1
        self.wav = self.slid_wav.value
        self.point1 = physics.point_source(radius = 0.01, speed= self.spd, wavelength = self.wav)
        #self.point1.vel = physics.vector3(0.1,0)
        self.point2 = physics.point_source(radius = 0.01, speed= self.spd, wavelength = self.wav)
        self.points = [self.point1, self.point2]
        for point in self.points:
            point.mousedown = False

    def __init__(self):
        # This sets up a variable for every component on this form.
        # For example, if we've drawn a button called "send_button", we can
        # refer to it as self.send_button:
        self.init_components()

        self.mouse = physics.vector3(0,0)
        self.moved = 0

        # Any code you write here will run when the form opens.
        #Uncomment as required.
        self.running= False
        self.reset = True
        self.dt = self.timer.interval
        self.first = True
        self.points = []

        self.t = 0
        #SET SCALE (pixels per m, or unit used in code)


        #APPEND ALL PARAMETER BOXES
        self.param_boxes= []
