from anvil import *
import physics
import draw
import math

class Form1(Form1Template):
    default_colour = "#32a4dd"
    default_colour_wave = "#c63939"

    # def canvas_mouse_move (self, x, y, **event_args):
    #
    #     # This method is called when the mouse cursor moves over this component
    #     #record mouse pos
    #     self.mouse.x = x/(self.xu*1.0)
    #     self.mouse.y = (self.ch-y)/(self.xu*1.0)
    #     #
    #     # #change text box value based on where mouse is
    #     for point in self.points:
    #         if point.mousedown:
    #             point.pos += self.mouse - point.pos
    #             self.draw_all()
    #
    #             self.moved +=1
    # def canvas_mouse_up (self, x, y, button, **event_args):
    # # This method is called when a mouse button is released on this component
    #     self.mouse.x = x/(self.xu*1.0)
    #     self.mouse.y = (self.ch-y)/(self.xu*1.0)
    #
    #     for point in self.points:
    #         point.mousedown = False
    #
    #     detect = False
    #     #if mouse is within a ball, record it
    #     for point in self.points:
    #         if (self.mouse - point.pos).mag()<point.radius:
    #             detect = True
    #             if self.moved <=2:
    #                 self.points.remove(point)
    #     if not detect:
    #         newpoint = physics.point_source(radius = 0.01, speed= self.spd, wavelength =self.wav)
    #         newpoint.pos = self.mouse*1.0
    #         newpoint.vel  = physics.vector3(0.1, 0)
    #         self.points.append(newpoint)
    #
    #
    #     self.draw_all()
    #
    # def canvas_mouse_down (self, x, y, button, **event_args):
    #     # This method is called when a mouse button is pressed on this component
    #     self.mouse.x = x/(self.xu*1.0)
    #     self.mouse.y = (self.ch-y)/(self.xu*1.0)
    #
    #     for point in self.points:
    #         if (self.mouse - point.pos).mag()<point.radius:
    #             point.mousedown = True
    #
    #     self.moved = 0
    #     self.draw_all()


    def can_slid_mouse_move (self, x, y, **event_args):
        self.spd_slider.mouse_move(x, y)
        self.spd_slider.draw()
    def can_slid_mouse_up (self, x, y, button, **event_args):
        self.spd_slider.mouse_up(x, y)
        self.spd_slider.draw()
    def can_slid_mouse_down (self, x, y, button, **event_args):
        self.spd_slider.mouse_down(x, y)
        self.spd_slider.draw()

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
        #self.initalize()
        #self.init_pos(self.points)
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
            self.draw_all()
            self.spd_slider = draw.slider(self.can_slid, mini= 0.1, maxi = 3, stepsize = 0.1, start=0.85)
            self.spd_slider.indicator = True
            self.spd_slider.draw()
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
        self.points[0].pos = physics.vector3(self.cw/(2.0*self.xu) - 0.05, self.ch/(2.0*self.xu))
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
