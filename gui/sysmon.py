from PyQt5 import QtWidgets, uic
import pyqtgraph as pg
import sys
import numpy as np
from pyqtgraph.Qt import QtCore, QtGui
sys.path.insert(0, '../src/')
from gather_data import sysinfo
# from sysmonitor import Ui_MainWindow


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        pg.setConfigOption('background', 'w')
        pg.setConfigOption('foreground', 'k')
        pg.setConfigOptions(antialias=True)
        uic.loadUi('sysmonitor.ui', self)

        self.len_data = 60
        self.cpu_curve = []
        self.mem_curve = []
        self.wait_time_ms = 1000
        self.s = sysinfo()
        self.meminfo = np.zeros([self.len_data, 2])
        self.cpuinfo = np.zeros([self.len_data, self.s.cpu_core_count+1])
        self.x = np.linspace(-self.len_data*self.wait_time_ms/1000, 0,
                             num=self.len_data, endpoint=True)
        self.plot_meminfo()
        self.plot_cpuinfo()
        self.headertitle = ('USER', 'PID', 'CPU [%]', 'MEM [%]', 'VSZ', 'RSS', 'TTY', 'STAT', 'START', 'TIME', 'COMMAND')
        self.tableWidget.verticalHeader().setVisible(False)
        self.tableWidget.horizontalHeader().setHighlightSections(False)
        self.update_running_processes()
        self.timer_3 = QtCore.QTimer()
        self.timer_3.timeout.connect(self.update_running_processes)
        self.timer_3.start(self.wait_time_ms)
        # self.tableWidget.setRowCount(4096)
        # self.tableWidget.setColumnCount(5)
        # self.tableWidget.setHorizontalHeaderLabels(headertitle)

    def plot_cpuinfo(self,):
        counter = 0
        p = []
        self.cpuinfo[-1, :] = self.s.refresh_stat() * 100
        for cpu in range(self.s.cpu_core_count):
            p.append(self.widget_2.addPlot())
            p[-1].setXRange(-self.len_data*self.wait_time_ms/1000, 0, padding=0)
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
            self.cpu_curve .append(p[-1].plot(pen=pg.mkPen('b', width=1),
                         fillLevel=-0.3, brush=(50, 50, 200, 50)))
            if counter == 3:
                self.widget_2.nextRow()
                counter = 0
            else:
                counter += 1

        self.update_cpuinfo()
        self.timer_2 = QtCore.QTimer()
        self.timer_2.timeout.connect(self.update_cpuinfo)
        self.timer_2.start(self.wait_time_ms)

    def plot_meminfo(self,):
        p = []
        memtotal, memoccup, swaptotal, swapfree = self.s.refresh_memory()
        self.meminfo[-1, :] = np.array([memoccup/memtotal,
                                       (swaptotal - swapfree)/swaptotal]) * 100
        p.append(self.widget.addPlot())
        p[-1].setXRange(-self.len_data*self.wait_time_ms/1000,
                             0, padding=0)
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
        self.mem_curve.append(p[-1].plot(pen=pg.mkPen('b', width=1),
                          fillLevel=-0.3, brush=(50, 50, 200, 50)))
        self.mem_curve.append(p[-1].plot(pen=pg.mkPen('r', width=1),
                          fillLevel=-0.3, brush=(200, 50, 50, 50)))
        self.update_meminfo()
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_meminfo)
        self.timer.start(self.wait_time_ms)

    def update_meminfo(self,):
        self.meminfo = np.roll(self.meminfo, -1, axis=0)
        memtotal, memoccup, swaptotal, swapfree = self.s.refresh_memory()
        self.meminfo[-1, :] = np.array([(memoccup)/memtotal,
                                        (swapfree - swapfree)/swaptotal]) * 100
        self.mem_curve[0].setData(self.x, self.meminfo[:, 0])
        self.mem_curve[1].setData(self.x, self.meminfo[:, 1])

    def update_cpuinfo(self,):
        self.cpuinfo = np.roll(self.cpuinfo, -1, axis=0)
        self.cpuinfo[-1, :] = self.s.refresh_stat() * 100
        for cpu in range(self.s.cpu_core_count):
            self.cpu_curve[cpu].setData(self.x, self.cpuinfo[:, cpu+1])

    def update_running_processes(self,):
        data = self.s.get_running_processes()
        numcols = len(data[0])
        numrows = len(data)
        self.tableWidget.setColumnCount(numcols)
        self.tableWidget.setRowCount(numrows)
        for row in range(numrows):
            for column in range(numcols):
                self.tableWidget.setItem(row, column,
                                         QtGui.QTableWidgetItem(data[row]
                                                                [column]))
        self.tableWidget.setHorizontalHeaderLabels(self.headertitle)
        # self.tableWidget.sortItems(2, QtCore.Qt.DescendingOrder)

def main():
    app = QtWidgets.QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
