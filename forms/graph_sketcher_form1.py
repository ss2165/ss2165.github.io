from anvil import *
import physics
import draw
import math

from settings import settings

class Form1(Form1Template):


    def find_xy(self, x, y):
        xnew= (x - self.graph.horpad - self.graph.yzero)/self.graph.xu
        fxnew = (self.ch-y -self.graph.verpad- self.graph.xzero)/self.graph.yu

        if self.graph.xrange[0] <=0 <= self.graph.xrange[1]:
            xnew +=0
        elif self.graph.xrange[0] > 0:
            xnew += self.graph.xrange[0]
        else:
            xnew += self.graph.xrange[1]

        if self.graph.yrange[0] <=0 <= self.graph.yrange[1]:
            fxnew +=0
        elif self.graph.yrange[0] > 0 :
            fxnew += self.graph.yrange[0]
        else :
            fxnew += self.graph.yrange[1]

        return (xnew, fxnew)
    def canvas_mouse_move (self, x, y, **event_args):
        xy = self.find_xy(x, y)

        if self.mousedown:
            self.canvas.line_to(x,y)
            self.canvas.stroke()
            self.newvalues.append(xy)
        self.lbl_cord.text = "({0}, {1})".format(self.graph.num_string(xy[0]), self.graph.num_string(xy[1]))

    def canvas_mouse_up (self, x, y, button, **event_args):
        self.mousedown = False
        self.canvas.close_path()

    def canvas_mouse_leave (self, x, y,  **event_args):
        self.mousedown = False

    def canvas_mouse_down (self, x, y, button, **event_args):
        self.mousedown = True
        self.canvas.reset_transform()
        self.canvas.move_to(x,y)
        self.canvas.stroke_style = "rgb(214, 106, 72)"
        self.canvas.line_width = self.graph.line_width
        self.canvas.begin_path()

        xy = self.find_xy(x, y)
        self.newvalues.append(xy)

    def btn_clear_click (self, **event_args):
        draw.reset2(self.canvas, 1)
        draw.clear_canvas(self.canvas, "#fff")
        self.graph.plot(xmarker = self.graph.xmarker/self.graph.xu, ymarker = self.graph.ymarker/self.graph.yu, colour = "#fff")
        self.newvalues = []

    def btn_run_click (self, **event_args):
        # This method is called when the button is clicked
          #if not self.running:
        #  self.running  = True
        #  self.reset = False
        #  self.btn_run.text = "Pause"

        #else:
        #  self.running = False
        #  self.btn_run.text = "Run"
        pass


    def btn_reset_click (self, **event_args):
        # This method is called when the button is clicked
            #self.running = False
        #self.reset = True
        #self.btn_run.text = "Run"
        pass

    def check(self):
        tol = 100
        newvalues = zip(*self.newvalues)
        xnew = newvalues[0]
        fxnew = newvalues[1]
        av = sum(fxnew)/ float(len(fxnew))
        sumsq = 0
        sumres = 0
        for x, y in self.newvalues:
            sumres += (y-self.correct_function(x))**2
            sumsq += (y -av)**2

        regscore = round(1 - sumres/sumsq, 4)
        regscore = regscore if regscore>0 else 0

        corrstats = self.find_stationary(self.values)
        teststats = self.find_stationary(self.newvalues)
        print teststats
        matches = 0

        for i in range(len(corrstats)):
            if i< len(teststats):
                gap =  (corrstats[i][0] - teststats[i][0])**2 + (corrstats[i][1] - teststats[i][1])**2
                add = 1-gap*tol/(self.graph.xrange[1] - self.graph.xrange[0])
                matches += add if add>0 else 0
        # print corrstats
        print matches
        print "\n"*5

        corrints = self.find_intersecs(self.values)
        testints = self.find_intersecs(self.newvalues)
        print testints
        intermatches = 0

        for i in range(len(corrints)):
            if i< len(testints):
                gap =  (corrints[i][0] - testints[i][0])**2 + (corrints[i][1] - testints[i][1])**2
                add =  1-gap*tol/(self.graph.xrange[1] - self.graph.xrange[0])
                intermatches += add if add>0 else 0

        # print corrints
        print intermatches
        print "\n"*5

        if len(corrstats)>0 or len(corrints)>0:
            score = regscore*0.5
            if len(corrstats)>0:
                if len(corrints) >0:
                    score += 0.25*matches/len(corrstats) + 0.25*intermatches/len(corrints)
                else:
                    score +=  0.5*matches/len(corrstats)
            else:
                score +=  0.5*intermatches/len(corrints)
        else:
            score = regscore

        return score if score>0 else 0

    def find_intersecs(self, values):
        inters = []
        wid = 1
        for i in range(len(values)):
            if i < len(values) -wid:
                testfx = values[i+wid][1]*values[i][1] <=0
                testx = values[i+wid][0]*values[i][0] <=0
                if testx or testfx:
                    if testx:
                        inters.append((0.0, values[i][1]))
                    elif testfx:
                        inters.append((values[i][0],0.0))

        return inters

    def find_stationary(self, values):
        stats = []
        wid = 1
        for i in range(len(values)):
            if i < len(values) -wid and i>wid:
                test = (values[i+wid][1] - values[i][1])*(values[i][1] - values[i-wid][1]) <=0
                if test:
                    stats.append(values[i])
        return stats

    def gauss_blur(self, values):
        sd = 4
        for i in range(len(values)):
            if sd-1 < i <len(values) -sd:
                xav = 0
                fav = 0
                gausstot =0
                for j in range(-sd, sd, 1):
                    gauss = math.exp(-(j/sd)**2)
                    xav += values[i+j][0]*gauss
                    fav += values[i+j][1]*gauss
                    gausstot += gauss
                values[i] = (xav/gausstot, fav/gausstot)
        return values
    def btn_submit_click(self, **event_args):
        if len(self.newvalues) > 0:
            draw.clear_canvas(self.canvas, "#fff")

            if self.check_blur.checked:
                self.newvalues = self.gauss_blur(self.newvalues)

            mark = self.check()*100
            self.lbl_mark.text = str(repr(mark)) + "%"
            colour = "#198dbf"
            if mark >self.pass_mark:
                self.lbl_mark.text += "\nWell done!"
            else:
                colour = "#fff"
                self.lbl_mark.text += "\nScore  over {0}% to pass".format(self.pass_mark)
            self.graph.plot( xmarker = self.graph.xmarker/self.graph.xu, ymarker = self.graph.ymarker/self.graph.yu, colour = colour)

            self.graph2 = draw.graph_plot(self.canvas, self.newvalues)
            self.graph2.axes_enabled = False
            self.graph2.xlabel = self.xlabel
            self.graph2.ylabel = self.ylabel
            self.graph2.xrange = self.graph.xrange
            self.graph2.yrange = self.graph.yrange
            self.graph2.plot(colour = "rgb(214, 106, 72)", xmarker = self.graph.xmarker/self.graph.xu, ymarker = self.graph.ymarker/self.graph.yu)
    def bit_length(self, n):
        s = bin(n)       # binary representation:  bin(-37) --> '-0b100101'
        s = s.lstrip('-0b') # remove leading zeros and minus sign
        return len(s)       # len('100101') --> 6

    def power2_fill(self, values):
        N = len(values)
        power2 = 1<<self.bit_length((N-1))
        diff = power2 - N
        for i in range(0,diff*2, 2):
            halff = (values[i][1] + values[i+1][1])/2
            halfx = (values[i][0] + values[i+1][0])/2
            values.insert(i+1, (halfx, halff))

        return values

    def fill_up(self):
        step =2*(self.xran[1] - self.xran[0])/self.cw
        x= self.xran[0] + step
        fx = self.correct_function(x)
        while self.values[-1][0] < self.xran[1]:
            self.values.append((x, self.correct_function(x)))
            x += step

    def timer_tick (self, **event_args):
        canvas = self.canvas
        self.cw = canvas.get_width()
        self.ch = canvas.get_height()
        cw = self.cw
        ch = self.ch

        if self.first:
            self.fill_up()
            self.graph = draw.graph_plot(canvas, self.values)
            self.graph.axes_enabled = True
            if self.set_xrange != [None, None]:
                self.graph.xrange = self.set_xrange
            if self.set_yrange != [None, None]:
                self.graph.yrange = self.set_yrange
            self.graph.xlabel = self.xlabel
            self.graph.ylabel = self.ylabel
            self.graph.plot(colour = "#fff", xmarker = self.xmarker, ymarker = self.ymarker)
            self.first = False

    def __init__(self):
        # This sets up a variable for every component on this form.
        # For example, if we've drawn a button called "send_button", we can
        # refer to it as self.send_button:
        self.init_components()

        sets = settings()

        if sets.check_graphical.checked:
            xran = (sets.x_calc0.text, sets.x_calc1.text)
            if xran[0] == "auto" or xran[1] == "auto":
                xran = (None, None)
            else:
                xran = (float(xran[0]), float(xran[1]))
            self.xran = xran
            self.xlabel = sets.xlabel.text
            self.ylabel = sets.ylabel.text

            xran = (sets.xrange0.text, sets.xrange1.text)
            if xran[0] == "auto" or xran[1] == "auto":
                xran = [None, None]
            else:
                xran = [float(xran[0]), float(xran[1])]

            self.set_xrange = xran

            xran = (sets.yrange0.text, sets.yrange1.text)
            if xran[0] == "auto" or xran[1] == "auto":
                xran = [None, None]
            else:
                xran = [float(xran[0]), float(xran[1])]

            self.set_yrange = xran
            marker = sets.xmarker.text
            if marker == "auto":
                marker = None
            else:
                marker = float(marker)
            self.xmarker = marker


            marker = sets.ymarker.text
            if marker == "auto":
                marker = None
            else:
                marker = float(marker)
            self.ymarker = marker

            self.func_name = sets.func_name.text

            self.pass_mark = float(sets.pass_mark.text)

        else:
            self.xran = (float(sets._x_calc[0]), float(sets._x_calc[1]))
            self.xlabel = sets._xlabel
            self.ylabel = sets._ylabel

            self.xmarker = sets._xmarker
            self.ymarker = sets._ymarker

            self.set_xrange = sets._set_xrange
            self.set_yrange = sets._set_yrange

            self.function_desc = sets._function_desc

            self.pass_mark = sets._pass_mark

        self.correct_function = sets.function

        self.mousedown = False
        # Any code you write here will run when the form opens.
        #Uncomment as required.
        self.running= False
        self.reset = True
        self.dt = self.timer.interval
        self.first = True
        self.values = [(self.xran[0], self.correct_function(self.xran[0]))]
        self.newvalues = []
        self.t = 0
        #SET SCALE (pixels per m, or unit used in code)
        self.xu = 1
        self.yu = 1


        if self.lbl_func.text == "":
            self.lbl_func.text = self.function_desc

        #APPEND ALL PARAMETER BOXES
        #self.param_boxes= []
