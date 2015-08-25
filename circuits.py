import physics
import draw
import math

class circuit():
    def __init__(self, canvas):
        self.canvas = canvas
        self.components = []

    def component_add(self,comp):
        if isinstance(comp, component):
            comp.canvas = self.canvas
            self.components.append(comp)
        else:
            raise "Not a component"

    def draw(self):
        canvas = self.canvas
        draw.clear_canvas(canvas)
        for comp in self.components:
            comp.draw()


            canvas.line_join = "round"
            start = comp.outpos
            if comp.output == None:
                raise "Component not connected to anything {0}".format(comp.name)
            end = comp.output.inpos

            if start != None and end != None:
                canvas.begin_path()
                canvas.move_to(start[0], start[1])

                if start[0] <= end[0]:
                    canvas.line_to(end[0], start[1])
                else:
                    canvas.line_to(start[0], end[1])

                canvas.line_to(end[0], end[1])
                comp.draw_end()

    def find_comp(self, lst, typ):
        result = []
        for comp in lst:
            if isinstance(comp, typ):
                result.append(comp)
        return result

    def update(self):
        cells = self.find_comp(self.components, cell)
        c = cells[0]
        # totR = 0
        # ne = c.output
        # while ne != c:
        #     totR += ne.R
        #     ne = ne.output
        # c.I = (c.outV - c.inV)/totR

        unsolved = True
        diff = 0
        while unsolved:
            c.I += diff*0.01
            ne = c.output
            finishV = c.outV
            while ne != c:
                ne.I = c.I
                ne.inV = ne.input.outV
                if isinstance(ne, cell):
                    ne.outV = ne.inV + ne.V
                else:
                    ne.outV = ne.inV - ne.I*ne.R
                finishV = ne.outV
                ne = ne.output

            diff = finishV - c.inV
            if abs(diff) <=1e-4:
                unsolved = False



class component():
    line_width  = 2
    scale = 1
    def __init__(self, x= 0, y= 0):
        self.canvas = None
        self.name = ""
        self.inpos = (x,y)

        self.width = 0
        self.outpos = (self.inpos[0] + self.width, self.inpos[1])

        self.rotate = 0
        self.hor_scale = 1
        self.ver_scale = 1


        self.input = None
        self.output = None

        self.I = 0.0
        self.R = 0.0
        self.inV = 0.0
        self.outV = 0.0

    def rotate(self, no):
        self.rotate = no
        cos = math.cos(self.rotate*math.pi/2)
        sin = math.sin(self.rotate*math.pi/2)
        self.outpos = (self.inpos[0] + self.width*cos, self.inpos[1] + self.width*sin)

    def hor_flip(self):
        self.hor_scale *= -1
        self.outpos = (self.inpos[0] + self.width*self.hor_scale, self.inpos[1])

    def ver_flip(self):
        self.ver_scale *= -1

    def draw_start(self):
        canvas = self.canvas
        draw.reset2(canvas, self.scale)
        canvas.translate(self.inpos[0], self.inpos[1])
        canvas.scale(self.hor_scale, self.ver_scale)
        canvas.rotate(self.rotate*math.pi/2)
        canvas.begin_path()

    def draw_end(self):
        canvas = self.canvas
        canvas.stroke_style = "#000"
        canvas.line_width = self.line_width
        canvas.stroke()
        draw.reset2(canvas, self.scale)

    def in_connect_to(self, other):
        self.input = other
        other.output = self
        self.inV = other.outV

    def out_connect_to(self, other):
        self.output = other
        other.input = self
        other.inV = self.outV

    def draw_wire(self, start, end):
        canvas = self.canvas
        canvas.line_join = "round"
        if start != None and end != None:
            canvas.begin_path()
            canvas.move_to(start[0], start[1])
            canvas.line_to(end[0], start[1])
            canvas.line_to(end[0], end[1])
            self.draw_end()

    def power(self):
        return (self.outV - self.inV)*self.I


class cell(component):
    def __init__(self, V = 0, ir  =0,  x= 0, y= 0):
        component.__init__(self, x= x, y= y)
        self.V  = float(V)
        self.inV = 0.0
        self.outV = float(V)
        self.ir = ir

        self.width = 30
        self.outpos = (self.inpos[0] + self.width, self.inpos[1])

    def draw(self):
        self.draw_start()
        canvas = self.canvas
        canvas.move_to(0,0)
        canvas.line_to(10, 0)
        canvas.move_to(10, -10)
        canvas.line_to(10, 10)
        canvas.move_to(20, -5)
        canvas.line_to(20, 5)
        canvas.move_to(20, 0)
        canvas.line_to(30, 0)
        self.draw_end()

    def update(self):
        self.inV = 0
        self.I = self.input.I
        self.input.outV = self.inV

class resistor(component):
    def __init__(self, R = 1,  x= 0, y= 0):
        component.__init__(self, x= x, y= y)
        self.R = float(R)
        self.width = 50
        self.outpos = (self.inpos[0] + self.width, self.inpos[1])


    def draw(self):
        self.draw_start()
        canvas = self.canvas
        canvas.move_to(0,0)
        canvas.line_to(10, 0)
        canvas.stroke_rect(10, -7, 30, 14)
        canvas.move_to(40, 0)
        canvas.line_to(50, 0)
        self.draw_end()

    def update(self):
        self.I = (self.outV - self.inV)/self.R

class bulb(component):
    def __init__(self, R = 1,  x= 0, y= 0):
        component.__init__(self, x= x, y= y)
        self.R = float(R)
        self.width = 40
        self.outpos = (self.inpos[0] + self.width, self.inpos[1])


    def draw(self):
        self.draw_start()
        canvas = self.canvas
        canvas.move_to(0,0)
        canvas.line_to(10, 0)
        canvas.arc(20, 0, 10, 0, 2*math.pi)
        canvas.translate(20, 0)
        canvas.rotate(math.pi/4)
        canvas.move_to(-10,0)
        canvas.line_to(10, 0)
        canvas.move_to(0,-10)
        canvas.line_to(0, 10)
        canvas.rotate(-math.pi/4)
        canvas.translate(-20, 0)
        canvas.move_to(30, 0)
        canvas.line_to(40, 0)
        self.draw_end()
        canvas.translate(self.inpos[0] + 20, self.inpos[1])
        canvas.arc(0, 0, 10 - (self.outV-self.inV)*self.I, 0, 2*math.pi)
        canvas.fill_style = "rgb(195, 238, 48)"
        canvas.fill()
        draw.reset2(canvas, self.scale)

def update_circuit(components):
    new = []
    for a in components:
        if a.input == None or a.output == None:
            raise "Not a closed circuit"
