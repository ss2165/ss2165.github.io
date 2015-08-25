from anvil import *
import physics
import draw
import math
import time

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


        if self.mousedown:
            xy = self.find_xy(x, y)
            self.newvalues.append(xy)
            self.canvas.line_to(x,y)
            self.canvas.stroke()

        #self.lbl_cord.text = "({0}, {1})".format(self.graph.num_string(xy[0]), self.graph.num_string(xy[1]))

    def canvas_mouse_up (self, x, y, button, **event_args):
        self.mousedown = False
        self.canvas.close_path()
        self.all.append(self.newvalues)
        self.newvalues = []

    def canvas_mouse_leave (self, x, y,  **event_args):
        self.mousedown = False

    def canvas_mouse_down (self, x, y, button, **event_args):
        if not self.started:
            self.started = True
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
        self.graph.plot(colour = "#fff", xmarker = self.xmarker, ymarker = self.ymarker)
        self.newvalues = []
        self.all = []
        self.grid_stat.clear()
        self.grid_x_int.clear()
        self.grid_y_int.clear()
        self.lbl_mark.text = ""
        self.lbl_mark.background = "#fff"
        self.started = False

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

        # corrstats = self.find_stationary_2(self.values)
        # teststats = self.find_stationary_2(self.newvalues)

        corrstats = self.find_stationary(self.values)

        teststats = self.find_stationary(self.newvalues)



        self.corr_x_ints = self.find_x_intersecs(self.values)

        self.corr_y_ints = self.find_y_intersecs(self.values)
        self.test_x_ints = self.find_x_intersecs(self.newvalues)
        self.test_y_ints = self.find_y_intersecs(self.newvalues)

        self.lbl_mark.text = ""
        numbers = True

        print self.corr_x_ints
        print "\n"*3
        print self.corr_y_ints
        print "\n"*3
        print corrstats
        print "\n"*3


        if len(corrstats) != len(teststats):
            self.lbl_mark.text += "Wrong number of stationary points"
            self.lbl_mark.background = "rgb(207, 84, 84)"
            numbers = False

        if len(self.corr_x_ints) != len(self.test_x_ints):
            self.lbl_mark.text += "\nWrong number of x intersections"
            self.lbl_mark.background = "rgb(207, 84, 84)"
            numbers = False

        if len(self.corr_y_ints) != len(self.test_y_ints):
            self.lbl_mark.text += "\nWrong number of y intersections"
            self.lbl_mark.background = "rgb(207, 84, 84)"
            numbers = False




        self.x_int_entries = []
        self.y_int_entries = []
        self.stat_entries = []
        if numbers:
            xquads = False
            yquads = False
            statquads = False
            for i in range(len(self.test_x_ints)):
                test = self.test_x_ints[i]
                corr = self.corr_x_ints[i]
                if test*corr<=0:
                    xquads = True

            for i in range(len(self.test_y_ints)):
                test = self.test_y_ints[i]
                corr = self.corr_y_ints[i]
                if test*corr<=0:
                    yquads = True

            for i in range(len(teststats)):
                test = teststats[i]
                corr = corrstats[i]

                if test[0]*corr[0]<=0 or test[1]*corr[1]<=0:
                    statquads = True

            if xquads or yquads or statquads:
                self.lbl_mark.background = "rgb(207, 84, 84)"
                if xquads:
                    self.lbl_mark.text += "\nWrong sign for x Intersection(s)"
                if yquads:
                    self.lbl_mark.text += "\nWrong sign for y Intersection(s)"
                if statquads:
                    self.lbl_mark.text += "\nStationary point(s) in wrong quadrant"


            if len(self.test_x_ints)>0:
                int_label = Label(text = "x Intersections", bold = True)
                self.grid_x_int.add_component(int_label)

                for i in range(len(self.test_x_ints)):
                    box = TextBox(placeholder = "{}".format(chr(i+65)))
                    box.set_event_handler("pressed_enter", self.btn_check_click)
                    self.x_int_entries.append(box)
                    self.grid_x_int.add_component(box, row = chr(i+65))


            if len(self.test_y_ints)>0:
                int_label = Label(text = "y Intersections", bold = True)
                self.grid_y_int.add_component(int_label)

                for i in range(len(self.test_y_ints)):
                    box = TextBox(placeholder = "{}".format(chr(i+65 + len(self.test_x_ints))))
                    box.set_event_handler("pressed_enter", self.btn_check_click)
                    self.y_int_entries.append(box)
                    self.grid_y_int.add_component(box, row = chr(i+65))

            if len(teststats)>0:
                int_label = Label(text = "Stationary points", bold = True)
                self.grid_stat.add_component(int_label)

                for i in range(len(teststats)):
                    box_x = TextBox(placeholder = "{}: x".format(chr(i+65 + len(self.test_x_ints) + len(self.test_y_ints))))
                    box_y = TextBox(placeholder = "{}: y".format(chr(i+65+ len(self.test_x_ints) + len(self.test_y_ints))))
                    box_x.set_event_handler("pressed_enter", self.btn_check_click)
                    box_y.set_event_handler("pressed_enter", self.btn_check_click)
                    self.stat_entries.append((box_x, box_y))
                    self.grid_stat.add_component(box_x, row = chr(i+65),  col_xs=0, width_xs=5)
                    self.grid_stat.add_component(box_y,row = chr(i+65),  col_xs=6, width_xs=5)
                    #self.grid_stat.add_component(Label())


        self.corrstats = corrstats
        self.teststats = teststats


        return 0



    def btn_check_click(self, **event_args):
        score = 0
        tol = 100

        corr_x_ints = self.corr_x_ints
        corr_y_ints = self.corr_y_ints
        corrstats = self.corrstats
        x_int_entries = self.x_int_entries
        y_int_entries = self.y_int_entries
        stat_entries = self.stat_entries

        for i in range(len(corr_x_ints)):
            if i< len(x_int_entries):
                try:
                    test = float(x_int_entries[i].text)
                except :
                    test = 0
                gap =  corr_x_ints[i] - test
                add =  1 - math.sqrt(abs(gap/corr_x_ints[i]))
                score += add if add>0 else 0

        for i in range(len(corr_y_ints)):
            if i< len(y_int_entries):
                try:
                    test = float(y_int_entries[i].text)
                except :
                    test = 0
                gap =  corr_y_ints[i] - test
                add =  1-math.sqrt(abs(gap/corr_y_ints[i]))
                score += add if add>0 else 0

        for i in range(len(corrstats)):
            if i< len(stat_entries):
                try:
                    test = (float(stat_entries[i][0].text), float(stat_entries[i][1].text))
                except:
                    test = (0,0)
                gapx =  corrstats[i][0] - test[0]
                gapy = corrstats[i][1] - test[1]
                add =  1- math.sqrt(abs(gapx/(corrstats[i][0]))) - math.sqrt(abs(gapy/(corrstats[i][1])))
                score += add if add>0 else 0

        score *= 100/(len(corrstats) + len(corr_y_ints) + len(corr_x_ints))

        self.lbl_mark.text = "{0}%".format(round(score))

        colour = "#198dbf"
        self.lbl_mark.background = "#fff"
        if score >self.pass_mark:
            self.lbl_mark.text += "\nWell done!"
        else:
            colour = "#fff"
            self.lbl_mark.text += "\nScore  over {0}% to pass".format(self.pass_mark)

        draw.clear_canvas(self.canvas)
        self.graph.axes_enabled = True
        self.graph.plot(colour = "rgb(214, 106, 72)", xmarker = self.xmarker, ymarker = self.ymarker)
        xlabs = [x.text for x in self.x_int_entries]
        ylabs = [x.text for x in self.y_int_entries]
        statlabs = ["({0}, {1})".format(x[0].text, x[1].text) for x in self.stat_entries]


        self.graph.circle_points(zip(self.test_x_ints, [0]*len(self.test_x_ints)), "#336888", pointlabels = xlabs)
        self.graph.circle_points(zip([0]*len(self.test_y_ints), self.test_y_ints), "D69648", pointlabels = ylabs, pointoffset = len(xlabs))
        self.graph.circle_points(self.teststats, "#339664", pointlabels = statlabs, pointoffset = len(xlabs) + len(ylabs))


    def find_x_intersecs(self, values):
        inters = []
        wid = 1
        for i in range(len(values)):
            if i < len(values) -wid:
                y1 = values[i][1]
                y2 = values[i+wid][1]
                x1 = values[i][0]

                testfx = False
                if y1 ==0:
                    testfx = True
                elif y2*y1 < 0 and abs(y2 - y1) <= 100/self.graph.yu:
                    testfx = True

                if testfx and len(inters) < 10:
                    inters.append( x1)

        return inters

    def find_y_intersecs(self, values):
        inters = []
        wid = 1
        for i in range(len(values)):
            if i < len(values) -wid:
                y1 = values[i][1]
                x1 = values[i][0]
                x2 = values[i+wid][0]

                testx = False
                if x1 ==0:
                    testx = True
                elif x2*x1 < 0 and abs(x2 - x1) <= 100/self.graph.xu:
                    testx = True

                if testx  and len(inters) < 10:
                    inters.append(y1)

        return inters

    def find_stationary(self, values):
        stats = []
        wid = 1
        for i in range(len(values)):
            if i < len(values) -wid and i>wid:
                y1 = values[i][1]
                y2 = values[i+wid][1]
                y_2 = values[i-wid][1]

                test = (y2 - y1)*(y1 - y_2) <=0  and abs(y2 - y1) <= 100/self.graph.yu  and abs(y_2 - y1) <= 100/self.graph.yu
                if test  and len(stats) < 10:
                    stats.append(values[i])
        return stats

    def diff(self, values):
        res = []
        for i in range(len(values)-1):
            x1,y1  = values[i]
            x2, y2 = values[i+1]
            if x2 != x1:
                res.append((x1, (y2-y1)/(x2-x1)))

        return res

    def gauss_blur(self, alls, sd = 4):
        self.sd = sd

        for values in alls:
            for i in range(len(values)):
                if sd-1 < i <len(values) -sd:
                    xav = 0
                    fav = 0
                    gausstot =0
                    start = -sd
                    end = sd
                    # if sd-1 > i:
                    #     start = -i
                    # elif i >len(values) -sd:
                    #     end = len(values) - i - 1

                    for j in range(start, end, 1):
                        gauss = math.exp(-(j/sd)**2)
                        xav += values[i+j][0]*gauss
                        fav += values[i+j][1]*gauss
                        gausstot += gauss
                    values[i] = (xav/gausstot, fav/gausstot)


        new = []

        for values in alls:
            new = new + values[self.sd:len(values) - self.sd]
        return new

    def find_stationary_2(self, values):
        res = []
        tol = float(self.txt_test.text)
        diffd = physics.diff_5(values)
        for i in range(len(diffd)):
            x = values[i][0]
            y = values[i][1]
            d = diffd[i][1]

            if abs(d) <= tol:
                res.append((x,y))
        return res

    def btn_submit_click(self, **event_args):
        self.grid_stat.clear()
        self.grid_x_int.clear()
        self.grid_y_int.clear()
        self.lbl_mark.background = "#fff"

        if len(self.all) > 0:
            draw.clear_canvas(self.canvas, "#fff")


            self.newvalues = self.gauss_blur(self.all)

            mark = self.check()*100
            #self.lbl_mark.text = str(repr(mark)) + "%"


            # colour = "#198dbf"
            # if mark >self.pass_mark:
            #     self.lbl_mark.text += "\nWell done!"
            # else:
            #     colour = "#fff"
            #     self.lbl_mark.text += "\nScore  over {0}% to pass".format(self.pass_mark)

            #self.graph.plot()
            self.graph.func(self.newvalues)
            #self.graph = draw.graph_plot(self.canvas, self.newvalues)
            # self.graph.axes_enabled = True
            # self.graph.markers_enabled = False
            # self.graph.xlabel = self.xlabel
            # self.graph.ylabel = self.ylabel
            # self.graph.xrange = self.graph.xrange
            # self.graph.yrange = self.graph.yrange
            self.graph.plot(colour = "rgb(214, 106, 72)", xmarker = self.xmarker, ymarker = self.ymarker)


            # diffd = self.gauss_blur([diffd],10)
            # self.graph3 = draw.graph_plot(self.canvas, diffd)
            # self.graph3.axes_enabled = False
            # self.graph3.xlabel = self.graph.xlabel
            # self.graph3.ylabel = self.graph.ylabel
            # self.graph3.xrange = self.graph.xrange
            # self.graph3.yrange = self.graph.yrange
            # #self.graph3.plot()
            #
            # diffd2 = physics.diff_5(diffd)
            # diffd2 = self.gauss_blur([diffd2],10)
            # self.graph4 = draw.graph_plot(self.canvas, diffd2)
            # self.graph4.axes_enabled = False
            # self.graph4.xlabel = self.graph.xlabel
            # self.graph4.ylabel = self.graph.ylabel
            # self.graph4.xrange = self.graph.xrange
            # self.graph4.yrange = self.graph.yrange
            #self.graph4.plot(colour = "rgb(52, 195, 96)")

            self.graph.circle_points(zip(self.test_x_ints, [0]*len(self.test_x_ints)), "#336888")
            self.graph.circle_points(zip([0]*len(self.test_y_ints), self.test_y_ints), "#D69648", pointoffset = len(self.test_x_ints))
            self.graph.circle_points(self.teststats, "#339664", pointoffset = len(self.test_x_ints) + len(self.test_y_ints))

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
        #step =2*(self.xran[1] - self.xran[0])/self.cw
        step = 10**round(math.log((self.xran[1] - self.xran[0])/10000, 10))
        print step
        x= self.xran[0] + step
        fx = self.correct_function(x)
        while self.values[-1][0] < self.xran[1]:
            try:
                self.values.append((x, self.correct_function(x)))
            except ZeroDivisionError:
                pass
            x += step

    def timer_tick (self, **event_args):
        canvas = self.canvas


        if self.first:
            self.cw = canvas.get_width()
            self.ch = canvas.get_height()
            cw = self.cw
            ch = self.ch
            self.fill_up()
            self.graph = draw.graph_plot(canvas, self.values)
            self.graph.markers_enabled = False
            if self.set_xrange != [None, None]:
                self.graph.xrange = self.set_xrange
            if self.set_yrange != [None, None]:
                self.graph.yrange = self.set_yrange
            self.graph.xlabel = self.xlabel
            self.graph.ylabel = self.ylabel
            self.graph.plot(colour = "#fff", xmarker = self.xmarker, ymarker = self.ymarker)
            self.first = False

        while canvas.get_width() != self.cw:
            self.btn_clear_click()
            self.cw = canvas.get_width()
            time.sleep(0.5)




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
        self.all = []
        self.t = 0
        #SET SCALE (pixels per m, or unit used in code)
        self.xu = 1
        self.yu = 1

        self.started = False

        if self.lbl_func.text == "":
            self.lbl_func.text = self.function_desc

        #APPEND ALL PARAMETER BOXES
        #self.param_boxes= []
