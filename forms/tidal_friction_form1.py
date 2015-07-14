from anvil import *
import physics
import draw
import math

class obj():
    def __init__(self, mass, radius, orbit = 0, angle =0, ang_vel= 0):
        self.angle = angle
        self.ang_vel = ang_vel
        self.orbit = orbit
        self.mass = mass
        self.radius=radius
    def move(self, dt):
        self.angle -= self.ang_vel*dt
        if self.angle >= 2*math.pi:
            self.angle -= 2*math.pi


class Form1(Form1Template):
    #moon_rad
    ladj = 0.001
    tadj = 10
    def btn_run_click (self, **event_args):
        # This method is called when the button is clicked
        if not self.running:
          if self.reset:
              self.init_objs()
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
        self.running = False
        self.reset = True
        self.btn_run.text = "Run"

        self.init_objs()

        #make parameters only editable while reset
        for box in self.param_boxes:
          box.enabled = self.reset


    def init_objs(self):
        ew = 0.0
        mw = 0.0
        et = float(self.txt_et.text)
        mt = float(self.txt_mt.text)

        if et>0:
            ew = 2.0*math.pi*self.tadj/et
        if mt >0:
            mw = 2.0*math.pi*self.tadj/mt

        self.earth = obj(1, 1, 0, 0, ew)
        self.moon = obj(0.4, 0.4, 3, math.pi/2- ((ew-mw)/10), mw)
        self.tides = obj(0, 1, 0, math.pi/2, 0)
        self.tides.ang_vel = self.moon.ang_vel

        self.marker  = obj(1, 0.2, 0.8, 0, ew)

    def timer_tick (self, **event_args):
        # This method is called Every [interval] seconds
        dt = self.dt
        canvas = self.canvas
        self.cw  = canvas.get_width()
        self.ch = canvas.get_height()
        cw= self.cw
        ch = self.ch
        xu = self.xu

        draw.clear_canvas(canvas, "#fff")
        if self.running:
            angmom = self.earth.radius**2*self.earth.ang_vel+self.moon.orbit**2*self.moon.ang_vel
            self.earth.move(self.dt)
            self.marker.move(self.dt)
            self.moon.move(self.dt)
            self.tides.move(self.dt)
            veldif = (self.earth.ang_vel - self.moon.ang_vel)
            self.moon.orbit += veldif*self.ladj*math.pow(self.moon.orbit, 1.5)*dt
            self.moon.ang_vel = (angmom- self.earth.radius**2*self.earth.ang_vel)/(self.moon.orbit**2)
            self.earth.ang_vel = (angmom - self.moon.orbit**2*self.moon.ang_vel)/(self.earth.radius**2)
            self.tides.ang_vel = self.moon.ang_vel


        if self.moon.orbit - self.moon.radius <= self.earth.radius or self.moon.orbit > math.sqrt((cw/xu)**2 + (ch/xu)**2)/2:
            self.running = False
            self.btn_run.text = "Run"

        self.draw_all()

    def draw_all(self):
        canvas = self.canvas
        self.cw  = canvas.get_width()
        self.ch = canvas.get_height()
        cw= self.cw
        ch = self.ch
        xu = self.xu

        draw.reset2(canvas, xu)
        self.draw(self.tides, "#ffd600", True)
        self.draw(self.earth, "#008cff")
        self.draw(self.moon, "#00ff94")
        canvas.begin_path()
        canvas.translate(cw/(2*xu), ch/(2*xu))
        canvas.move_to(0,0)
        canvas.rotate(self.earth.angle)
        canvas.line_to(self.earth.radius, 0)
        canvas.line_width =0.05
        canvas.stroke_style =  "#d6786b"
        canvas.stroke()
        draw.reset2(canvas, xu)

        if self.check_arrows.checked:
            #arrows
            canvas.translate(cw/(2*xu), ch/(2*xu))

            canvas.rotate(self.moon.angle)
            canvas.translate(self.moon.orbit, 0)
            canvas.rotate(math.pi/2 -(self.moon.angle-self.tides.angle))
            draw.arrow(canvas,-0.01*(self.earth.ang_vel - self.moon.ang_vel), 0.2)
            canvas.fill_style = "#d14f42"
            canvas.fill()


            draw.reset2(canvas, xu)
            canvas.translate(cw/(2*xu), ch/(2*xu))
            canvas.rotate(self.tides.angle)
            canvas.translate(1.3*self.earth.radius, 0)
            canvas.rotate(math.pi/2)
            draw.arrow(canvas,0.01*(self.earth.ang_vel - self.moon.ang_vel), 0.2)
            canvas.fill_style = "#d14f42"
            canvas.fill()
            draw.reset2(canvas, xu)



    def draw(self, obj, colour, tides = False):
        cw= self.cw
        ch = self.ch
        xu = self.xu
        canvas = self.canvas

        canvas.translate(cw/(2*xu), ch/(2*xu))

        canvas.rotate(obj.angle)
        canvas.translate(obj.orbit, 0)

        if tides:
            canvas.scale(1.3, 1)
        draw.circle(canvas, obj.radius)

        canvas.fill_style = colour
        canvas.fill()

        draw.reset2(canvas, xu)


    def __init__(self):
        # This sets up a variable for every component on this form.
        # For example, if we've drawn a button called "send_button", we can
        # refer to it as self.send_button:
        self.init_components()

        # Any code you write here will run when the form opens.
        #Uncomment as required.
        self.running= False
        self.reset = True
        self.first = True
        self.dt = self.timer.interval
        self.t = 0
        self.xu = 50

        self.param_boxes= []
        self.param_boxes.append(self.txt_et)
        self.param_boxes.append(self.txt_mt)

        self.init_objs()
