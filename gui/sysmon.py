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
        self.gpu_curve = []
        self.net_curve = []
        self.ti = []
        self.ti_net = []
        self.wait_time_ms = 1000
        self.s = sysinfo()
        self.meminfo = np.zeros([self.len_data, 2])
        self.netinfo = np.zeros([self.len_data, 2, self.s.amount_net_adater])
        self.cpuinfo = np.zeros([self.len_data, self.s.cpu_core_count+1])
        self.x = np.linspace(-self.len_data*self.wait_time_ms/1000, 0,
                             num=self.len_data, endpoint=True)
        self.label_8.setText(self.s.cpu_model_name)
        self.plot_meminfo()
        self.plot_cpuinfo()
        self.plot_netinfo()
        self.headertitle = ('USER', 'PID', 'CPU [%]', 'MEM [%]', 'START', 'TIME', 'COMMAND')
        self.tableWidget.verticalHeader().setVisible(False)
        self.tableWidget.horizontalHeader().setHighlightSections(False)
        # self.tableWidget.setRowCount(4096)
        # self.tableWidget.setColumnCount(5)
        # self.tableWidget.setHorizontalHeaderLabels(headertitle)
        header = self.tableWidget.horizontalHeader()
        header.setResizeMode(QtGui.QHeaderView.ResizeToContents)
        header.setStretchLastSection(True)
        header.setResizeMode(False)
        self.tableWidget.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        # self.tableWidget.setSortingEnabled(True)
        self.tableWidget.setShowGrid(False)
        self.update_running_processes()
        self.timer_4 = QtCore.QTimer()
        self.timer_4.timeout.connect(self.update_running_processes)
        self.timer_4.start(self.wait_time_ms)
        # dynamically create gpu tabs
        if self.s.nvidia_installed == 1:
            self.gpu_widgets = []
            self.gpuinfo = np.zeros([self.len_data, 4, self.s.gpu_num])
            for gpu_ind in range(self.s.gpu_num):
                tab_widgets = []
                # first set vertical alignment of tab
                tab = QtWidgets.QWidget()
                self.tabWidget.addTab(tab, self.s.gpu_name[gpu_ind])
                vbox = QtGui.QVBoxLayout(tab)

                # then add widgets in horizontal layout
                widget_1 = QtWidgets.QWidget()
                widget_2 = QtWidgets.QWidget()
                widget_3 = QtWidgets.QWidget()
                widget_4 = QtWidgets.QWidget()
                widget_5 = QtWidgets.QWidget()
                vbox.addWidget(widget_1)
                vbox.addWidget(widget_2)
                vbox.addWidget(widget_3)
                vbox.addWidget(widget_4)
                vbox.addWidget(widget_5)
                hbox_1 = QtGui.QHBoxLayout(widget_1)
                hbox_2 = QtGui.QHBoxLayout(widget_2)
                hbox_3 = QtGui.QHBoxLayout(widget_3)
                hbox_4 = QtGui.QHBoxLayout(widget_4)
                hbox_5 = QtGui.QHBoxLayout(widget_5)

                label_1 = QtGui.QLabel("Gpu:") # pg.GraphicsLayoutWidget()
                label_2 = QtGui.QLabel("Memory:") #pg.GraphicsLayoutWidget()
                label_3 = QtGui.QLabel("Encoder:") # pg.GraphicsLayoutWidget()
                label_4 = QtGui.QLabel("Decoder:") #pg.GraphicsLayoutWidget()
                label_5 = QtGui.QLabel("Gpu clock:") # pg.GraphicsLayoutWidget()
                label_6 = QtGui.QLabel("Memory clock:") #pg.GraphicsLayoutWidget()
                hbox_1.addWidget(label_1)
                hbox_1.addWidget(label_2)
                hbox_3.addWidget(label_3)
                hbox_3.addWidget(label_4)
                hbox_5.addWidget(label_5)
                hbox_5.addWidget(label_6)

                graph_w_1 = pg.GraphicsLayoutWidget()
                graph_w_2 = pg.GraphicsLayoutWidget()
                graph_w_3 = pg.GraphicsLayoutWidget()
                graph_w_4 = pg.GraphicsLayoutWidget()

                hbox_2.addWidget(graph_w_1)
                hbox_2.addWidget(graph_w_2)
                hbox_4.addWidget(graph_w_3)
                hbox_4.addWidget(graph_w_4)

                # Append for later access
                tab_widgets.append(tab)
                tab_widgets.append(vbox)
                tab_widgets.append(widget_1)
                tab_widgets.append(widget_2)
                tab_widgets.append(widget_3)
                tab_widgets.append(widget_4)
                tab_widgets.append(widget_5)
                tab_widgets.append(hbox_1)
                tab_widgets.append(hbox_2)
                tab_widgets.append(hbox_3)
                tab_widgets.append(hbox_4)
                tab_widgets.append(hbox_5)
                tab_widgets.append(label_1)
                tab_widgets.append(label_2)
                tab_widgets.append(label_3)
                tab_widgets.append(label_4)
                tab_widgets.append(label_5)
                tab_widgets.append(label_6)
                tab_widgets.append(graph_w_1)
                tab_widgets.append(graph_w_2)
                tab_widgets.append(graph_w_3)
                tab_widgets.append(graph_w_4)
                self.gpu_widgets.append(tab_widgets)
            self.plot_gpuinfo()
            self.update_gpuinfo()
            self.timer_3 = QtCore.QTimer()
            self.timer_3.timeout.connect(self.update_gpuinfo)
            self.timer_3.start(self.wait_time_ms)

    def plot_gpuinfo(self,):
        p = []
        for gpu_ind in range(self.s.gpu_num):
            for i in range(1,5):
                p.append(self.gpu_widgets[gpu_ind][-i].addPlot())
                p[-1].setXRange(-self.len_data*self.wait_time_ms/1000,
                                     0, padding=0)
                p[-1].setYRange(0, 100, padding=0)
                p[-1].enableAutoRange('xy', False)
                p[-1].showAxis('top', show=True)
                p[-1].showAxis('right', show=True)
                p[-1].axes['bottom']['item'].setStyle(showValues=True)
                p[-1].axes['top']['item'].setStyle(showValues=False)
                p[-1].axes['left']['item'].setStyle(showValues=False)
                p[-1].axes['right']['item'].setStyle(showValues=True)
                p[-1].axes['right']['item'].setGrid(100)
                p[-1].axes['top']['item'].setGrid(100)
                p[-1].setLabel('bottom', "Seconds")
                p[-1].setMouseEnabled(x=False, y=False)
                p[-1].hideButtons()
                p[-1].setMenuEnabled(False)
                self.gpu_curve.append(p[-1].plot(pen=pg.mkPen('b', width=1),
                            fillLevel=-0.3, brush=(50, 50, 200, 50)))

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
            self.ti.append(pg.TextItem('', anchor=(0, 0)))
            self.ti[-1].setPos(-self.len_data*self.wait_time_ms/1000, 100)
            p[-1].addItem(self.ti[-1])
            self.ti.append(pg.TextItem('', anchor=(1, 0)))
            self.ti[-1].setPos(0, 100)
            p[-1].addItem(self.ti[-1])
            self.cpu_curve.append(p[-1].plot(pen=pg.mkPen('b', width=1),
                         fillLevel=-0.3, brush=(50, 50, 200, 50)))
            if counter == 3:
                self.widget_2.nextRow()
                counter = 0
            else:
                counter += 1

        p.append(self.widget_5.addPlot())
        p[-1].setXRange(-self.len_data*self.wait_time_ms/1000, 0, padding=0)
        p[-1].setYRange(0, 100, padding=0)
        p[-1].enableAutoRange('xy', False)
        p[-1].showAxis('top', show=True)
        p[-1].showAxis('right', show=True)
        p[-1].axes['bottom']['item'].setStyle(showValues=True)
        p[-1].axes['top']['item'].setStyle(showValues=False)
        p[-1].axes['left']['item'].setStyle(showValues=False)
        p[-1].axes['right']['item'].setStyle(showValues=True)
        p[-1].axes['right']['item'].setGrid(100)
        p[-1].axes['top']['item'].setGrid(100)
        p[-1].setLabel('right', "[%]")
        p[-1].setLabel('bottom', "Seconds")
        p[-1].setMouseEnabled(x=False, y=False)
        p[-1].hideButtons()
        p[-1].setMenuEnabled(False)
        self.cpu_curve .append(p[-1].plot(pen=pg.mkPen('b', width=1),
                     fillLevel=-0.3, brush=(50, 50, 200, 50)))

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
        p[-1].axes['bottom']['item'].setStyle(showValues=True)
        p[-1].axes['top']['item'].setStyle(showValues=False)
        p[-1].axes['left']['item'].setStyle(showValues=False)
        p[-1].axes['right']['item'].setStyle(showValues=True)
        p[-1].axes['right']['item'].setGrid(100)
        p[-1].axes['top']['item'].setGrid(100)
        p[-1].setLabel('bottom', "Seconds")
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

    def plot_netinfo(self,):
        p = []
        p.append(self.widget_10.addPlot())
        self.s.refresh_network()
        for adapter in range(self.s.amount_net_adater):
            p[-1].setXRange(-self.len_data*self.wait_time_ms/1000,
                              0, padding=0)
            #p[-1].setYRange(0, 100, padding=0)
            p[-1].enableAutoRange('x', False)
            p[-1].showAxis('top', show=True)
            p[-1].showAxis('right', show=True)
            p[-1].axes['bottom']['item'].setStyle(showValues=True)
            p[-1].axes['top']['item'].setStyle(showValues=False)
            p[-1].axes['left']['item'].setStyle(showValues=False)
            p[-1].axes['right']['item'].setStyle(showValues=True)
            p[-1].axes['right']['item'].setGrid(100)
            p[-1].axes['top']['item'].setGrid(100)
            p[-1].setLabel('bottom', "Seconds")
            p[-1].setLabel('top', "Hi")
            p[-1].setMouseEnabled(x=False, y=False)
            p[-1].hideButtons()
            p[-1].setMenuEnabled(False)
            p[-1].vb.setLimits(yMin=0)
            self.net_curve.append(p[-1].plot(pen=pg.mkPen('b', width=1),
                              fillLevel=-0.3, brush=(50, 50, 200, 50)))
            self.net_curve.append(p[-1].plot(pen=pg.mkPen('r', width=1),
                              fillLevel=-0.3, brush=(200, 50, 50, 50)))
            self.ti_net.append(p[-1])
            # self.ti_net.append(pg.TextItem('', anchor=(0, 1)))
            # self.ti_net[-1].setPos(-self.len_data*self.wait_time_ms/1000, 0)
            # p[-1].addItem(self.ti_net[-1])
            # self.ti_net.append(pg.TextItem('', anchor=(1, 1)))
            # self.ti_net[-1].setPos(0, 0)
            # p[-1].addItem(self.ti_net[-1])
            self.widget_10.nextRow()
        self.update_netinfo()
        self.timer_5 = QtCore.QTimer()
        self.timer_5.timeout.connect(self.update_netinfo)
        self.timer_5.start(self.wait_time_ms)

    def update_netinfo(self,):
        self.netinfo = np.roll(self.netinfo, -1, axis=0)
        rx_bytes, tx_bytes, rx_packets, tx_packets = self.s.refresh_network()
        for adapter in range(self.s.amount_net_adater):
            self.netinfo[-1, 0, adapter] = (rx_bytes[adapter, 0] - rx_bytes[adapter, 1]) / self.wait_time_ms
            self.netinfo[-1, 1, adapter] = (tx_bytes[adapter, 0] - tx_bytes[adapter, 1]) / self.wait_time_ms
            self.net_curve[0 + 2 * adapter].setData(self.x, self.netinfo[:, 0, adapter])
            self.net_curve[1 + 2 * adapter].setData(self.x, self.netinfo[:, 1, adapter])
            self.ti_net[adapter].setLabel('top', 'Rx: ' + str(self.netinfo[-1, 0, adapter]) + ' bytes/s<br>' +
                                          'Tx: ' + str(self.netinfo[-1, 1, adapter]) + ' bytes/s')
            # self.ti_net[1 + 2 * adapter].setText('Tx: ' + str(self.netinfo[-1, 1, adapter]) + ' bytes/s\n')

    def update_meminfo(self,):
        self.meminfo = np.roll(self.meminfo, -1, axis=0)
        memtotal, memoccup, swaptotal, swapfree = self.s.refresh_memory()
        self.meminfo[-1, :] = np.array([(memoccup)/memtotal,
                                        (swaptotal - swapfree)/swaptotal]) * 100
        self.mem_curve[0].setData(self.x, self.meminfo[:, 0])
        self.mem_curve[1].setData(self.x, self.meminfo[:, 1])
        self.label_5.setText('Memory: ' + str(round(memoccup/1048576, 1)) + 'GiB of ' + str(round(memtotal/1048576, 1)) + 'GiB used (' + str(round(self.meminfo[-1, 0], 1)) + '%)')
        self.label_6.setText('Swap: ' + str(round((swaptotal - swapfree)/1048576, 1)) + 'GiB of ' + str(round(swaptotal/1048576, 1)) + 'GiB used (' + str(round(self.meminfo[-1, 1], 1)) + '%)')


    def update_gpuinfo(self,):
        self.gpuinfo = np.roll(self.gpuinfo, -1, axis=0)
        data = self.s.get_nvidia_smi_info()
        for gpu_ind in range(self.s.gpu_num):
            self.gpuinfo[-1, 0, gpu_ind] = int(data[gpu_ind][4])
            self.gpu_curve[3 + 4 * gpu_ind].setData(self.x, self.gpuinfo[:, 0, gpu_ind])
            self.gpuinfo[-1, 1, gpu_ind] = int(data[gpu_ind][5])
            self.gpu_curve[2 + 4 * gpu_ind].setData(self.x, self.gpuinfo[:, 1, gpu_ind])
            self.gpuinfo[-1, 2, gpu_ind] = int(data[gpu_ind][6])
            self.gpu_curve[1 + 4 * gpu_ind].setData(self.x, self.gpuinfo[:, 2, gpu_ind])
            self.gpuinfo[-1, 3, gpu_ind] = int(data[gpu_ind][7])
            self.gpu_curve[0 + 4 * gpu_ind].setData(self.x, self.gpuinfo[:, 3, gpu_ind])
            self.gpu_widgets[gpu_ind][-5].setText("Memory clock: " + str(int(data[gpu_ind][8])) + 'MHz')
            self.gpu_widgets[gpu_ind][-6].setText("Gpu clock: " + str(int(data[gpu_ind][9])) + 'MHz')


    def update_cpuinfo(self,):
        self.cpuinfo = np.roll(self.cpuinfo, -1, axis=0)
        self.cpuinfo[-1, :] = self.s.refresh_stat() * 100
        for cpu in range(self.s.cpu_core_count):
            self.cpu_curve[cpu].setData(self.x, self.cpuinfo[:, cpu+1])
            self.ti[0 + 2 * cpu].setText(str(round(self.s.cpu_clock[cpu]/1000000, 2)) + 'GHz')
            self.ti[1 + 2 * cpu].setText(str(int(self.cpuinfo[-1, cpu+1])) + '%')
        self.cpu_curve[cpu+1].setData(self.x, self.cpuinfo[:, 0])
        self.label_3.setText('Overall usage: ' + str(round(self.cpuinfo[-1, 0], 1)) + '%')
        self.label_7.setText(str(round(self.cpuinfo[-1, 0], 1)) + '%')

    def update_running_processes(self,):
        data = self.s.get_running_processes(only_usr=False)
        numcols = len(data[0])
        numrows = len(data)
        self.tableWidget.setColumnCount(numcols)
        self.tableWidget.setRowCount(numrows)
        for row in range(numrows):
            for column in range(numcols):
                if column == 1 or column == 2 or column == 3:
                    item = QtWidgets.QTableWidgetItem()
                    item.setData(QtCore.Qt.DisplayRole, float(data[row][column]))
                    self.tableWidget.setItem(row, column,
                                             QtGui.QTableWidgetItem(item))
                else:
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
