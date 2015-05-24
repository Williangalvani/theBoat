from Queue import deque
from matplotlib import pyplot as plt

class AnalogData:
    # constr

    def __init__(self, maxLen):
        self.ax = deque([0.0] * maxLen)
        self.ay = deque([0.0] * maxLen)
        self.maxLen = maxLen
        self.datas = 0

    # ring buffer
    def addToBuf(self, buf, val):
        if len(buf) < self.maxLen:
            buf.append(val)
        else:
            buf.pop()
            buf.appendleft(val)

    # add data
    def add(self, data):
        self.addToBuf(self.ax, data)
        self.datas+=1

# plot class
class AnalogPlot:
    # constr
    def __init__(self, analogData):
        # set plot to animated
        plt.ion()
        self.axline, = plt.plot(analogData.ax)
        self.ayline, = plt.plot(analogData.ay)
        plt.ylim([-360, 360])

    # update plot
    def update(self, analogData):
        self.axline.set_ydata(analogData.ax)
        self.ayline.set_ydata(analogData.ay)
        plt.draw()

