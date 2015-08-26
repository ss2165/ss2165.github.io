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

import math
import draw

class graph_plot():

    def __init__(self, canvas, values):
        self.canvas = canvas
        self.x = []
        self.fx = []
        for value in values:
            self.x.append(value[0])
            self.fx.append(value[1])

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
        self.x = []
        self.fx = []
        for value in values:
            self.x.append(value[0])
            self.fx.append(value[1])

    def transform(self):
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

    def axes_transform(self):
        canvas = self.canvas
        cw = canvas.get_width()
        ch = canvas.get_height()


    def plot(self, colour = "#198dbf", xmarker = None, ymarker = None):
        canvas = self.canvas
        x = self.x
        fx = self.fx
        cw = canvas.get_width()
        ch = canvas.get_height()
        draw.reset2(canvas, 1)
        #draw.clear_canvas(canvas, "#fff")
        self.transform()

        canvas.begin_path()

        for i in range(len(self.x)):

            if i ==0:
                canvas.move_to(x[i], fx[i])
            xcheck = self.xrange[0] <= x[i] <=self.xrange[1]
            ycheck = self.yrange[0] <= fx[i] <=self.yrange[1]
            if xcheck and ycheck:
                xcheck2 =abs(x[i] - x[i-1]) <= 100/self.xu
                ycheck2 = abs(fx[i] - fx[i-1]) <=100/self.yu

                if xcheck2 and ycheck2:
                    canvas.line_to(x[i], fx[i])
                else:
                    canvas.move_to(x[i], fx[i])
            else:
                canvas.move_to(x[i], fx[i])


        canvas.stroke_style = colour
        draw.reset2(canvas, 1)
        canvas.line_width = self.line_width
        canvas.stroke()

        minus = 1

        canvas.translate(self.horpad, self.verpad)
        cw -= self.horpad*2
        ch -= self.verpad*2

        if self.axes_enabled:
            xr = [self.xrange[0]*self.xu, self.xrange[1]*self.xu]
            yr = [self.yrange[0]*self.yu, self.yrange[1]*self.yu]

            yzero = -xr[0]
            xzero = -yr[0]

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

            canvas.begin_path()
            canvas.move_to(yzero, 0)
            canvas.line_to(yzero, (yr[1]-yr[0]))
            canvas.move_to(0, xzero)
            canvas.line_to((xr[1]- xr[0]), xzero)

            canvas.stroke_style = "#444444"
            canvas.line_width = self.axes_width
            canvas.stroke()

            canvas.fill_style = "#000"

            if self.xlabel != "":
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


                #markers

            if xmarker != None:
                self.xmarker = float(xmarker*self.xu)
            else:
                self.xmarker = (xr[1] - xr[0])/10

            if ymarker != None:
                self.ymarker = float(ymarker*self.yu)
            else:
                self.ymarker = (yr[1] - yr[0])/10



            if self.gridlines_enabled:
                x = self.xmarker
                y = self.ymarker

                canvas.begin_path()
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

            if self.markers_enabled:
                x = 0
                y = 0
                canvas.translate(yzero, xzero)
                canvas.begin_path()
                while -1 <= -x + yzero  or x + yzero <= cw+1:
                    if x + yzero <= cw+1:
                        canvas.move_to((x), 5)
                        canvas.line_to((x), - 5)
                    if -1 <= -x + yzero:
                        canvas.move_to(-(x), 5)
                        canvas.line_to(-(x), - 5)
                    font_size = self.font_size - 4
                    canvas.font = "{0}px sans-serif".format(font_size)

                    num = (x + xr[0] + yzero)/self.xu
                    if xr[0] <=0 <= xr[1]:
                        num +=0
                    elif xr[0] < 0:
                        num -= 2*xr[1]/self.xu

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
        canvas = self.canvas

        self.transform()

        canvas.begin_path()

        for i in range(len(points)):
            x,y = points[i]
            canvas.translate(x, y)

            canvas.scale(1/self.xu, 1/self.yu)
            canvas.move_to(self.line_width*5, 0)
            canvas.arc(0, 0, self.line_width*4, 0, 2*math.pi)
            canvas.scale(1, -1)
            text = ""
            if pointlabels != None:
                text = pointlabels[i]
            else:
                text = chr(i+65 + pointoffset)

            canvas.fill_text(text, 15, 15)
            canvas.scale(self.xu, -self.yu)
            canvas.translate(-x, -y)

        canvas.stroke_style = colour
        draw.reset2(canvas, 1)
        canvas.line_width = self.line_width*2
        canvas.stroke()

    def find_xy(self, x, y):
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
    if n == 0:
        return "0"
    elif abs(n) < 1e-3:
        return "{:.3e}".format(n)
    elif abs(n)<1:
        return "{:.3g}".format(n)
    elif 1<=abs(n)<=100:
        return "{:g}".format(round(n, 2))
    elif abs(n) < 1e4:
        return "{}".format(round(int(n), 3))
    else:
        return "%3.3e" % n

def find_intersecs(values, tol = 1, x = False, y = False):
    """Finds x intersections in maxima in list of (x,y) tuples and returns list of found tuples"""
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
            elif before*after < 0 and abs(after - before) <= tol:
                test = True

            if test and len(inters) < 10:
                inters.append(val)

    return inters


def find_stationary(values, tol = 1):
    """Finds minima in maxima in list of (x,y) tuples and returns list of found tuples"""
    stats = []

    for i in range(len(values)):
        if i < len(values) -1 and i>1:
            x1 = values[i][0]
            x2 = values[i+1][0]
            x_2 = values[i-1][0]
            y1 = values[i][1]
            y2 = values[i+1][1]
            y_2 = values[i-1][1]

            test = (y2 - y1)*(y1 - y_2) <=0  and abs(y2 - y1) <= tol  and abs(y_2 - y1) <= tol and abs(x2 - x1) <= tol  and abs(x_2 - x1) <= tol
            if test  and len(stats) < 10:
                stats.append(values[i])
    return stats

def gauss_blur(alls, sd = 4):
    """Takes in a list of functions (list of lists of (x,y) tuples), returns smoothed continuous list of tuples"""


    for values in alls:
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


    new = []

    for values in alls:
        new = new + values[sd:len(values) - sd]
    return new

def fill_up(function, xran):
    step = 10**round(math.log((xran[1] - xran[0])/10000, 10))
    x= xran[0]
    fx = function(x)
    values = [(x, fx)]

    x += step

    while values[-1][0] < xran[1]:
        try:
            values.append((x, function(x)))
        except ZeroDivisionError:
            pass
        x += step

    return values

def extract_vals(box_list):
    vals = []
    for box in box_list:
        try:
            vals.append(float(box.text))
        except:
            vals.append(0)
    return vals

def val_compare(test_list, corr_list):
    score = 0
    for test, corr in zip(test_list, corr_list):

        gap =  corr - test
        add =  1 - math.sqrt(abs(gap/corr))
        if add > 1:
            add = 1
        if add < 0:
            add = 0

        score += add
    return score/len(corr_list)
