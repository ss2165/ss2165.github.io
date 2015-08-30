from anvil import *
import physics
import draw
import math

from settings import settings

class Form1(Form1Template):



    def canvas_mouse_move (self, x, y, **event_args):
        if self.first = False
            xy = self.graph.find_xy(x, y)

            if self.mousedown:
                self.canvas.line_to(x,y)
                self.canvas.stroke()
                self.newvalues.append(xy)
            self.lbl_cord.text = "({0}, {1})".format(graphs.num_string(xy[0]), graphs.num_string(xy[1]))

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

        xy = self.graph.find_xy(x, y)
        self.newvalues.append(xy)

    def btn_clear_click (self, **event_args):
        draw.reset2(self.canvas, 1)
        draw.clear_canvas(self.canvas, "#fff")
        self.newvalues = []
        self.all = []
        self.graph.func(self.startvals)
        self.lbl_mark.text = ""
        self.lbl_mark.background = "#fff"

        self.graph.plot(colour = "#fff", xmarker = self.xmarker, ymarker = self.ymarker)




    def check():
        tol = 100

        score = least_squares(self.newvalues, self.correct_function)
        corr_x_stat = []
        corr_y_stat = []
        test_x_stat = []
        test_y_stat = []
        if len(self.corrstats) > 0:
            corr_x_stat = zip(*self.corrstats)[0]
            corr_y_stat = zip(*self.corrstats)[1]
            test_x_stat = zip(*self.teststats)[0]
            test_y_stat = zip(*self.teststats)[1]



        score += val_compare(self.test_x_ints, self.corr_x_ints) + val_compare(self.test_y_ints, self.corr_y_ints)
        score += val_compare(test_x_stat, corr_x_stat) + val_compare(test_y_stat, corr_y_stat)

        check_total = 1
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
            draw.clear_canvas(self.canvas, "#fff")


            self.newvalues = graphs.gauss_blur(self.all)

            tolx  = 100/self.graph.xu
            toly = 100/self.graph.yu

            self.teststats = find_stationary(self.newvalues, tol = toly)
            self.test_x_ints = find_intersecs(self.newvalues, tol = toly, x = True)
            self.test_y_ints = find_intersecs(self.newvalues, tol = tolx, y = True)

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
                else:
                    mark = self.check()*100
                    self.lbl_mark.text = "{0}%".format(round(score))

                    self.lbl_mark.background = "#fff"

                    #TODO pass mark checking
                    if score >self.pass_mark:
                        self.lbl_mark.text += "\nWell done!"
                    else:
                        self.lbl_mark.text += "\nScore  over {0}% to pass".format(self.pass_mark)

                    self.graph2 = draw.graph_plot(self.canvas, self.newvalues)
                    self.graph2.axes_enabled = True
                    self.graph2.xlabel = self.xlabel
                    self.graph2.ylabel = self.ylabel
                    self.graph2.xrange = self.graph.xrange
                    self.graph2.yrange = self.graph.yrange
                    self.graph2.plot(colour = self.draw_colour, xmarker = self.xmarker, ymarker = self.ymarker)


    def fill_up(self):
        step =2*(self.xran[1] - self.xran[0])/self.cw
        x= self.xran[0] + step
        fx = self.correct_function(x)
        while self.values[-1][0] < self.xran[1]:
            self.values.append((x, self.correct_function(x)))
            x += step

    def timer_tick (self, **event_args):
        canvas = self.canvas

        if self.first:
            self.values = fill_up(self.correct_function, self.xran)
            self.graph = draw.graph_plot(canvas, self.values)
            self.graph.axes_enabled = True
            if self.set_xrange != [None, None]:
                self.graph.xrange = self.set_xrange
            if self.set_yrange != [None, None]:
                self.graph.yrange = self.set_yrange
            self.graph.xlabel = self.xlabel
            self.graph.ylabel = self.ylabel
            self.graph.plot(colour = "#fff", xmarker = self.xmarker, ymarker = self.ymarker)

            tolx  = 100/self.graph.xu
            toly = 100/self.graph.yu

            self.corrstats = find_stationary(self.values, tol = toly)
            self.corr_x_ints = find_intersecs(self.values, tol = toly, x = True)
            self.corr_y_ints = find_intersecs(self.values, tol = tolx, y = True)

            print self.corr_x_ints
            print "\n"*3
            print self.corr_y_ints
            print "\n"*3
            print self.corrstats
            print "\n"*3
            self.first = False

    def __init__(self):

        self.init_components()



        sets = settings()

        self.imp_settings(sets)
        self.lbl_func.text = self.func_desc

        self.mousedown = False

        self.first = True
        self.values = []
        self.newvalues = []
        self.startvals = [(-0.01,-0.01),(0.01,0.01)]
        self.all = []
