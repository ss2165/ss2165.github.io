import math

class slider():
    def __init__(self, min, max, steps):
        pass
    def draw(self, canvas):
        pass
    def value(self):
        pass



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
        dx= (x2-x)/no
        dy = (y2-y)/no

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
    canvas.stroke_rect(0, 0, canvas.get_width()/xu, canvas.get_height()/xu)
    canvas.line_width = thickness
    canvas.stroke_style = colour
    canvas.stroke()
