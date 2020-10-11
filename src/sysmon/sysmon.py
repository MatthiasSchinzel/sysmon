from PyQt5 import QtWidgets, uic
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
import sys
import numpy as np
import os
from .gather_data import sysinfo
import pkg_resources


def bytes_to_bit(bytes, per_second_flag=0, r=2):
    if bytes * 8 > 1e12:
        number_str = str(round(int(bytes) / 1e12 * 8, r))
        unit = 'Tbit'
    elif bytes * 8 > 1e9:
        number_str = str(round(int(bytes) / 1e9 * 8, r))
        unit = 'Gbit'
    elif bytes * 8 > 1e6:
        number_str = str(round(int(bytes) / 1e6 * 8, r))
        unit = 'Mbit'
    elif bytes * 8 > 1e3:
        number_str = str(round(int(bytes) / 1e3 * 8, r))
        unit = 'kbit'
    else:
        number_str = str(round(int(bytes) * 8, r))
        unit = 'bit'
    if per_second_flag:
        unit += '/s'
        number_str = number_str + '{:>7}'.format(unit)
    else:
        number_str = number_str + '{:>5}'.format(unit)
    return number_str


def bytes_to_byte(bytes, per_second_flag=0, r=2):
    if bytes > 1e12:
        number_str = str(round(int(bytes) / 1e12, r))
        unit = 'TB'
    elif bytes > 1e9:
        number_str = str(round(int(bytes) / 1e9, r))
        unit = 'GB'
    elif bytes > 1e6:
        number_str = str(round(int(bytes) / 1e6, r))
        unit = 'MB'
    elif bytes > 1e3:
        number_str = str(round(int(bytes) / 1e3, r))
        unit = 'kB'
    else:
        number_str = str(int(bytes))
        unit = 'B'
    if per_second_flag:
        unit += '/s'
        number_str = number_str + '{:>5}'.format(unit)
    else:
        number_str = number_str + '{:>3}'.format(unit)
    return number_str


def bytes_to_bibyte(bytes, per_second_flag=0, r=2):
    if bytes > 1024**4:
        number_str = str(round(int(bytes) / 1024**4, r))
        unit = 'TiB'
    elif bytes > 1024**3:
        number_str = str(round(int(bytes) / 1024**3, r))
        unit = 'GiB'
    elif bytes > 1024**2:
        number_str = str(round(int(bytes) / 1024**2, r))
        unit = 'MiB'
    elif bytes > 1024:
        number_str = str(round(int(bytes) / 1024, r))
        unit = 'kiB'
    else:
        number_str = str(int(bytes))
        unit = 'B'
    if per_second_flag:
        unit += '/s'
        number_str = number_str + '{:>6}'.format(unit)
    else:
        number_str = number_str + '{:>4}'.format(unit)
    return number_str


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        pg.setConfigOption('background', 'w')
        pg.setConfigOption('foreground', 'k')
        pg.setConfigOptions(antialias=True)
        uic.loadUi(pkg_resources.resource_filename(__name__,
                                                   "sysmonitor.ui"), self)

        self.len_data = 60
        self.cpu_curve = []
        self.mem_curve = []
        self.gpu_curve = []
        self.net_curve = []
        self.disk_curve = []
        self.ti = []
        self.ti_net = []
        self.ti_disk = []
        self.wait_time_ms = 1000
        self.s = sysinfo()
        self.meminfo = np.zeros([self.len_data, 2])
        self.netinfo = np.zeros([self.len_data, 2, self.s.amount_net_adater])
        self.diskinfo = np.zeros([self.len_data, 2, self.s.amount_disks])
        self.cpuinfo = np.zeros([self.len_data, self.s.cpu_core_count + 1])
        self.x = np.linspace(-self.len_data * self.wait_time_ms / 1000, 0,
                             num=self.len_data, endpoint=True)
        self.label_8.setText(self.s.cpu_model_name)
        self.plot_meminfo()
        self.plot_cpuinfo()
        self.plot_netinfo()
        self.plot_diskinfo()
        self.headertitle = ('USER', 'PID', 'CPU [%]', 'MEM [%]',
                            'START', 'TIME', 'COMMAND')
        self.tableWidget.verticalHeader().setVisible(False)
        self.tableWidget.horizontalHeader().setHighlightSections(False)
        header = self.tableWidget.horizontalHeader()
        header.setResizeMode(QtGui.QHeaderView.ResizeToContents)
        header.setStretchLastSection(True)
        header.setResizeMode(False)
        self.tableWidget.setSelectionBehavior(
            QtGui.QAbstractItemView.SelectRows)
        self.tableWidget.setShowGrid(False)
        self.update_running_processes()
        self.timer_4 = QtCore.QTimer()
        self.timer_4.timeout.connect(self.update_running_processes)
        self.timer_4.start(self.wait_time_ms)
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
                hbox_1 = QtGui.QGridLayout(widget_1)
                hbox_2 = QtGui.QGridLayout(widget_2)
                hbox_3 = QtGui.QGridLayout(widget_3)
                hbox_4 = QtGui.QGridLayout(widget_4)
                hbox_5 = QtGui.QGridLayout(widget_5)

                label_1 = QtGui.QLabel("Gpu:")
                label_1_sub = QtGui.QLabel("% over 60 seconds")
                label_1_sub.setFont(QtGui.QFont('Ubuntu', 7))
                label_2 = QtGui.QLabel("Memory:")
                label_2_sub = QtGui.QLabel("% over 60 seconds")
                label_2_sub.setFont(QtGui.QFont('Ubuntu', 7))
                label_3 = QtGui.QLabel("Encoder:")
                label_3_sub = QtGui.QLabel("% over 60 seconds")
                label_3_sub.setFont(QtGui.QFont('Ubuntu', 7))
                label_4 = QtGui.QLabel("Decoder:")
                label_4_sub = QtGui.QLabel("% over 60 seconds")
                label_4_sub.setFont(QtGui.QFont('Ubuntu', 7))
                label_5 = QtGui.QLabel("Gpu clock:")
                label_6 = QtGui.QLabel("Memory clock:")
                hbox_1.addWidget(label_1, 1, 1)
                hbox_1.addWidget(label_2, 1, 2)
                hbox_1.addWidget(label_1_sub, 2, 1)
                hbox_1.addWidget(label_2_sub, 2, 2)
                hbox_3.addWidget(label_3, 1, 1)
                hbox_3.addWidget(label_4, 1, 2)
                hbox_3.addWidget(label_3_sub, 2, 1)
                hbox_3.addWidget(label_4_sub, 2, 2)
                hbox_5.addWidget(label_5, 1, 1)
                hbox_5.addWidget(label_6, 1, 2)

                graph_w_1 = pg.GraphicsLayoutWidget()
                graph_w_2 = pg.GraphicsLayoutWidget()
                graph_w_3 = pg.GraphicsLayoutWidget()
                graph_w_4 = pg.GraphicsLayoutWidget()

                hbox_2.addWidget(graph_w_1, 1, 1)
                hbox_2.addWidget(graph_w_2, 1, 2)
                hbox_4.addWidget(graph_w_3, 1, 1)
                hbox_4.addWidget(graph_w_4, 1, 2)

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
            for i in range(1, 5):
                p.append(self.gpu_widgets[gpu_ind][-i].addPlot())
                p[-1].setXRange(-self.len_data * self.wait_time_ms / 1000,
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
                                                 fillLevel=-0.3,
                                                 brush=(50, 50, 200, 50)))

    def plot_cpuinfo(self,):
        counter = 0
        p = []
        self.cpuinfo[-1, :] = self.s.refresh_stat() * 100
        for cpu in range(self.s.cpu_core_count):
            p.append(self.widget_2.addPlot())
            p[-1].setXRange(-self.len_data *
                            self.wait_time_ms / 1000, 0, padding=0)
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
            self.ti[-1].setPos(-self.len_data * self.wait_time_ms / 1000, 100)
            p[-1].addItem(self.ti[-1])
            self.ti.append(pg.TextItem('', anchor=(1, 0)))
            self.ti[-1].setPos(0, 100)
            p[-1].addItem(self.ti[-1])
            self.cpu_curve.append(p[-1].plot(pen=pg.mkPen('b', width=1),
                                             fillLevel=-0.3,
                                             brush=(50, 50, 200, 50)))
            if counter == 3:
                self.widget_2.nextRow()
                counter = 0
            else:
                counter += 1

        p.append(self.widget_5.addPlot())
        p[-1].setXRange(-self.len_data * self.wait_time_ms /
                        1000, 0, padding=0)
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
                                          fillLevel=-0.3,
                                          brush=(50, 50, 200, 50)))

        self.update_cpuinfo()
        self.timer_2 = QtCore.QTimer()
        self.timer_2.timeout.connect(self.update_cpuinfo)
        self.timer_2.start(self.wait_time_ms)

    def plot_meminfo(self,):
        p = []
        memtotal, memoccup, swaptotal, swapfree = self.s.refresh_memory()
        p.append(self.widget.addPlot())
        p[-1].setXRange(-self.len_data * self.wait_time_ms / 1000,
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
                                         fillLevel=-0.3,
                                         brush=(50, 50, 200, 50)))
        self.mem_curve.append(p[-1].plot(pen=pg.mkPen('r', width=1),
                                         fillLevel=-0.3,
                                         brush=(200, 50, 50, 50)))
        self.update_meminfo()
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_meminfo)
        self.timer.start(self.wait_time_ms)

    def plot_netinfo(self,):
        p = []
        self.s.refresh_network()
        for adapter in range(self.s.amount_net_adater):
            p.append(self.widget_10.addPlot())
            p[-1].setXRange(-self.len_data * self.wait_time_ms / 1000,
                            0, padding=0)
            p[-1].enableAutoRange('x', False)
            p[-1].showAxis('top', show=True)
            p[-1].showAxis('right', show=True)
            p[-1].axes['bottom']['item'].setStyle(showValues=True)
            p[-1].axes['top']['item'].setStyle(showValues=False)
            p[-1].axes['left']['item'].setStyle(showValues=False)
            p[-1].axes['right']['item'].setStyle(showValues=True)
            p[-1].axes['right']['item'].setGrid(100)
            p[-1].axes['top']['item'].setGrid(100)
            p[-1].setLabels(right=('', 'bit/s'))
            p[-1].setMouseEnabled(x=False, y=False)
            p[-1].hideButtons()
            p[-1].setMenuEnabled(False)
            p[-1].vb.setLimits(yMin=0)
            self.net_curve.append(p[-1].plot(pen=pg.mkPen('b', width=1),
                                             fillLevel=-0.3,
                                             brush=(50, 50, 200, 50)))
            self.net_curve.append(p[-1].plot(pen=pg.mkPen('r', width=1),
                                             fillLevel=-0.3,
                                             brush=(200, 50, 50, 50)))
            self.ti_net.append(p[-1])
            self.widget_10.nextRow()
        self.update_netinfo()
        adapter_text = ''
        for ind, adapter in enumerate(self.s.pysical_adapters):
            adapter_text += adapter
            if ind + 1 != self.s.amount_net_adater:
                adapter_text += ', '
        self.label_11.setText(adapter_text)
        self.timer_5 = QtCore.QTimer()
        self.timer_5.timeout.connect(self.update_netinfo)
        self.timer_5.start(self.wait_time_ms)

    def update_netinfo(self,):
        self.netinfo = np.roll(self.netinfo, -1, axis=0)
        rx_bytes, tx_bytes, rx_packets, tx_packets = self.s.refresh_network()
        for adapter in range(self.s.amount_net_adater):
            self.netinfo[-1, 0, adapter] = (
                (rx_bytes[adapter, 0] - rx_bytes[adapter, 1])
                / (self.wait_time_ms / (1e3)))
            self.netinfo[-1, 1, adapter] = (
                (tx_bytes[adapter, 0] - tx_bytes[adapter, 1])
                / (self.wait_time_ms / (1e3)))
            self.net_curve[0 + 2 * adapter].setData(
                self.x, self.netinfo[:, 0, adapter] * 8)
            self.net_curve[1 + 2 * adapter].setData(
                self.x, self.netinfo[:, 1, adapter] * 8)
            val_1 = "{:>13}".format(bytes_to_bit(
                self.netinfo[-1, 0, adapter], 1)).replace(" ", "&nbsp;")
            val_2 = "{:>13}".format(bytes_to_bit(
                self.netinfo[-1, 1, adapter], 1)).replace(" ", "&nbsp;")
            self.ti_net[adapter].setLabel(
                'top',
                "<span style = \"font-family:consolas\">" +
                "<span1 style=\"color:blue\">Rx: " +
                val_1 +
                "</span1> <span2 style=\"color:red\"> &nbsp;&nbsp;&nbsp;Tx: "
                + val_2 +
                '</span2></span>')
            if self.s.max_connection_speed[adapter] == '-1':
                self.ti_net[adapter].setLabel(
                    'bottom', self.s.pysical_adapters[adapter] +
                    ' disconnected' +
                    ', Total received: ' +
                    bytes_to_bibyte(rx_bytes[adapter, 0]) +
                    ', Total transmitted: ' +
                    bytes_to_bibyte(tx_bytes[adapter, 0]))
            elif self.s.max_connection_speed[adapter] == '-2':
                self.ti_net[adapter].setLabel(
                    'bottom', self.s.pysical_adapters[adapter] +
                    ', Total received: ' +
                    bytes_to_bibyte(rx_bytes[adapter, 0]) +
                    ', Total transmitted: ' +
                    bytes_to_bibyte(tx_bytes[adapter, 0]))
            else:
                self.ti_net[adapter].setLabel(
                    'bottom', self.s.pysical_adapters[adapter] +
                    ' connected with ' + self.s.max_connection_speed[adapter] +
                    ', Total received: ' +
                    bytes_to_bibyte(rx_bytes[adapter, 0]) +
                    ', Total transmitted: ' +
                    bytes_to_bibyte(tx_bytes[adapter, 0]))
            if ((self.netinfo[:, 0, adapter] * 8) < 1000).all() and \
               ((self.netinfo[:, 1, adapter] * 8) < 1000).all():
                self.ti_net[adapter].enableAutoRange('y', False)
                self.ti_net[adapter].setYRange(0, 1000, padding=0)
            else:
                self.ti_net[adapter].enableAutoRange('y', True)

    def plot_diskinfo(self,):
        p = []
        self.s.refresh_disks()
        for disk in range(self.s.amount_disks):
            p.append(self.widget_8.addPlot())
            p[-1].setXRange(-self.len_data * self.wait_time_ms / 1000,
                            0, padding=0)
            p[-1].enableAutoRange('x', False)
            p[-1].showAxis('top', show=True)
            p[-1].showAxis('right', show=True)
            p[-1].axes['bottom']['item'].setStyle(showValues=True)
            p[-1].axes['top']['item'].setStyle(showValues=False)
            p[-1].axes['left']['item'].setStyle(showValues=False)
            p[-1].axes['right']['item'].setStyle(showValues=True)
            p[-1].axes['right']['item'].setGrid(100)
            p[-1].axes['top']['item'].setGrid(100)
            p[-1].setLabels(right=('', 'B/s'))
            p[-1].setMouseEnabled(x=False, y=False)
            p[-1].hideButtons()
            p[-1].setMenuEnabled(False)
            p[-1].vb.setLimits(yMin=0)
            self.disk_curve.append(p[-1].plot(pen=pg.mkPen('b', width=1),
                                              fillLevel=-0.3,
                                              brush=(50, 50, 200, 50)))
            self.disk_curve.append(p[-1].plot(pen=pg.mkPen('r', width=1),
                                              fillLevel=-0.3,
                                              brush=(200, 50, 50, 50)))
            self.ti_disk.append(p[-1])
            self.widget_8.nextRow()
        self.update_diskinfo()
        disk_text = ''
        for ind, disk in enumerate(self.s.pysical_disk):
            disk_text += disk
            if ind + 1 != self.s.amount_disks:
                disk_text += ', '
        self.label_13.setText(disk_text)
        self.timer_6 = QtCore.QTimer()
        self.timer_6.timeout.connect(self.update_diskinfo)
        self.timer_6.start(self.wait_time_ms)

    def update_diskinfo(self,):
        self.diskinfo = np.roll(self.diskinfo, -1, axis=0)
        read_bytes, write_bytes = self.s.refresh_disks()
        for disk in range(self.s.amount_disks):
            self.diskinfo[-1, 0, disk] = ((read_bytes[disk, 0] -
                                          read_bytes[disk, 1])
                                          / (self.wait_time_ms / (1e3)))
            self.diskinfo[-1, 1, disk] = ((write_bytes[disk, 0] -
                                          write_bytes[disk, 1])
                                          / (self.wait_time_ms / (1e3)))
            self.disk_curve[0 + 2 *
                            disk].setData(self.x, self.diskinfo[:, 0, disk])
            self.disk_curve[1 + 2 *
                            disk].setData(self.x, self.diskinfo[:, 1, disk])
            val_1 = "{:>10}".format(bytes_to_byte(
                self.diskinfo[-1, 0, disk], 1)).replace(" ", "&nbsp;")
            val_2 = "{:>10}".format(bytes_to_byte(
                self.diskinfo[-1, 1, disk], 1)).replace(" ", "&nbsp;")
            self.ti_disk[disk].setLabel(
                'top',
                "<span style = \"font-family:consolas\">" +
                "<span1 style=\"color:blue\">Read: " +
                val_1 +
                "</span1>" +
                "<span2 style=\"color:red\"> &nbsp;&nbsp;&nbsp;Write: "
                + val_2 + '</span2></span>')
            self.ti_disk[disk].setLabel(
                'bottom', self.s.pysical_disk[disk] + ' (' +
                bytes_to_byte(self.s.pysical_disk_size[disk], r=0) + ')' +
                ', Total read: ' + bytes_to_byte(read_bytes[disk, 0]) +
                ', Total write: ' + bytes_to_byte(write_bytes[disk, 0]))
            if (self.diskinfo[:, 0, disk] < 1000).all() and \
               (self.diskinfo[:, 1, disk] < 1000).all():
                self.ti_disk[disk].enableAutoRange('y', False)
                self.ti_disk[disk].setYRange(0, 1000, padding=0)
            else:
                self.ti_disk[disk].enableAutoRange('y', True)

    def update_meminfo(self,):
        self.meminfo = np.roll(self.meminfo, -1, axis=0)
        memtotal, memoccup, swaptotal, swapfree = self.s.refresh_memory()
        if swaptotal != 0:
            self.meminfo[-1, :] = np.array([(memoccup) / memtotal,
                                            (swaptotal - swapfree)
                                            / swaptotal]) * 100
            self.mem_curve[1].setData(self.x, self.meminfo[:, 1])
            self.label_6.setText(
                'Swap: ' + str(round((swaptotal - swapfree) / 1048576, 1)) +
                'GiB of ' + str(round(swaptotal / 1048576, 1)) + 'GiB used (' +
                str(round(self.meminfo[-1, 1], 1)) + '%)')
        else:
            self.meminfo[-1, :] = np.array([(memoccup) / memtotal,
                                            0]) * 100
            self.label_6.setText('Swap not available')
        self.mem_curve[0].setData(self.x, self.meminfo[:, 0])
        self.label_5.setText(
            'Memory: ' + str(round(memoccup / 1048576, 1)) + 'GiB of ' +
            str(round(memtotal / 1048576, 1)) + 'GiB used (' +
            str(round(self.meminfo[-1, 0], 1)) + '%)')

    def update_gpuinfo(self,):
        self.gpuinfo = np.roll(self.gpuinfo, -1, axis=0)
        data = self.s.get_nvidia_smi_info()
        for gpu_ind in range(self.s.gpu_num):
            num = data[gpu_ind][4]
            if num != '-':
                self.gpuinfo[-1, 0, gpu_ind] = int(num)
                self.gpu_curve[3 + 4 * gpu_ind].setData(
                    self.x, self.gpuinfo[:, 0, gpu_ind])
            num = data[gpu_ind][5]
            if num != '-':
                self.gpuinfo[-1, 1, gpu_ind] = int(num)
                self.gpu_curve[2 + 4 * gpu_ind].setData(
                    self.x, self.gpuinfo[:, 1, gpu_ind])
            num = data[gpu_ind][6]
            if num != '-':
                self.gpuinfo[-1, 2, gpu_ind] = int(num)
                self.gpu_curve[1 + 4 * gpu_ind].setData(
                    self.x, self.gpuinfo[:, 2, gpu_ind])
            num = data[gpu_ind][7]
            if num != '-':
                self.gpuinfo[-1, 3, gpu_ind] = int(num)
                self.gpu_curve[0 + 4 * gpu_ind].setData(
                    self.x, self.gpuinfo[:, 3, gpu_ind])
            self.gpu_widgets[gpu_ind][-5].setText(
                "Memory clock: " + str(int(data[gpu_ind][8])) + 'MHz')
            self.gpu_widgets[gpu_ind][-6].setText(
                "Gpu clock: " + str(int(data[gpu_ind][9])) + 'MHz')

    def update_cpuinfo(self,):
        self.cpuinfo = np.roll(self.cpuinfo, -1, axis=0)
        self.cpuinfo[-1, :] = self.s.refresh_stat() * 100
        for cpu in range(self.s.cpu_core_count):
            self.cpu_curve[cpu].setData(self.x, self.cpuinfo[:, cpu + 1])
            self.ti[0 + 2 * cpu].setText(
                str(round(self.s.cpu_clock[cpu] / 1000000, 2)) + 'GHz')
            self.ti[1 + 2 * cpu].setText(
                str(int(self.cpuinfo[-1, cpu + 1])) + '%')
        self.cpu_curve[cpu + 1].setData(self.x, self.cpuinfo[:, 0])
        self.label_3.setText('Overall usage: ' +
                             str(round(self.cpuinfo[-1, 0], 1)) + '%')
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
                    item.setData(QtCore.Qt.DisplayRole,
                                 float(data[row][column]))
                    self.tableWidget.setItem(row, column,
                                             QtGui.QTableWidgetItem(item))
                else:
                    self.tableWidget.setItem(row, column,
                                             QtGui.QTableWidgetItem(data[row]
                                                                    [column]))
        self.tableWidget.setHorizontalHeaderLabels(self.headertitle)


def main():
    os.environ['PATH'] = '/sbin:' + os.environ.get('PATH')
    app = QtWidgets.QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
