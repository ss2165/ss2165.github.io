from anvil import *
import physics
import draw
import math
import graphs

from settings import settings

class Problem():
    """Exception: Fills error box with error string"""
    def __init__(self, outbox, string, colour):
        outbox.text= string
        outbox.background = colour
        outbox.visible = True

class Form1(Form1Template):
    error_red = "rgb(207, 84, 84)"
    draw_colour = "rgb(214, 106, 72)"
    x_circle = "#336888"
    y_circle = "#D69648"
    stat_circle = "#339664"


    def canvas_mouse_move (self, x, y, **event_args):

        if self.mousedown:
            xy = self.graph.find_xy(x, y)
            self.newvalues.append(xy)
            self.canvas.line_to(x,y)
            self.canvas.stroke()


    def canvas_mouse_up (self, x, y, button, **event_args):
        self.mousedown = False
        self.canvas.close_path()
        self.all.append(self.newvalues)
        self.newvalues = []

    def canvas_mouse_leave (self, x, y,  **event_args):
        self.mousedown = False

    def canvas_mouse_down (self, x, y, button, **event_args):

        self.mousedown = True
        self.canvas.reset_transform()
        self.canvas.move_to(x,y)
        self.canvas.stroke_style = self.draw_colour
        self.canvas.line_width = self.graph.line_width
        self.canvas.begin_path()

        xy = self.graph.find_xy(x, y)
        self.newvalues.append(xy)

    def btn_clear_click (self, **event_args):
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


    def drawn_process(self):
        tolx  = 100/self.graph.xu
        toly = 100/self.graph.yu

        self.corrstats = graphs.find_stationary(self.values, tol = toly)
        self.teststats = graphs.find_stationary(self.newvalues, tol = toly)

        self.corr_x_ints = graphs.find_intersecs(self.values, tol = toly, x = True)
        self.corr_y_ints = graphs.find_intersecs(self.values, tol = tolx, y = True)

        self.test_x_ints = graphs.find_intersecs(self.newvalues, tol = toly, x = True)
        self.test_y_ints = graphs.find_intersecs(self.newvalues, tol = tolx, y = True)

        self.lbl_mark.text = ""
        numbers = True

        print self.corr_x_ints
        print "\n"*3
        print self.corr_y_ints
        print "\n"*3
        print self.corrstats
        print "\n"*3

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
                if test*corr<=0:
                    xquads = True

            for i in range(len(self.test_y_ints)):
                test = self.test_y_ints[i]
                corr = self.corr_y_ints[i]
                if test*corr<=0:
                    yquads = True

            for i in range(len(self.teststats)):
                test = self.teststats[i]
                corr = self.corrstats[i]

                if test[0]*corr[0]<=0 or test[1]*corr[1]<=0:
                    statquads = True

            if xquads or yquads or statquads:
                self.lbl_mark.background = self.error_red
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

    def btn_check_click(self, **event_args):
        tol = 100

        corr_x_ints = self.corr_x_ints
        corr_y_ints = self.corr_y_ints
        corr_x_stat = zip(*self.corrstats)[0]
        corr_y_stat = zip(*self.corrstats)[1]

        ent_x_ints = graphs.extract_vals(self.x_int_box)
        ent_y_ints = graphs.extract_vals(self.y_int_box)
        ent_x_stat = graphs.extract_vals(self.x_stat_box)
        ent_y_stat = graphs.extract_vals(self.y_stat_box)

        score = graphs.val_compare(ent_x_ints, corr_x_ints) + graphs.val_compare(ent_y_ints, corr_y_ints)
        score += graphs.val_compare(ent_x_stat, corr_x_stat) + graphs.val_compare(ent_y_stat, corr_y_stat)
        score *= 100/4


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



    def btn_submit_click(self, **event_args):
        self.grid_stat.clear()
        self.grid_x_int.clear()
        self.grid_y_int.clear()
        self.lbl_mark.background = "#fff"

        if len(self.all) > 0:
            draw.clear_canvas(self.canvas, "#fff")


            self.newvalues = graphs.gauss_blur(self.all)
            self.graph.func(self.newvalues)
            
            self.drawn_process()



            self.graph.plot(colour = "rgb(214, 106, 72)", xmarker = self.xmarker, ymarker = self.ymarker)


            self.graph.circle_points(zip(self.test_x_ints, [0]*len(self.test_x_ints)), self.x_circle)
            self.graph.circle_points(zip([0]*len(self.test_y_ints), self.test_y_ints), self.y_circle, pointoffset = len(self.test_x_ints))
            self.graph.circle_points(self.teststats, self.stat_circle, pointoffset = len(self.test_x_ints) + len(self.test_y_ints))



    # def fill_up(self):
    #     #step =2*(self.xran[1] - self.xran[0])/self.cw
    #     step = 10**round(math.log((self.xran[1] - self.xran[0])/10000, 10))
    #     x= self.xran[0] + step
    #     fx = self.correct_function(x)
    #     while self.values[-1][0] < self.xran[1]:
    #         try:
    #             self.values.append((x, self.correct_function(x)))
    #         except ZeroDivisionError:
    #             pass
    #         x += step

    def timer_tick (self, **event_args):
        canvas = self.canvas


        if self.first:
            self.cw = canvas.get_width()
            self.ch = canvas.get_height()
            cw = self.cw
            ch = self.ch

            self.graph = graphs.graph_plot(canvas, self.startvals)
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
            self.values = graphs.fill_up(self.correct_function, self.xran)
            self.first = False

        # while canvas.get_width() != self.cw:
        #     self.btn_clear_click()
        #     self.cw = canvas.get_width()




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

            self.lbl_func.text = sets.func_desc.text

            self.pass_mark = float(sets.pass_mark.text)

        else:
            self.xran = (float(sets._x_calc[0]), float(sets._x_calc[1]))
            self.xlabel = sets._xlabel
            self.ylabel = sets._ylabel

            self.xmarker = sets._xmarker
            self.ymarker = sets._ymarker

            self.set_xrange = sets._set_xrange
            self.set_yrange = sets._set_yrange

            self.lbl_func.text = sets._function_desc

            self.pass_mark = sets._pass_mark

        self.correct_function = sets.function

        self.mousedown = False

        self.dt = self.timer.interval
        self.first = True
        self.values = []
        self.newvalues = []
        self.startvals = [(-0.01,-0.01),(0.01,0.01)]
        self.all = []
