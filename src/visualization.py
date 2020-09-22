from pyqtgraph.Qt import QtGui, QtCore
import numpy as np
import pyqtgraph as pg
from gather_data import sysinfo
from scipy.interpolate import interp1d



s = sysinfo()
wait_time_ms = 100
len_data = 600
xnew = np.linspace(0, len_data, num=5*len_data, endpoint=True)
x = np.linspace(-len_data*wait_time_ms/1000, 0, num=len_data, endpoint=True)
data = np.zeros([len_data, ])
#QtGui.QApplication.setGraphicsSystem('raster')
app = QtGui.QApplication([])
#mw = QtGui.QMainWindow()
#mw.resize(800,800)

win = pg.GraphicsWindow(title="Basic plotting examples")
win.resize(1000,600)
win.setWindowTitle('pyqtgraph example: Plotting')

# Enable antialiasing for prettier plots
pg.setConfigOptions(antialias=True)

p6 = win.addPlot(title="CPU load [%]")
curve = p6.plot(pen=pg.mkPen('g', width=2))
data[-1] = s.refresh_stat()[0] * 100
p6.setLabel('bottom', "Seconds")
ptr = 0
p6.setXRange(-len_data*wait_time_ms/1000, 0, padding=0)
p6.setYRange(0, 100, padding=0)


def update():
    global curve, data, ptr, p6
    data = np.roll(data, -1)
    data[-1] = s.refresh_stat()[0] * 100
    #f2 = interp1d(x, data, kind='slinear')
    #curve.setData(xnew, f2(xnew))
    curve.setData(x, data)
    if ptr == 0:
        p6.enableAutoRange('xy', False)  ## stop auto-scaling after the first data set is plotted
    ptr += 1
timer = QtCore.QTimer()
timer.timeout.connect(update)
timer.start(wait_time_ms)


## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
