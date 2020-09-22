from pyqtgraph.Qt import QtGui, QtCore
import numpy as np
import pyqtgraph as pg
from gather_data import sysinfo
from scipy.interpolate import interp1d

pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')

colors = [()]
p = []
curve = []
s = sysinfo()
wait_time_ms = 1000
len_data = 60
xnew = np.linspace(0, len_data, num=5*len_data, endpoint=True)
x = np.linspace(-len_data*wait_time_ms/1000, 0, num=len_data, endpoint=True)
data = np.zeros([len_data, s.cpu_core_count+1])
#QtGui.QApplication.setGraphicsSystem('raster')
app = QtGui.QApplication([])
#mw = QtGui.QMainWindow()
#mw.resize(800,800)

win = pg.GraphicsWindow(title="Basic plotting examples")
win.resize(1000,600)
win.setWindowTitle('pyqtgraph example: Plotting')

# Enable antialiasing for prettier plots
pg.setConfigOptions(antialias=True)

data[-1, :] = s.refresh_stat() * 100
counter = 0
for cpu in range(s.cpu_core_count):
    p.append(win.addPlot())
    #p[-1].setLabel('bottom', "Seconds")
    p[-1].setXRange(-len_data*wait_time_ms/1000, 0, padding=0)
    p[-1].setYRange(0, 100, padding=0)
    p[-1].enableAutoRange('xy', False)
    p[-1].showAxis('top', show=True)
    p[-1].showAxis('right', show=True)
    p[-1].axes['bottom']['item'].setStyle(showValues=False)
    p[-1].axes['top']['item'].setStyle(showValues=False)
    p[-1].axes['left']['item'].setStyle(showValues=False)
    p[-1].axes['right']['item'].setStyle(showValues=False)
    p[-1].axes['right']['item'].setGrid(100)
    p[-1].axes['top']['item'].setGrid(100)
    curve.append(p[-1].plot(pen=pg.mkPen('b', width=1), fillLevel=-0.3, brush=(50,50,200,50)))
    if counter == 3:
        win.nextRow()
        counter = 0
    else:
        counter += 1



def update():
    global curve, data, ptr, p
    data = np.roll(data, -1, axis=0)
    data[-1, :] = s.refresh_stat() * 100
    # f2 = interp1d(x, data, kind='slinear')
    # curve.setData(xnew, f2(xnew))
    for cpu in range(s.cpu_core_count):
        curve[cpu].setData(x, data[:, cpu+1])

timer = QtCore.QTimer()
timer.timeout.connect(update)
timer.start(wait_time_ms)


## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
