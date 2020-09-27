from pyqtgraph.Qt import QtGui, QtCore
import numpy as np
import pyqtgraph as pg
from gather_data import sysinfo


def update():
    global curve, data, ptr, p
    data = np.roll(data, -1, axis=0)
    memtotal, memoccup, swaptotal, swapfree = s.refresh_memory()
    print(memtotal / 1048576, memoccup / 1048576, swaptotal, swapfree)
    data[-1, :] = np.array([(memoccup)/memtotal, (swapfree - swapfree)/swaptotal]) * 100
    # f2 = interp1d(x, data, kind='slinear')
    # curve.setData(xnew, f2(xnew))
    print(data[-1, :])
    curve[0].setData(x, data[:, 0])
    curve[1].setData(x, data[:, 1])


colors = [()]
p = []
curve = []
wait_time_ms = 1000
len_data = 60
counter = 0

pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')
pg.setConfigOptions(antialias=True)

app = QtGui.QApplication([])
win = pg.GraphicsWindow(show=True)
# win.resize(1000, 600)
win.setWindowTitle('pyqtgraph example: Plotting')

s = sysinfo()
data = np.zeros([len_data, 2])
x = np.linspace(-len_data*wait_time_ms/1000, 0, num=len_data, endpoint=True)

memtotal, memoccup, swaptotal, swapfree = s.refresh_memory()
data[-1, :] = np.array([memoccup/memtotal, (swaptotal - swapfree)/swaptotal]) * 100
p.append(win.addPlot())
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
p[-1].setMouseEnabled(x=False, y=False)
p[-1].hideButtons()
p[-1].setMenuEnabled(False)
curve.append(p[-1].plot(pen=pg.mkPen('b', width=1),
             fillLevel=-0.3, brush=(50, 50, 200, 50)))
curve.append(p[-1].plot(pen=pg.mkPen('r', width=1),
             fillLevel=-0.3, brush=(200, 50, 50, 50)))

update()
timer = QtCore.QTimer()
timer.timeout.connect(update)
timer.start(wait_time_ms)


if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
