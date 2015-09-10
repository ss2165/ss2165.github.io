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

"""Anvil service module for graph plotting and function processing.

Classes:
graph_plot -- plots a given function on an Anvil canvas.
graph_form -- base class for sketcher forms
graph_sketcher_1 & graph_sketcher_2 -- emulate Anvil forms for the two forms of graph sketching app supported.

Functions:
num_string -- return a sensibly formatted string of inputed float.
find_intersecs -- find x or y intersections of inputed list of values.
find_stationary --  find maxima and minima in inputed list of values.
gauss_blur -- smooth given function.
fill_up -- generate list of values for given function.
extract_vals -- generates list of floats from list of Anvil input boxes.
val_compare -- compare list of test values to correct values, return score.
least_squares -- compute R^2 values of input values with correct function.
find_compare -- find points in list of values, and val_compare if found.
"""
import math
import draw
import physics
from anvil import*

from settings import settings

class graph_plot():
    """Plots values (list of (x,y) tuples) on Anvil canvas.

    Attributes:
    canvas (Canvas) -- canvas to plot on
    xrange (list)-- x range to plot over
    yrange (list)-- y range to plot over
    line_width (int)-- plot line width
    axes_enabled (bool) -- whether to plot axes
    gridlines_enabled (bool) -- whether to plot gridlines
    markers_enabled (bool) -- whether to plot markers
    xlabel (string) -- x axis label
    ylabel (string) -- y axis label
    xmarker (float) -- stepsize in which to draw x gridlines and markers
    ymarker (float) -- stepsize in which to draw y gridlines and markers
    """
    def __init__(self, canvas, values):
        """Read in values to be plotted and declare variables."""
        self.canvas = canvas

        self.func(values)

        self.yrange = [min(self.fx), max(self.fx)]
        self.xrange = [min(self.x), max(self.x)]
        self.line_width = 2

        self.axes_enabled = True
        self.markers_enabled = True
        self.gridlines_enabled = True
        self.axes_width = 4

        self.xlabel = ""
        self.ylabel = ""

    def func(self,values):
        """Read list of values in to x and fx attributes up to the resolution of the canvas."""
        self.x = []
        self.fx = []

        #check if there are more values than pixels, if so reduce resolution of values
        # if len(values) > self.canvas.get_width():
        #     x, y = zip(*values)
        #     try:
        #         #a value per pixel
        #         newstep =float(self.xrange[1] - self.xrange[0])/self.canvas.get_width()
        #
        #     except AttributeError:
        #         #if xrange hasn't been set yet
        #         newstep = float(max(x) - min(x) )/self.canvas.get_width()
        #     for x,y in values:
        #         if abs(x % newstep - newstep) <= newstep/5.0:
        #             self.x.append(x)
        #             self.fx.append(y)
        #     print len(values), len(self.x), self.canvas.get_width()
        # else:
        for x, y in values:
            self.x.append(x)
            self.fx.append(y)


    def transform(self):
        """Transform and scale canvas such that raw x,y values can be used for plotting"""
        canvas = self.canvas
        cw = canvas.get_width()
        ch = canvas.get_height()

        self.font_size = 14
        font_size = self.font_size
        self.font = "{0}px sans-serif".format(font_size)
        font = self.font
        canvas.font = font

        if self.xlabel != "":
            label_size = canvas.measure_text(self.xlabel)
            self.horpad = label_size + 15 + self.axes_width
        else:
            self.horpad = 10

        if self.ylabel != "":
            label_size = font_size
            self.verpad = label_size + 15 + self.axes_width
        else:
            self.verpad = 10

        horpad = self.horpad
        verpad = self.verpad

        self.xu = float(cw - 2*horpad)/(self.xrange[1]- self.xrange[0])
        self.yu = float(ch - 2*verpad)/(self.yrange[1]- self.yrange[0])
        canvas.scale(self.xu, self.yu)
        canvas.translate(-self.xrange[0] + horpad/self.xu, -self.yrange[0] + verpad/self.yu)


    def plot(self, colour = "#198dbf", xmarker = None, ymarker = None):
        """Plot the function on the canvas.

        Arguments:
        colour (string) -- colour of line to plot in
        xmarker (float) -- optional, if specified sets x marker and gridline spacing.
        ymarker (float) -- optional, if specified sets y marker and gridline spacing.
        """

        canvas = self.canvas
        x = self.x
        fx = self.fx
        cw = canvas.get_width()
        ch = canvas.get_height()
        draw.reset2(canvas, 1)

        #transform to plot mode
        self.transform()

        canvas.begin_path()
        for i in range(len(self.x)):
            #canvas can't plot values that are too big or too small
            # if abs(x[i]) < 1e-9:
            #     x[i] = 0.0
            if abs(fx[i]*self.yu) > 1e4:
                if fx[i] < 0:
                    fx[i] = -1e4/self.yu
                else:
                    fx[i] = 1e4/self.yu
            if i ==0:
                canvas.move_to(x[i], fx[i])
            # elif abs(x[i]) < 1e-5:
            #     print x[i]
            else:

                #check value is within plot range
                xcheck = self.xrange[0] <= x[i] <=self.xrange[1] and self.xrange[0] <= x[i - 1] <=self.xrange[1]
                ycheck = self.yrange[0] <= fx[i] <=self.yrange[1] and self.xrange[0] <= fx[i - 1] <=self.xrange[1]

                if xcheck and ycheck:
                    #check subsequent values are not too far apart (discontinuity)
                    xcheck2 =abs(x[i] - x[i-1]) <= 50/self.xu
                    ycheck2 = abs(fx[i] - fx[i-1]) <= 50/self.yu

                    if xcheck2 and ycheck2:
                        canvas.line_to(x[i], fx[i])
                    else:
                        canvas.move_to(x[i], fx[i])
                else:
                    canvas.move_to(x[i], fx[i])


        canvas.stroke_style = colour
        #reset for width scale to be 1
        draw.reset2(canvas, 1)
        canvas.line_width = self.line_width
        canvas.stroke()

        minus = 1

        #move to corner of plot
        canvas.translate(self.horpad, self.verpad)
        #change to dimensions of plot box
        cw -= self.horpad*2
        ch -= self.verpad*2

        if self.axes_enabled:
            #convert ranges to pixels
            xr = [self.xrange[0]*self.xu, self.xrange[1]*self.xu]
            yr = [self.yrange[0]*self.yu, self.yrange[1]*self.yu]

            yzero = -xr[0]
            xzero = -yr[0]

            #check if zero is in plot range, if not move axes ot sides of box
            if not xr[0] <= 0 <= xr[1]:
                if xr[0]>0:
                    yzero = 0
                else:
                    minus = -1
                    yzero = cw
            if not yr[0] <= 0 <= yr[1]:
                if yr[0]>0:
                    xzero = 0
                else:
                    xzero = ch
            self.xzero = xzero
            self.yzero = yzero

            #draw axes
            canvas.begin_path()
            canvas.move_to(yzero, 0)
            canvas.line_to(yzero, (yr[1]-yr[0]))
            canvas.move_to(0, xzero)
            canvas.line_to((xr[1]- xr[0]), xzero)

            canvas.stroke_style = "#444444"
            canvas.line_width = self.axes_width
            canvas.stroke()

            canvas.fill_style = "#000"

            #draw labels
            if self.xlabel != "":
                #translate to text before flipping for text rendering
                canvas.translate((xr[1]  - xr[0]) +  15, xzero- self.axes_width )
                canvas.scale(1, -1)
                canvas.fill_text(self.xlabel, 0, 0)
                draw.reset2(canvas, 1)
                canvas.translate(self.horpad, self.verpad)
            if self.ylabel != "":
                canvas.translate(yzero- canvas.measure_text(self.ylabel)/2, (yr[1]- yr[0]) + 15 )
                canvas.scale(1, -1)
                canvas.fill_text(self.ylabel, 0, 0)
            draw.reset2(canvas, 1)
            canvas.translate(self.horpad, self.verpad)


            #read in markers if provided, else do 10 markers for each axis
            if xmarker != None:
                self.xmarker = float(xmarker*self.xu)
            else:
                self.xmarker = (xr[1] - xr[0])/10

            if ymarker != None:
                self.ymarker = float(ymarker*self.yu)
            else:
                self.ymarker = (yr[1] - yr[0])/10


            #draw gridlines
            if self.gridlines_enabled:
                x = self.xmarker
                y = self.ymarker

                canvas.begin_path()
                #step in marker steps until reaching edges
                while -1 <= -x + yzero  or x + yzero <= cw+1:
                    if x + yzero <= cw+1:
                        canvas.move_to((x + yzero), ch)
                        canvas.line_to((x+ yzero), 0)
                    if -1 <= -x + yzero:
                        canvas.move_to((-x+ yzero), ch)
                        canvas.line_to((-x+ yzero), 0)
                    x += self.xmarker

                while -1 <= -y + xzero  or y + xzero <= ch+1:
                    if y + xzero <= ch+1:
                        canvas.move_to(0, (y + xzero))
                        canvas.line_to(cw, (y + xzero))
                    if  -1 <= -y + xzero:
                        canvas.move_to(0, -y + xzero)
                        canvas.line_to(cw, -y + xzero)
                    y += self.ymarker

                canvas.line_width = int(self.axes_width/4)
                canvas.stroke_style = "#969696"
                canvas.stroke()

            #draw markers
            if self.markers_enabled:
                x = 0
                y = 0
                canvas.translate(yzero, xzero)
                canvas.begin_path()
                #step in marker steps until reaching edges
                while -1 <= -x + yzero  or x + yzero <= cw+1:
                    if x + yzero <= cw+1:
                        canvas.move_to((x), 5)
                        canvas.line_to((x), - 5)
                    if -1 <= -x + yzero:
                        canvas.move_to(-(x), 5)
                        canvas.line_to(-(x), - 5)
                    font_size = self.font_size - 4
                    canvas.font = "{0}px sans-serif".format(font_size)

                    #convert pixel value to label number
                    num = (x + xr[0] + yzero)/self.xu
                    if xr[0] <= 0 <= xr[1]:
                        num += 0
                    elif xr[0] < 0:
                        num -= 2*xr[1]/self.xu

                    #print text
                    if x + yzero <= cw+1:
                        canvas.translate((x), - 2 +font_size)
                        canvas.scale(1, -1)
                        st = num_string(num)
                        canvas.fill_text(st, 0, 0)
                        canvas.scale(1,-1)
                        canvas.translate(-(x), 2 - font_size)
                    if -1 <= -x + yzero:
                        canvas.translate(-(x),  - 2 +font_size)
                        canvas.scale(1,-1)
                        st = num_string(-num)
                        canvas.fill_text(st, 0, 0)
                        canvas.scale(1,-1)
                        canvas.translate((x), 2 - font_size)

                    x += self.xmarker

                #step in marker steps until reaching edges, same as x
                while -1 <= -y + xzero  or y + xzero <= ch+1:
                    if y + xzero <= ch+1:
                        canvas.move_to(-5, (y))
                        canvas.line_to(5, (y))
                    if  -1 <= -y + xzero:
                        canvas.move_to(-5, -(y))
                        canvas.line_to(5, -(y))
                    font_size = self.font_size - 4
                    canvas.font = "{0}px sans-serif".format(font_size)

                    num = (y + yr[0] + xzero)/self.yu
                    if yr[0] <=0 <= yr[1]:
                        num +=0
                    elif yr[0] < 0:
                        num -= 2*yr[1]/self.yu

                    if y + xzero <= ch+1:
                        canvas.translate(7, (y) )
                        canvas.scale(1, -1)
                        st = num_string(num)
                        canvas.fill_text(st, 0, 0)
                        canvas.scale(1,-1)
                        canvas.translate(-7, -(y) )
                    if  -1 <= -y + xzero:
                        canvas.translate(7, -(y))
                        canvas.scale(1, -1)
                        st = num_string(-num)
                        canvas.fill_text(st, 0, 0)
                        canvas.scale(1,-1)
                        canvas.translate(-7, (y) )

                    y += self.ymarker
                canvas.line_width = int(self.axes_width/2)
                canvas.stroke_style = "#444444"
                canvas.stroke()
        draw.reset2(canvas, 1)

    def circle_points(self, points, colour, pointlabels = None, pointoffset = 0):
        """Draws circles at given list of points on the plot.

        Arguments:
        points (list) -- list of tuples to draw circles at
        colour (string) -- colour of circles
        pointlabels (list) -- optional list of strings to label circles with
        pointoffset (int) -- set which letter of alphabet to start labelling at

        """
        canvas = self.canvas

        self.transform()

        canvas.begin_path()

        for i in range(len(points)):
            #translate to point
            x,y = points[i]
            canvas.translate(x, y)

            #scale to 1x1
            canvas.scale(1/self.xu, 1/self.yu)
            canvas.move_to(self.line_width*5, 0)
            canvas.arc(0, 0, self.line_width*4, 0, 2*math.pi)
            #flip for text
            canvas.scale(1, -1)
            text = ""
            if pointlabels != None:
                text = pointlabels[i]
            else:
                #label with capital letters
                text = chr(i+65 + pointoffset)

            canvas.fill_text(text, 15, 15)
            canvas.scale(self.xu, -self.yu)
            canvas.translate(-x, -y)

        canvas.stroke_style = colour
        draw.reset2(canvas, 1)
        canvas.line_width = self.line_width*2
        canvas.stroke()

    def find_xy(self, x, y):
        """Returns corresponding (x,y) tuple on plot from x, y canvas values"""
        xnew= (x - self.horpad - self.yzero)/self.xu
        fxnew = (self.canvas.get_height() -y -self.verpad- self.xzero)/self.yu

        if self.xrange[0] <=0 <= self.xrange[1]:
            xnew +=0
        elif self.xrange[0] > 0:
            xnew += self.xrange[0]
        else:
            xnew += self.xrange[1]

        if self.yrange[0] <=0 <= self.yrange[1]:
            fxnew +=0
        elif self.yrange[0] > 0 :
            fxnew += self.yrange[0]
        else :
            fxnew += self.yrange[1]

        return (xnew, fxnew)


def num_string(n):
    """Returns formatted string of float n."""

    if n == 0:
        return "0"
    elif abs(n) < 1e-3:
        #scientific notation below 10^-3
        return "%.3e" % n
    elif abs(n)<1:
        #3dp
        return "{:.3g}".format(n)
    elif 1<=abs(n)<=100:
        #2dp under 100
        return "{:g}".format(round(n, 2))
    elif abs(n) < 1e4:
        #integer under 10^4
        return "{}".format(round(int(n), 3))
    else:
        #scientific notation above 10^4
        return "%3.3e" % n

def find_intersecs(values, tol = 1, x = False, y = False):
    """Finds x intersections in maxima in list of (x,y) tuples and returns list of found tuples.


    values (list) -- list of tuples to search.
    tol (number) -- how close values have to be to be considered continuous.
    x, y (bool) -- which axis to find intersections in.
    """
    inters = []

    add = 1
    if y:
        add = 0

    for i in range(len(values)):
        if i < len(values) -1:

            before = values[i][0+add]
            after = values[i+1][0+add]
            val = values[i][1-add]

            test = False
            if before ==0:
                test = True
            #if there is a sign change and they are sufficiently close
            elif before*after < 0 and abs(after - before) <= tol:
                test = True

            #limit to 10 intersections
            if test and len(inters) < 10:
                inters.append(val)

    return inters


def find_stationary(values, tolx=1, toly=1):
    """Finds minima in maxima in list of (x,y) tuples and returns list of found tuples.

    values (list) -- list of tuples to search.
    tol (number) -- how close values have to be to be considered continuous.
    """
    stats = []

    for i in range(len(values)):
        if i < len(values) -1 and i>1:
            x1 = values[i][0]
            x2 = values[i+1][0]
            x_2 = values[i-1][0]
            y1 = values[i][1]
            y2 = values[i+1][1]
            y_2 = values[i-1][1]

            #if sign change in gradient and sufficiently close together
            test = (y2 - y1)*(y1 - y_2) <=0  and abs(y2 - y1) <= toly  and abs(y_2 - y1) <= toly and abs(x2 - x1) <= tolx  and abs(x_2 - x1) <= tolx
            if test  and len(stats) < 10:
                stats.append(values[i])
    return stats

def gauss_blur(alls, sd = 4):
    """Takes in a list of functions (list of lists of (x,y) tuples), returns smoothed continuous list of tuples.

    alls (list) -- list of lists of tuples, each list of tuples corresponding to a section of continuous function.
    sd (int) -- optional width of gaussian.
    """


    for values in alls:
        for i in range(sd, len(values)-sd):

            xav = 0
            fav = 0
            gausstot =0
            #convolve with gaussian and update list as you go
            for j in range(-sd, sd, 1):
                gauss = math.exp(-(j/sd)**2)
                xav += values[i+j][0]*gauss
                fav += values[i+j][1]*gauss
                gausstot += gauss
            values[i] = (xav/gausstot, fav/gausstot)


    new = []

    for values in alls:
        #join functions together, removing unsmoothed points at start and end of list
        new = new + values[sd:len(values) - sd]
    return new

def fill_up(function, xran, step_mult=1):
    """Returns list of tuples of (x, y) values for function over domain xran (tuple)."""
    #stepsize nearest power of 10 to 1/10000th of range
    step = step_mult*10**math.floor(math.log((xran[1] - xran[0])/10000, 10))
    x= xran[0]
    values = []

    #x += step

    while x < xran[1]:
        try:
            values.append((x, function(x)))
        #skip singular points
        except ZeroDivisionError:
            pass
        x += step

    return values

def extract_vals(box_list):
    """Return list of floats extracted from list of input boxes."""
    vals = []
    for box in box_list:
        try:
            vals.append(float(box.text))
        except:
            pass
    return vals

def val_compare(test_list, corr_list, tol=1):
    """Return score out of one to how well test_list values match corr_list values.

    Uses square root of fractional difference.
    """
    score = 0
    for test, corr in zip(test_list, corr_list):

        gap =  abs(corr - test)
        add =  1
        if gap > 2*tol:
            add = 0
        elif gap > tol:
            add = 0.5

        score += add

    try:
        return score/len(corr_list)
    except ZeroDivisionError:
        #if list empty, zero score
        return 0

def val_compare2(test_list, corr_list):
    """Return score out of one to how well test_list values match corr_list values (exactly).

    Uses square root of fractional difference.
    """
    score = 0
    for test, corr in zip(test_list, corr_list):

        if test == corr:
            score += 1

    try:
        return score/len(corr_list)
    except ZeroDivisionError:
        #if list empty, zero score
        return 0

def least_squares(values, function):
    """Return R^2 values for least squares test of values against function"""

    unzipped = zip(*values)
    x = unzipped[0]
    fx = unzipped[1]
    av = sum(fx)/ float(len(fx))
    sumsq = 0
    sumres = 0
    for x, y in values:
        sumres += (y-function(x))**2
        sumsq += (y -av)**2

    regscore = round(1 - sumres/sumsq, 4)
    return regscore if regscore>0 else 0

def find_compare(point, values, tolx=0.1, toly=0.1):
    """Find if any point if values is close enough to point, and return val_compare score."""
    x1, y1 = point
    xfound = 0
    yfound = 0
    for x2,y2 in values:
        #10% fractional difference
        testx = abs((x2-x1)) <= tolx
        testy = abs((y2-y1)) <= toly
        if testx and testy:
            return (val_compare([x2], [x1]) + val_compare([y2], [y1]))/2
    return 0

class graph_form():
    """Base class for both graph sketcher forms.

    Methods:
    imp_settings -- read in settings from settings form.
    init_components -- initialize some shared components.
    """
    def imp_settings(self, sets):
        """Read in settings from settings from, either graphical or code."""

        #graphical
        if sets.check_graphical.checked:
            buff = (sets.x_calc0.text, sets.x_calc1.text)
            #check for no provided range
            if buff[0] == "auto" or buff[1] == "auto":
                buff= (None, None)
            else:
                buff= (float(buff[0]), float(buff[1]))

            self.xran= buff
            self.xlabel = sets.xlabel.text
            self.ylabel = sets.ylabel.text

            buff= (sets.xrange0.text, sets.xrange1.text)
            if buff[0] == "auto" or buff[1] == "auto":
                buff= [None, None]
            else:
                buff= [float(buff[0]), float(buff[1])]

            self.set_xrange = buff

            buff= (sets.yrange0.text, sets.yrange1.text)
            if buff[0] == "auto" or buff[1] == "auto":
                buff= [None, None]
            else:
                buff= [float(buff[0]), float(buff[1])]

            self.set_yrange = buff
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

            self.func_desc = sets.func_desc.text

            self.pass_mark = float(sets.pass_mark.text)

        else:
            self.xran = (float(sets._x_calc[0]), float(sets._x_calc[1]))
            self.xlabel = sets._xlabel
            self.ylabel = sets._ylabel

            self.xmarker = sets._xmarker
            self.ymarker = sets._ymarker

            self.set_xrange = sets._set_xrange
            self.set_yrange = sets._set_yrange

            self.func_desc = sets._function_desc

            self.pass_mark = sets._pass_mark

        self.correct_function = sets.function
        try:
            self.pre_plot_function = sets.pre_plot_function
        except AttributeError:
            pass

        self.special_points = sets._special_points

    def init_components(self, form):
        self.btn_submit = Button(text = "Submit")
        self.btn_submit.set_event_handler("click", self.btn_submit_click)
        form.add_component(self.btn_submit, row = "A", width_xs = 2, col_xs = 0)

        self.btn_clear = Button(text = "Clear")
        self.btn_clear.set_event_handler("click", self.btn_clear_click)
        form.add_component(self.btn_clear, row = "A", width_xs = 2, col_xs = 2)

        self.lbl_func = Label()
        form.add_component(self.lbl_func, row = "A", width_xs = 4, col_xs = 5)

        self.lbl_cord = Label()
        form.add_component(self.lbl_cord, row = "A", width_xs = 3, col_xs = 9)

        self.canvas = Canvas(height = "443")
        self.canvas.set_event_handler("mouse_down", self.canvas_mouse_down)
        self.canvas.set_event_handler("mouse_up", self.canvas_mouse_up)
        self.canvas.set_event_handler("mouse_move", self.canvas_mouse_move)
        self.canvas.set_event_handler("mouse_leave", self.canvas_mouse_leave)
        form.add_component(self.canvas, row = "B", width_xs = 12, col_xs = 0)

        self.lbl_mark  = Label(height = "96", align = "center")
        form.add_component(self.lbl_mark, row = "C", width_xs = 10, col_xs = 1)


        self.timer = Timer(interval = 0.5)
        self.timer.set_event_handler("tick", self.timer_tick)
        form.add_component(self.timer)


class graph_sketcher_1(graph_form):
    """Exact plot based graph sketcher. Subclass of graph_form.

    """
    #colour setup
    error_red = "rgb(207, 84, 84)"
    draw_colour = "rgb(214, 106, 72)"
    x_circle = "#336888"
    y_circle = "#D69648"
    stat_circle = "#339664"

    def canvas_mouse_move(self, x, y, **event_args):
        if self.first == False:
            xy = self.graph.find_xy(x, y)

            if self.mousedown:
                self.canvas.line_to(x,y)
                self.canvas.stroke()
                self.newvalues.append(xy)
            self.lbl_cord.text = "({0}, {1})".format(num_string(xy[0]), num_string(xy[1]))

    def canvas_mouse_up(self, x, y, button, **event_args):
        self.mousedown = False
        self.canvas.close_path()
        self.mousedown = False
        self.all.append(self.newvalues)
        self.newvalues = []

    def canvas_mouse_leave(self, x, y,  **event_args):
        self.mousedown = False
        self.all.append(self.newvalues)
        self.newvalues = []

    def canvas_mouse_down(self, x, y, button, **event_args):
        self.mousedown = True
        if self.submitted and button == 0:
            self.btn_clear_click()
        self.canvas.reset_transform()
        self.canvas.move_to(x,y)
        self.canvas.stroke_style = self.draw_colour
        self.canvas.line_width = self.graph.line_width
        self.canvas.begin_path()

        xy = self.graph.find_xy(x, y)
        self.newvalues.append(xy)

    def btn_clear_click(self, **event_args):
        draw.reset2(self.canvas, 1)
        draw.clear_canvas(self.canvas, "#fff")
        self.newvalues = []
        self.all = []

        self.lbl_mark.text = ""
        self.lbl_mark.background = "#fff"

        self.graph.axes_enabled = True
        if self.preplot:
            self.graph.func(self.prevalues)
            self.graph.plot(colour = "#d69134", xmarker = self.xmarker, ymarker = self.ymarker)
        else:
            self.graph.func(self.startvals)
            self.graph.plot(colour = "#fff", xmarker = self.xmarker, ymarker = self.ymarker)

        self.submitted = False

    def check(self):
        tolx  = 8/self.graph.xu
        toly = 8/self.graph.yu

        regscore = least_squares(self.newvalues, self.correct_function)
        score = 0
        check_total = 1

        corr_x_stat = []
        corr_y_stat = []
        test_x_stat = []
        test_y_stat = []
        if len(self.corrstats) > 0:
            corr_x_stat = zip(*self.corrstats)[0]
            corr_y_stat = zip(*self.corrstats)[1]
            test_x_stat = zip(*self.teststats)[0]
            test_y_stat = zip(*self.teststats)[1]

        score += val_compare(self.test_x_ints, self.corr_x_ints, tol=tolx) + val_compare(self.test_y_ints, self.corr_y_ints, tol=toly)
        score += val_compare(test_x_stat, corr_x_stat, tol=tolx) + val_compare(test_y_stat, corr_y_stat, tol=toly)
        print "regression = {}".format(regscore*100)
        print "point hits = {}".format(score*100/4.0)
        score += regscore
        if len(self.special_points)>0:
            check_total += len(self.special_points)
            for point in self.special_points:
                score += find_compare(point, self.newvalues, tolx=tolx, toly=toly)


        if len(self.corrstats)>0:
            check_total += 2
        if len(self.corr_x_ints)>0:
            check_total += 1
        if len(self.corr_y_ints)>0:
            check_total += 1
        score *= 100/check_total

        return score



    def btn_submit_click(self, **event_args):
        if len(self.all) > 0:
            self.submitted = True
            draw.clear_canvas(self.canvas, "#fff")
            if self.preplot:
                self.graph.func(self.prevalues)
                self.graph.plot(colour = "#d69134", xmarker = self.xmarker, ymarker = self.ymarker)
            self.newvalues = gauss_blur(self.all)


            self.graph.func(self.newvalues)
            self.graph.axes_enabled = True
            self.graph.plot(colour = self.draw_colour, xmarker = self.xmarker, ymarker = self.ymarker)

            tolx  = 50/self.graph.xu
            toly = 50/self.graph.yu

            self.teststats = find_stationary(self.newvalues, toly=toly, tolx=tolx)
            self.test_x_ints = find_intersecs(self.newvalues, tol = toly, x = True)
            self.test_y_ints = find_intersecs(self.newvalues, tol = tolx, y = True)

            self.lbl_mark.text = ""
            numbers = True


            if len(self.corrstats) != len(self.teststats):
                self.lbl_mark.text += "Wrong number of stationary points"
                self.lbl_mark.background = self.error_red
                self.graph.func(self.newvalues)
                self.graph.circle_points(self.teststats, self.stat_circle, pointoffset = len(self.test_x_ints) + len(self.test_y_ints))
                numbers = False

            if len(self.corr_x_ints) != len(self.test_x_ints):
                self.lbl_mark.text += "\nWrong number of x intersections"
                self.lbl_mark.background = self.error_red
                self.graph.circle_points(zip(self.test_x_ints, [0]*len(self.test_x_ints)), self.x_circle)
                numbers = False

            if len(self.corr_y_ints) != len(self.test_y_ints):
                self.lbl_mark.text += "\nWrong number of y intersections"
                self.lbl_mark.background = self.error_red
                self.graph.circle_points(zip([0]*len(self.test_y_ints), self.test_y_ints), self.y_circle, pointoffset = len(self.test_x_ints))
                numbers = False

            if numbers:
                xquads = False
                yquads = False
                statquads = False
                for i in range(len(self.test_x_ints)):
                    test = self.test_x_ints[i]
                    corr = self.corr_x_ints[i]
                    if test*corr<0:
                        xquads = True

                for i in range(len(self.test_y_ints)):
                    test = self.test_y_ints[i]
                    corr = self.corr_y_ints[i]
                    if test*corr<0:
                        yquads = True

                for i in range(len(self.teststats)):
                    test = self.teststats[i]
                    corr = self.corrstats[i]

                    if test[0]*corr[0]<0 or test[1]*corr[1]<0:
                        statquads = True

                if xquads or yquads or statquads:
                    self.lbl_mark.background = self.error_red
                    if xquads:
                        self.graph.circle_points(zip(self.test_x_ints, [0]*len(self.test_x_ints)), self.x_circle)
                        self.lbl_mark.text += "\nWrong sign for x Intersection(s)"
                    if yquads:
                        self.graph.circle_points(zip([0]*len(self.test_y_ints), self.test_y_ints), self.y_circle, pointoffset = len(self.test_x_ints))
                        self.lbl_mark.text += "\nWrong sign for y Intersection(s)"
                    if statquads:
                        self.graph.circle_points(self.teststats, self.stat_circle, pointoffset = len(self.test_x_ints) + len(self.test_y_ints))
                        self.lbl_mark.text += "\nStationary point(s) in wrong quadrant"
                else:
                    score = self.check()
                    self.lbl_mark.text = "{0}%".format(round(score))

                    self.lbl_mark.background = "#fff"

                    #TODO pass mark checking
                    if score >self.pass_mark:
                        self.lbl_mark.text += "\nWell done!"
                        self.graph.func(self.values)
                        self.graph.axes_enabled = False
                        self.graph.plot(xmarker = self.xmarker, ymarker = self.ymarker)
                    else:
                        self.lbl_mark.text += "\nScore  over {0}% to pass".format(self.pass_mark)
                    #self.graph.plot(xmarker = self.xmarker, ymarker = self.ymarker)
                    #diffd = physics.diff_5(self.values)
                    #self.graph.func(diffd)
                    #self.graph.plot(colour = "rgb(32, 167, 25)", xmarker = self.xmarker, ymarker = self.ymarker)


    def timer_tick (self, **event_args):
        canvas = self.canvas

        if self.first:
            self.values = fill_up(self.correct_function, self.xran, step_mult=100)
            self.preplot = True
            try:
                self.prevalues = fill_up(self.pre_plot_function, self.xran, step_mult=100)
                self.graph = graph_plot(canvas, self.prevalues)
            except AttributeError:
                self.preplot = False
                self.graph = graph_plot(canvas, self.startvals)

            self.graph.axes_enabled = True
            if self.set_xrange != [None, None]:
                self.graph.xrange = self.set_xrange
            if self.set_yrange != [None, None]:
                self.graph.yrange = self.set_yrange
            self.graph.xlabel = self.xlabel
            self.graph.ylabel = self.ylabel

            if self.preplot:
                self.graph.plot(colour="#d69134", xmarker = self.xmarker, ymarker = self.ymarker)
            else:
                self.graph.plot(colour="#fff", xmarker=self.xmarker, ymarker=self.ymarker)

            tolx  = 50/self.graph.xu
            toly = 50/self.graph.yu

            # self.corrstats = find_stationary(self.values, tol = toly)
            # self.corr_x_ints = find_intersecs(self.values, tol = toly, x = True)
            # self.corr_y_ints = find_intersecs(self.values, tol = tolx, y = True)

            print self.corr_x_ints
            print "\n"*3
            print self.corr_y_ints
            print "\n"*3
            print self.corrstats
            print "\n"*3
            self.first = False

    def __init__(self, form):

        self.btn_submit = Button(text = "Submit")
        self.btn_submit.set_event_handler("click", self.btn_submit_click)
        form.add_component(self.btn_submit, row = "A", width_xs = 2, col_xs = 0)

        self.btn_clear = Button(text = "Clear")
        self.btn_clear.set_event_handler("click", self.btn_clear_click)
        form.add_component(self.btn_clear, row = "A", width_xs = 2, col_xs = 2)

        self.lbl_func = Label()
        form.add_component(self.lbl_func, row = "A", width_xs = 4, col_xs = 5)

        self.lbl_cord = Label()
        form.add_component(self.lbl_cord, row = "A", width_xs = 3, col_xs = 9)

        self.canvas = Canvas(height = "443")
        self.canvas.set_event_handler("mouse_down", self.canvas_mouse_down)
        self.canvas.set_event_handler("mouse_up", self.canvas_mouse_up)
        self.canvas.set_event_handler("mouse_move", self.canvas_mouse_move)
        self.canvas.set_event_handler("mouse_leave", self.canvas_mouse_leave)
        form.add_component(self.canvas, row = "B", width_xs = 12, col_xs = 0)

        self.lbl_mark  = Label(height = "96", align = "center")
        form.add_component(self.lbl_mark, row = "C", width_xs = 10, col_xs = 1)


        self.timer = Timer(interval = 0.5)
        self.timer.set_event_handler("tick", self.timer_tick)
        form.add_component(self.timer)



        sets = settings()

        self.imp_settings(sets)
        self.lbl_func.text = self.func_desc
        self.corrstats = sets._stationaries
        self.corr_x_ints = sets._x_intcpts
        self.corr_y_ints = sets._y_intcpts
        self.mousedown = False

        self.first = True
        self.values = []
        self.newvalues = []
        self.startvals = [(-0.01,-0.01),(0.01,0.01)]
        self.all = []
        self.submitted = False

class graph_sketcher_2(graph_form):
    """Rough sketch based graph sketcher. Subclass of graph_form.

    """
    error_red = "rgb(207, 84, 84)"
    draw_colour = "rgb(214, 106, 72)"
    x_circle = "#336888"
    y_circle = "#D69648"
    stat_circle = "#339664"


    def canvas_mouse_move(self, x, y, **event_args):

        if self.mousedown:
            xy = self.graph.find_xy(x, y)
            self.newvalues.append(xy)
            self.canvas.line_to(x,y)
            self.canvas.stroke()


    def canvas_mouse_up(self, x, y, button, **event_args):
        self.mousedown = False
        self.canvas.close_path()
        self.all.append(self.newvalues)
        self.newvalues = []

    def canvas_mouse_leave(self, x, y,  **event_args):
        self.mousedown = False

    def canvas_mouse_down(self, x, y, button, **event_args):
        if self.submitted and button == 0:
            self.btn_clear_click()
        self.mousedown = True
        self.canvas.reset_transform()
        self.canvas.move_to(x,y)
        self.canvas.stroke_style = self.draw_colour
        self.canvas.line_width = self.graph.line_width
        self.canvas.begin_path()

        xy = self.graph.find_xy(x, y)
        self.newvalues.append(xy)

    def btn_clear_click(self, **event_args):
        draw.clear_canvas(self.canvas, "#fff")
        self.graph.func(self.startvals)

        self.newvalues = []
        self.all = []
        self.grid_stat.clear()
        self.grid_x_int.clear()
        self.grid_y_int.clear()
        self.lbl_mark.text = ""
        self.lbl_mark.background = "#fff"

        self.graph.plot(colour = "#fff", xmarker = self.xmarker, ymarker = self.ymarker)
        self.submitted = False


    def btn_check_click(self, **event_args):
        tol = 100

        corr_x_ints = self.corr_x_ints
        corr_y_ints = self.corr_y_ints

        corr_x_stat = []
        corr_y_stat = []
        if len(self.corrstats) > 0:
            corr_x_stat = zip(*self.corrstats)[0]
            corr_y_stat = zip(*self.corrstats)[1]

        ent_x_ints = extract_vals(self.x_int_box)
        ent_y_ints = extract_vals(self.y_int_box)
        ent_x_stat = extract_vals(self.x_stat_box)
        ent_y_stat = extract_vals(self.y_stat_box)

        score = val_compare2(ent_x_ints, corr_x_ints) + val_compare2(ent_y_ints, corr_y_ints)
        score += val_compare2(ent_x_stat, corr_x_stat) + val_compare2(ent_y_stat, corr_y_stat)

        check_total = 0
        if len(self.corrstats)>0:
            check_total += 2
        if len(corr_x_ints)>0:
            check_total += 1
        if len(corr_y_ints)>0:
            check_total += 1
        score *= 100/check_total


        self.lbl_mark.text = "{0}%".format(round(score))

        self.lbl_mark.background = "#fff"

        #TODO pass mark checking
        if score >self.pass_mark:
            self.lbl_mark.text += "\nWell done!"
        else:
            self.lbl_mark.text += "\nScore  over {0}% to pass".format(self.pass_mark)

        draw.reset2(self.canvas, 1)
        draw.clear_canvas(self.canvas)
        self.graph.plot(colour = "rgb(214, 106, 72)", xmarker = self.xmarker, ymarker = self.ymarker)

        xlabs = [x.text for x in self.x_int_box]
        ylabs = [x.text for x in self.y_int_box]
        statlabs = ["({0}, {1})".format(self.x_stat_box[i].text, self.y_stat_box[i].text) for i in range(len(self.x_stat_box))]


        self.graph.circle_points(zip(self.test_x_ints, [0]*len(self.test_x_ints)), self.x_circle, pointlabels = xlabs)
        self.graph.circle_points(zip([0]*len(self.test_y_ints), self.test_y_ints), self.y_circle, pointlabels = ylabs, pointoffset = len(xlabs))
        self.graph.circle_points(self.teststats, self.stat_circle, pointlabels = statlabs, pointoffset = len(xlabs) + len(ylabs))

    def drawn_process(self):
        tolx  = 50/self.graph.xu
        toly = 50/self.graph.yu

        self.teststats = find_stationary(self.newvalues, toly=toly, tolx=tolx)
        self.test_x_ints = find_intersecs(self.newvalues, tol=toly, x = True)
        self.test_y_ints = find_intersecs(self.newvalues, tol=tolx, y = True)

        self.lbl_mark.text = ""
        numbers = True



        if len(self.corrstats) != len(self.teststats):
            self.lbl_mark.text += "Wrong number of stationary points"
            self.lbl_mark.background = self.error_red
            numbers = False

        if len(self.corr_x_ints) != len(self.test_x_ints):
            self.lbl_mark.text += "\nWrong number of x intersections"
            self.lbl_mark.background = self.error_red
            numbers = False

        if len(self.corr_y_ints) != len(self.test_y_ints):
            self.lbl_mark.text += "\nWrong number of y intersections"
            self.lbl_mark.background = self.error_red
            numbers = False

        self.x_int_box = []
        self.y_int_box = []
        self.x_stat_box = []
        self.y_stat_box = []

        if numbers:
            xquads = False
            yquads = False
            statquads = False
            for i in range(len(self.test_x_ints)):
                test = self.test_x_ints[i]
                corr = self.corr_x_ints[i]
                if test*corr<0:
                    xquads = True

            for i in range(len(self.test_y_ints)):
                test = self.test_y_ints[i]
                corr = self.corr_y_ints[i]
                if test*corr<0:
                    yquads = True

            for i in range(len(self.teststats)):
                test = self.teststats[i]
                corr = self.corrstats[i]

                if test[0]*corr[0]<0 or test[1]*corr[1]<0:
                    statquads = True

            if xquads or yquads or statquads:
                self.lbl_mark.background = self.error_red
                if xquads:
                    self.lbl_mark.text += "\nWrong sign for x Intersection(s)"
                if yquads:
                    self.lbl_mark.text += "\nWrong sign for y Intersection(s)"
                if statquads:
                    self.lbl_mark.text += "\nStationary point(s) in wrong quadrant"

            else:
                self.btn_check.visible = True
                if len(self.test_x_ints)>0:
                    int_label = Label(text = "x Intersections", bold = True)
                    self.grid_x_int.add_component(int_label)

                    for i in range(len(self.test_x_ints)):
                        box = TextBox(placeholder = "{}".format(chr(i+65)))
                        box.set_event_handler("pressed_enter", self.btn_check_click)
                        self.x_int_box.append(box)
                        self.grid_x_int.add_component(box, row = chr(i+65))


                if len(self.test_y_ints)>0:
                    int_label = Label(text = "y Intersections", bold = True)
                    self.grid_y_int.add_component(int_label)

                    for i in range(len(self.test_y_ints)):
                        box = TextBox(placeholder = "{}".format(chr(i+65 + len(self.test_x_ints))))
                        box.set_event_handler("pressed_enter", self.btn_check_click)
                        self.y_int_box.append(box)
                        self.grid_y_int.add_component(box, row = chr(i+65))

                if len(self.teststats)>0:
                    int_label = Label(text = "Stationary points", bold = True)
                    self.grid_stat.add_component(int_label)

                    for i in range(len(self.teststats)):
                        box_x = TextBox(placeholder = "{0}: {1}".format(chr(i+65 + len(self.test_x_ints) + len(self.test_y_ints)), self.xlabel))
                        box_y = TextBox(placeholder = "{0}: {1}".format(chr(i+65+ len(self.test_x_ints) + len(self.test_y_ints)), self.ylabel))
                        box_x.set_event_handler("pressed_enter", self.btn_check_click)
                        box_y.set_event_handler("pressed_enter", self.btn_check_click)
                        self.x_stat_box.append(box_x)
                        self.y_stat_box.append(box_y)
                        self.grid_stat.add_component(box_x, row = chr(i+65),  col_xs=0, width_xs=5)
                        self.grid_stat.add_component(box_y,row = chr(i+65),  col_xs=6, width_xs=5)


    def btn_submit_click(self, **event_args):
        self.submitted = True
        self.grid_stat.clear()
        self.grid_x_int.clear()
        self.grid_y_int.clear()
        self.lbl_mark.background = "#fff"

        if len(self.all) > 0:
            draw.clear_canvas(self.canvas, "#fff")

            self.newvalues = gauss_blur(self.all)
            self.graph.func(self.newvalues)

            self.drawn_process()

            self.graph.plot(colour = "rgb(214, 106, 72)", xmarker = self.xmarker, ymarker = self.ymarker)

            self.graph.circle_points(zip(self.test_x_ints, [0]*len(self.test_x_ints)), self.x_circle)
            self.graph.circle_points(zip([0]*len(self.test_y_ints), self.test_y_ints), self.y_circle, pointoffset = len(self.test_x_ints))
            self.graph.circle_points(self.teststats, self.stat_circle, pointoffset = len(self.test_x_ints) + len(self.test_y_ints))

    def timer_tick(self, **event_args):
        canvas = self.canvas

        if self.first:
            self.graph = graph_plot(canvas, self.startvals)
            self.graph.markers_enabled = False
            if self.set_xrange != [None, None]:
                self.graph.xrange = self.set_xrange
            else:
                self.graph.xrange = [self.xran[0], self.xran[1]]
            if self.set_yrange != [None, None]:
                self.graph.yrange = self.set_yrange
            self.graph.xlabel = self.xlabel
            self.graph.ylabel = self.ylabel
            self.graph.plot(colour = "#fff", xmarker = self.xmarker, ymarker = self.ymarker)
            #self.values = fill_up(self.correct_function, self.xran)

            tolx  = 50/self.graph.xu
            toly = 50/self.graph.yu

            #self.corrstats = find_stationary(self.values, tol = toly)
            #self.corr_x_ints = find_intersecs(self.values, tol = toly, x = True)
            #self.corr_y_ints = find_intersecs(self.values, tol = tolx, y = True)

            print self.corr_x_ints
            print "\n"*3
            print self.corr_y_ints
            print "\n"*3
            print self.corrstats
            print "\n"*3

            self.first = False



    def __init__(self, form):
        self.btn_submit = Button(text = "Submit")
        self.btn_submit.set_event_handler("click", self.btn_submit_click)
        form.add_component(self.btn_submit, row = "A", width_xs = 2, col_xs = 0)

        self.btn_clear = Button(text = "Clear")
        self.btn_clear.set_event_handler("click", self.btn_clear_click)
        form.add_component(self.btn_clear, row = "A", width_xs = 2, col_xs = 2)

        self.lbl_func = Label()
        form.add_component(self.lbl_func, row = "A", width_xs = 5, col_xs = 5)

        self.canvas = Canvas(height = "443")
        self.canvas.set_event_handler("mouse_down", self.canvas_mouse_down)
        self.canvas.set_event_handler("mouse_up", self.canvas_mouse_up)
        self.canvas.set_event_handler("mouse_move", self.canvas_mouse_move)
        self.canvas.set_event_handler("mouse_leave", self.canvas_mouse_leave)
        form.add_component(self.canvas, row = "B", width_xs = 12, col_xs = 0)

        self.lbl_mark  = Label(height = "96", align = "center")
        form.add_component(self.lbl_mark, row = "C", width_xs = 10, col_xs = 1)

        self.grid_x_int = GridPanel(height = "200")
        self.grid_y_int = GridPanel(height = "200")
        self.grid_stat = GridPanel(height = "200")

        form.add_component(self.grid_x_int, row = "D", width_xs = 3, col_xs = 0)
        form.add_component(self.grid_y_int, row = "D", width_xs = 3, col_xs = 3)
        form.add_component(self.grid_stat, row = "D", width_xs = 4, col_xs = 6)

        self.btn_check = Button(text="Check", visible=False)
        self.btn_check.set_event_handler("click", self.btn_check_click)
        form.add_component(self.btn_check, row = "D", width_xs = 2, col_xs = 10)

        self.timer = Timer(interval = 0.5)
        self.timer.set_event_handler("tick", self.timer_tick)
        form.add_component(self.timer)


        sets = settings()

        self.imp_settings(sets)
        self.lbl_func.text = self.func_desc
        if hasattr(sets, '_show_mark'):
            self.lbl_mark.visible = sets._show_mark
        self.corrstats = sorted(sets._stationaries,key=lambda x: x[0])
        self.corr_x_ints = sorted(sets._x_intcpts)
        self.corr_y_ints = sorted(sets._y_intcpts)
        self.mousedown = False

        self.first = True
        self.values = []
        self.newvalues = []
        self.startvals = [(-0.01,-0.01),(0.01,0.01)]
        self.all = []
        self.submitted = False
