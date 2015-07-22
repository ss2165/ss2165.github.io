from anvil import *
import physics
import draw
import math

class Form1(Form1Template):
  #set maximum radius of balls in m
  bigrad = 0.05
  #standard width of lines in metres
  linewidth = 0.003
  border = 5 #doesn't scale
  arrow_scale = 0.15

  def can_lab_mouse_move (self, x, y, **event_args):
    # This method is called when the mouse cursor moves over this component
    #record mouse pos
    self.mouse.x = x/self.xu
    self.mouse.y = (self.ch-y)/self.xu

    #change text box value based on where mouse is
    if self.mousedown[4]:
        x = ((self.mouse - self.balls[0].pos).x)/self.arrow_scale
        y = ((self.mouse - self.balls[0].pos).y)/self.arrow_scale
        self.txt_xsp_1.text = "%.2f" % x
        self.txt_ysp_1.text = "%.2f" % y
    elif self.mousedown[5]:
        x = ((self.mouse - self.balls[1].pos).x)/self.arrow_scale
        y = ((self.mouse - self.balls[1].pos).y)/self.arrow_scale
        self.txt_xsp_2.text = "%.2f" % x
        self.txt_ysp_2.text = "%.2f" % y
    elif self.mousedown[0] or self.mousedown[2]:
        self.txt_x_1.text = "%.2f" % self.mouse.x
        self.txt_y_1.text = "%.2f" % self.mouse.y
    elif self.mousedown[1] or self.mousedown[3]:
        self.txt_x_2.text = "%.2f" % self.mouse.x
        self.txt_y_2.text = "%.2f" % self.mouse.y


  def can_lab_mouse_up (self, x, y, button, **event_args):
    # This method is called when a mouse button is released on this component
    self.mousedown = [False, False, False, False, False, False]

  def can_lab_mouse_down (self, x, y, button, **event_args):
    # This method is called when a mouse button is pressed on this component
    self.mouse.x = x/self.xu
    self.mouse.y = (self.ch-y)/self.xu
    #if mouse is within a ball, record it
    for i in range(4):
        if (self.balls[i].pos - self.mouse).mag() <=self.balls[i].radius:
            self.mousedown[i] = True
    #arrow detect
    for i in range(2):
        if (0.9*self.arrow_scale*self.balls[i].vel + self.balls[i].pos - self.mouse).mag()<= self.bigrad/3 and self.check_vel.checked:
            self.mousedown[i+4] = True


  def txt_change (self, **event_args):
    # This method is called when the text in this text box is edited
    #reinitialize balls everytime parameters are changed
    self.init_balls()


  def btn_velreset_click (self, **event_args):
      if self.reset:
          self.reset = False
          for i in range(4):
              self.param_boxes[i+2].text = "0"
              self.balls[i].vel = physics.vector3(0,0)
          self.reset = True

  def btn_reset_click (self, **event_args):
      #called when reset button is clicked
      self.running = False
      self.reset = True
      self.btn_run.text = "Run"
      #reset balls
      self.init_balls()
      self.init_balls_pos()

      self.starts = []
      self.collides = []
      self.ends = []
      self.collided = False

      #make parameters only editable while reset
      for box in self.param_boxes:
        box.enabled = self.reset

  def btn_run_click (self, **event_args):
    # This method is called when the run button is clicked
    if not self.running:

      self.first_run = False
      self.reset = False
      self.btn_run.text = "Pause"

      #starts = []
      for ball in self.balls:
          self.starts.append(1.0*ball.pos)
      self.ends = []

      self.running  = True

    else:

      self.btn_run.text = "Run"
      for ball in self.balls:
          self.ends.append(1.0*ball.pos)
      self.running = False

    #disable boxes when running
    for box in self.param_boxes:
      box.enabled = self.reset

  def txt_zoom_change (self, **event_args):
    # This method is called when the text in this text box is edited
    if self.reset:
        scale = float(self.txt_zoom.text)
        if 0.1<=scale<=4 :
            self.oldxu  = 1.0*self.xu
            self.newxu = self.cw/(self.bigrad*2*10)*scale
            self.zoom = True

        #self.init_balls_pos()

  def timer_1_tick (self, **event_args):
    # This method is called Every [interval] seconds
    self.dt = self.timer_1.interval
    dt = self.dt
    self.cw = self.can_lab.get_width()
    self.ch = self.can_lab.get_height()


    #initalize balls at first iteration
    if self.first:
      #pixels per m, based on large ball diameter, canvas 10 ball widths
      self.xu  = self.cw/(self.bigrad*2*10)
      self.balls = []
      for i in range(0,4):
          x = physics.ball(1, self.bigrad)
          self.balls.append(x)

      #self.init_balls(self.can_lab)
      self.init_balls()
      self.init_balls_pos()
      self.first = False

    #draw everything
    self.draw_all()

    if self.reset:
        self.init_balls()

    if self.running:
        for ball in self.balls:
            ball.move(dt)
        self.check(self.balls[0], self.balls[1], True)
        self.check(self.balls[2], self.balls[3], False)

    KElab = 0.5 *(self.balls[0].mass*self.balls[0].vel.mag()**2 + self.balls[1].mass*self.balls[1].vel.mag()**2)
    MOlab = self.balls[0].momentum() + self.balls[1].momentum()

    KEzmf = 0.5 *(self.balls[2].mass*self.balls[2].vel.mag()**2 + self.balls[3].mass*self.balls[3].vel.mag()**2)
    MOzmf = self.balls[2].momentum() + self.balls[3].momentum()

    zmfvel = self.balls[0].zmf_vel(self.balls[1])

    self.lbl_kelab.text = "Total KE = {0}J".format(repr(round(KElab, 3)))
    self.lbl_kezmf.text = "Total KE = {0}J".format(repr(round(KEzmf, 3)))

    self.lbl_molab.text = "Total Momentum = ({0}, {1}) kgms-1".format(repr(round(MOlab.x, 3)), repr(round(MOlab.y, 3)))
    self.lbl_mozmf.text = "Total Momentum = ({0}, {1}) kgms^-1".format(repr(round(MOzmf.x, 3)), repr(round(MOzmf.y, 3)))

    self.lbl_zmfvel.text = "v = ({0}, {1}) ms^-1".format(repr(round(zmfvel.x, 3)), repr(round(zmfvel.y, 3)))

    self.lbl_box.text = "(Box: {0}m x {1}m)".format(repr(round(self.cw/self.xu, 3)), repr(round(self.ch/self.xu, 3)))

    self.lbl_vx_1.text = repr(round(self.balls[0].vel.x,3))
    self.lbl_vy_1.text = repr(round(self.balls[0].vel.y,3))
    self.lbl_vx_2.text = repr(round(self.balls[1].vel.x,3))
    self.lbl_vy_2.text = repr(round(self.balls[1].vel.y,3))

    if self.zoom:
        self.xu += (self.newxu-self.oldxu)/20
        self.init_balls_pos()
        if -0.05 <=(self.xu - self.newxu) <= 0.05:
            self.zoom = False



  def draw_dashes(self, canvas, i, colour):
      canvas.begin_path()
      if self.collided:
          draw.dashed_line(canvas, 0.02, self.collides[i].x, self.collides[i].y, self.starts[i].x,self.starts[i].y)
          draw.dashed_line(canvas, 0.02, self.ends[i].x, self.ends[i].y, self.collides[i].x,self.collides[i].y)
      else:
          draw.dashed_line(canvas, 0.02, self.ends[i].x, self.ends[i].y, self.starts[i].x,self.starts[i].y)
      #canvas.line_to(self.ends[i].x, self.ends[i].y)
      canvas.line_width = self.linewidth
      canvas.stroke_style = colour
      canvas.stroke()


  def draw_all(self):
      #draw lab frame
      self.draw_frame(self.can_lab, self.balls[:2])
      #draw zmf frame
      self.draw_frame(self.can_zmf, self.balls[2:])
      if not self.running and not self.first_run and not self.reset and self.check_paths.checked:
          dashblue = "#009cff"
          dashred= "#e94545"
          self.draw_dashes(self.can_lab, 0, dashblue)
          self.draw_dashes(self.can_lab, 1, dashred)
          self.draw_dashes(self.can_zmf, 2, dashblue)
          self.draw_dashes(self.can_zmf, 3, dashred)

  def draw_frame(self, canvas, balls):
    #draws border, arrows and balls on to canvas
    cw = self.cw
    ch = self.ch
    xu= self.xu

    #reset canvas
    draw.reset2(canvas,xu)

    #clear canvas
    draw.clear_canvas(canvas, "#fff")

    #balls
    for i in range(0,2):
        if i%2 == 0:
            canvas.fill_style = "#4c7fbe"
        else:
            canvas.fill_style ="#bb2828"
        draw.circle(canvas, balls[i].radius,balls[i].pos.x, balls[i].pos.y)
        canvas.fill()

    #borders
    canvas.stroke_style = "#000"
    canvas.line_width  = self.border/xu
    canvas.stroke_rect(0,0, cw/(1.0*xu),ch/(1.0*xu))


    #arrows
    if not self.running and self.check_vel.checked:
        for ball in balls:
            #x component
            draw.arrow(canvas, ball.vel.x*self.arrow_scale, 2*self.linewidth, ball.pos.x, ball.pos.y)
            canvas.fill_style = "#333333"
            canvas.fill()

            #y component
            canvas.translate(ball.pos.x, ball.pos.y)
            canvas.rotate(math.pi/2)
            draw.arrow(canvas, ball.vel.y*self.arrow_scale, 2*self.linewidth)
            canvas.fill()
            draw.reset2(canvas,xu)

            #velocity vector
            canvas.translate(ball.pos.x, ball.pos.y)
            if ball.vel.y>0:
                canvas.rotate(ball.vel.phi())
            else:
                canvas.rotate(-ball.vel.phi())
            draw.arrow(canvas, ball.vel.mag()*self.arrow_scale, 4*self.linewidth)
            canvas.fill_style = "#49902a"
            canvas.fill()

            draw.reset2(canvas, xu)

  def check(self, ball_1, ball_2, lab):
  #check for collision and draw if detected
      if ball_1.collision_check(ball_2):
          ball_1.collide(ball_2, self.radio_elastic.selected)
          self.collides.append(1.0*ball_1.pos)
          self.collides.append(1.0*ball_2.pos)
          self.collided = True


  def radcalc(self, mass_l, mass_s, bigrad):
    #calculates radius of smaller ball
    return bigrad*math.pow(mass_s/mass_l, 0.333333333333)

  def init_balls(self):
    #fills ball parameters with box values
    bigrad = self.bigrad
    cw = self.cw
    ch = self.ch

    #initialize balls
    for i in range (0,4):
        #Relies on param_boxes order maintained!
        self.balls[i].mass = float(self.param_boxes[i%2].text)
        self.balls[i].vel.x = float(self.param_boxes[i%2+2].text)
        self.balls[i].vel.y = float(self.param_boxes[i%2+4].text)
        self.balls[i].pos.x = float(self.param_boxes[i%2+8].text)
        self.balls[i].pos.y = float(self.param_boxes[i%2+10].text)


    #adjust small ball size (bigger ball size is fixed)
    if self.balls[0].mass > self.balls[1].mass:
      self.balls[0].radius = bigrad
      self.balls[1].radius=  self.radcalc(self.balls[0].mass,self.balls[1].mass, bigrad)

    elif self.balls[0].mass< self.balls[1].mass:
      self.balls[1].radius = bigrad
      self.balls[0].radius = self.radcalc(self.balls[1].mass,self.balls[0].mass, bigrad)
    else:
      self.balls[1].radius = bigrad
      self.balls[0].radius = bigrad

    #subtract zmf velocity for zmf frame balls
    v = self.balls[0].zmf_vel(self.balls[1])
    for i in range(0,2):
        self.balls[i+2].radius  = self.balls[i].radius
        self.balls[i+2].vel = self.balls[i].vel -v

  def init_balls_pos(self):
      #returns balls to standard positions
      cw = self.cw
      ch = self.ch

      for i in range(0,4):
          self.balls[i].pos.y = ch/(2.0*self.xu)
          self.param_boxes[10].text = "%.3f" % self.balls[i].pos.y
          self.param_boxes[11].text = "%.3f" % self.balls[i].pos.y
          if i%2 ==0:
              self.balls[i].pos.x =self.balls[i].radius + self.border/self.xu
              self.param_boxes[8].text = "%.3f" % self.balls[i].pos.x
          else:
              self.balls[i].pos.x = cw/self.xu-(self.balls[i].radius+self.border/self.xu)
              self.param_boxes[9].text = "%.3f" % self.balls[i].pos.x

  def __init__(self):
    # This sets up a variable for every component on this form.
    self.init_components()
    self.running = False
    self.first  = True
    self.first_run = True
    self.reset  = True
    self.mousedown = [False, False, False, False, False, False]
    self.mouse = physics.vector3(0,0,0)
    self.collided = False
    self.zoom = False
    #list of parameter inputs
    self.param_boxes = []

    self.param_boxes.append(self.txt_mass_1)
    self.param_boxes.append(self.txt_mass_2)
    self.param_boxes.append(self.txt_xsp_1)
    self.param_boxes.append(self.txt_xsp_2)
    self.param_boxes.append(self.txt_ysp_1)
    self.param_boxes.append(self.txt_ysp_2)
    self.param_boxes.append(self.radio_elastic)
    self.param_boxes.append(self.radio_inelastic)
    self.param_boxes.append(self.txt_x_1)
    self.param_boxes.append(self.txt_x_2)
    self.param_boxes.append(self.txt_y_1)
    self.param_boxes.append(self.txt_y_2)
    self.param_boxes.append(self.btn_velreset)

    self.starts = []
    self.collides = []
    self.ends = []
