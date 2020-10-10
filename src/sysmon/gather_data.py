import numpy as np
from pathlib import Path
import subprocess
import getpass


class NoCPUInformation(Exception):
    pass


class NoMemoryInformation(Exception):
    pass


class sysinfo:
    def __init__(self,):
        if not Path('/proc/stat').is_file():
            raise NoCPUInformation('/proc/stat does not exist. ' +
                                   'Maybe you use a virtual machine?')
        if not Path('/proc/meminfo').is_file():
            raise NoMemoryInformation('/proc/meminfo does not exist.')
        self.lines = []
        self.cpu_core_count = 0
        self.pysical_cpu_core_count = 0
        self.cpu_model_name = []
        self.previdle = 0
        self.previowait = 0
        self.amount_disks = 0
        self.read_file('stat')
        self.count_cpu_cores()
        self.get_pysical_disks_and_size()
        self.user = np.zeros([self.cpu_core_count+1, 2])
        self.nice = np.zeros([self.cpu_core_count+1, 2])
        self.system = np.zeros([self.cpu_core_count+1, 2])
        self.idle = np.zeros([self.cpu_core_count+1, 2])
        self.iowait = np.zeros([self.cpu_core_count+1, 2])
        self.irq = np.zeros([self.cpu_core_count+1, 2])
        self.softirq = np.zeros([self.cpu_core_count+1, 2])
        self.steal = np.zeros([self.cpu_core_count+1, 2])
        self.guest = np.zeros([self.cpu_core_count+1, 2])
        self.guest_nice = np.zeros([self.cpu_core_count+1, 2])
        self.cpu_clock = np.zeros([self.cpu_core_count, ])
        self.read_bytes = np.zeros([self.amount_disks, 2])
        self.write_bytes = np.zeros([self.amount_disks, 2])
        self.cpu_load = 0
        self.memtotal = 0
        self.memfree = 0
        self.swaptotal = 0
        self.swapfree = 0
        self.username = getpass.getuser()
        self.nvidia_installed = 0
        self.gpu_num = 0
        self.gpu_name = []
        self.check_for_nvidia_smi()
        if self.nvidia_installed == 1:
            self.get_basic_info_nvidia_smi()
        self.get_cpuinfo()
        self.get_all_pysical_adapters()
        self.get_max_connection_speed()

    def read_file(self, type):
        with open('/proc/' + type, 'r') as reader:
            file = reader.read()
        self.lines = file.splitlines()

    def count_cpu_cores(self,):
        self.cpu_core_count = 0
        for line in self.lines:
            if "cpu" in line:
                self.cpu_core_count += 1
        self.cpu_core_count -= 1

    def parse_stat(self,):
        self.user = np.roll(self.user, 1)
        self.nice = np.roll(self.nice, 1)
        self.system = np.roll(self.system, 1)
        self.idle = np.roll(self.idle, 1)
        self.iowait = np.roll(self.iowait, 1)
        self.irq = np.roll(self.irq, 1)
        self.softirq = np.roll(self.softirq, 1)
        self.steal = np.roll(self.steal, 1)
        self.guest = np.roll(self.guest, 1)
        self.guest_nice = np.roll(self.guest_nice, 1)
        for cpu in range(0, self.cpu_core_count+1):
            cur_data = self.lines[cpu].split()
            self.user[cpu, 0] = int(cur_data[1])
            self.nice[cpu, 0] = int(cur_data[2])
            self.system[cpu, 0] = int(cur_data[3])
            self.idle[cpu, 0] = int(cur_data[4])
            self.iowait[cpu, 0] = int(cur_data[5])
            self.irq[cpu, 0] = int(cur_data[6])
            self.softirq[cpu, 0] = int(cur_data[7])
            self.steal[cpu, 0] = int(cur_data[8])
            self.guest[cpu, 0] = int(cur_data[9])
            self.guest_nice[cpu, 0] = int(cur_data[10])

    def process_stat(self,):
        PrevIdle = self.idle[:, 1] + self.iowait[:, 1]
        Idle = self.idle[:, 0] + self.iowait[:, 0]
        PrevNonIdle = (self.user[:, 1] +
                       self.nice[:, 1] +
                       self.system[:, 1] +
                       self.irq[:, 1] +
                       self.softirq[:, 1] +
                       self.steal[:, 1])
        NonIdle = (self.user[:, 0] +
                   self.nice[:, 0] +
                   self.system[:, 0] +
                   self.irq[:, 0] +
                   self.softirq[:, 0] +
                   self.steal[:, 0])
        PrevTotal = PrevIdle + PrevNonIdle
        Total = Idle + NonIdle
        totald = Total - PrevTotal
        idled = Idle - PrevIdle
        self.cpu_load = (totald - idled)/totald

    def parse_meminfo(self,):
        for line in self.lines:
            if "MemTotal" in line:
                cur_data = line.split()
                self.memtotal = int(cur_data[1])
            if "MemFree" in line:
                cur_data = line.split()
                self.memfree = int(cur_data[1])
            if "SwapTotal" in line:
                cur_data = line.split()
                self.swaptotal = int(cur_data[1])
            if "SwapFree" in line:
                cur_data = line.split()
                self.swapfree = int(cur_data[1])
            if "Buffers" in line:
                cur_data = line.split()
                self.buffers = int(cur_data[1])
            if "Cached" in line:
                if "SwapCached" not in line:
                    cur_data = line.split()
                    self.cached = int(cur_data[1])

    def get_running_processes(self, only_usr=True):
        ps = str(subprocess.Popen(['ps', 'aux', '--sort=-pcpu'],
                                  stdout=subprocess.PIPE).communicate()[0])
        processes = ps.split('\\n')
        processes.pop(0)
        processes.pop(-1)
        process = []
        counter = 0
        max = 50
        for cur_process in processes:
            cur_list = cur_process.split(maxsplit=10)
            cur_list.pop(4)
            cur_list.pop(4)
            cur_list.pop(4)
            cur_list.pop(4)
            if cur_list[0] == self.username and only_usr is True:
                process.append(cur_list)
                process[-1][2] = round(float(
                                    process[-1][2])/self.cpu_core_count, 1)
            elif only_usr is False:
                process.append(cur_list)
                process[-1][2] = round(float(
                                    process[-1][2])/self.cpu_core_count, 1)
            if counter > max:
                break
            counter += 1
        return process

    def check_for_nvidia_smi(self,):
        ps = str(subprocess.Popen(['command -v nvidia-smi'],
                                  stdout=subprocess.PIPE,
                                  shell=True).communicate()[0].decode("utf-8"))
        processes = ps.strip('\n')
        if processes:
            self.nvidia_installed = 1
            ps = str(subprocess.Popen(
                ['nvidia-smi'], stdout=subprocess.PIPE)
                .communicate()[0].decode("utf-8"))
            nvidia_smi_feedback = ps.strip('\n')
            if 'failed' in nvidia_smi_feedback:
                print('There seems to be a problem with your GPU. Disabling' +
                      ' GPU support. Please check nvidia-smi')
                self.nvidia_installed = 0

    def get_basic_info_nvidia_smi(self,):
        ps = str(subprocess.Popen(
            ['nvidia-smi', '-L'], stdout=subprocess.PIPE)
            .communicate()[0].decode("utf-8"))
        processes = ps.split('\n')
        processes.pop(-1)
        self.gpu_num = len(processes)
        for id, gpu in enumerate(processes):
            gpu = gpu.replace('GPU ' + str(id) + ': ', '')
            gpu = gpu.split('(')
            self.gpu_name.append(gpu[0].rstrip())

    def get_nvidia_smi_info(self,):
        ps = str(subprocess.Popen(['nvidia-smi', 'dmon', '-c', '1'],
                                  stdout=subprocess.PIPE).communicate()[0])
        processes = ps.split('\\n')
        processes.pop(0)
        processes.pop(0)
        processes.pop(-1)
        smi_info = []
        for cur_process in processes:
            smi_info.append([j for j in cur_process.split(maxsplit=9)])
        return smi_info

    def get_cpu_clock_speed(self,):
        ps = str(subprocess.Popen(
                ['cat /sys/devices/system/cpu/cpu*/cpufreq/scaling_cur_freq'],
                stdout=subprocess.PIPE, shell=True)
                .communicate()[0].decode("utf-8"))
        processes = ps.split('\n')
        processes.pop(-1)
        lst = range(len(processes))
        lst = [str(x) for x in lst]
        lst.sort()
        lst = [int(x) for x in lst]
        processes = [x for _, x in sorted(zip(lst, processes))]
        for id, process in enumerate(processes):
            self.cpu_clock[id] = int(process)

    def parse_cpuinfo(self,):
        for line in self.lines:
            if "model name" in line:
                # cur_data = line.split(maxsplit=1)
                line = line.replace('model name', '')
                line = line.replace(':', '')
                self.cpu_model_name = line
            if "cpu cores" in line:
                cur_data = line.split()
                self.pysical_cpu_core_count = cur_data[-1]

    def get_all_pysical_adapters(self,):
        ps = str(subprocess.Popen(
            ['ls -l /sys/class/net/'], stdout=subprocess.PIPE, shell=True)
            .communicate()[0].decode("utf-8"))
        processes = ps.split('\n')
        processes.pop(0)
        processes.pop(-1)
        self.pysical_adapters = []
        self.amount_net_adater = 0
        for line in processes:
            if 'virtual' not in line:
                self.pysical_adapters.append(line.split()[8])
                self.amount_net_adater += 1
        self.rx_bytes = np.zeros([self.amount_net_adater, 2])
        self.rx_packets = np.zeros([self.amount_net_adater, 2])
        self.tx_bytes = np.zeros([self.amount_net_adater, 2])
        self.tx_packets = np.zeros([self.amount_net_adater, 2])
        ps = str(subprocess.Popen(['command -v iwconfig'],
                                  stdout=subprocess.PIPE,
                                  shell=True).communicate()[
                                  0].decode("utf-8"))
        self.iwconfig_exist = ps.strip('\n')

    def get_max_connection_speed(self,):
        self.max_connection_speed = []
        for adapter in self.pysical_adapters:
            if 'wl' not in adapter:
                ps = str(subprocess.Popen(
                    ['cat /sys/class/net/' + adapter + '/speed'],
                    stdout=subprocess.PIPE, shell=True)
                    .communicate()[0].decode("utf-8"))
                processes = ps.split('\n')
                processes.pop(-1)
                self.max_connection_speed.append(processes[-1])
                if self.max_connection_speed[-1] != '-1':
                    self.max_connection_speed[-1] += ' Mbit/s'
            else:
                if self.iwconfig_exist:
                    ps = str(subprocess.Popen(
                        ['iwconfig ' + adapter + ' | grep "Bit Rate"'],
                        stdout=subprocess.PIPE, shell=True)
                        .communicate()[0].decode("utf-8"))
                    processes = ps.split('\n')
                    if processes[0] != '':
                        processes.pop(-1)
                        self.max_connection_speed.append(processes[
                                                         -1].split()[
                                                         1].replace(
                                                         'Rate=', '') +
                                                         ' Mbit/s')
                    else:
                        self.max_connection_speed.append(str(-1))
                else:
                    # wifi, but iwconfig not working
                    self.max_connection_speed.append(str(-2))

    def get_pysical_disks_and_size(self,):
        ps = str(subprocess.Popen(
            ['lsblk -b | grep -e ^NAME -e disk'],
            stdout=subprocess.PIPE, shell=True)
            .communicate()[0].decode("utf-8"))
        processes = ps.split('\n')
        processes.pop(0)
        processes.pop(-1)
        self.pysical_disk = []
        self.pysical_disk_size = []
        self.amount_disks = 0
        for line in processes:
            cur_line = line.split()
            self.pysical_disk.append(cur_line[0])
            self.pysical_disk_size.append(cur_line[3])
            self.amount_disks += 1
        for ind, size in enumerate(self.pysical_disk_size):
            if 'K' in size:
                self.pysical_disk_size[ind] = float(size.replace('K', '')
                                                    .replace(',', '.')) * 1e3
            if 'M' in size:
                self.pysical_disk_size[ind] = float(size.replace('M', '')
                                                    .replace(',', '.')) * 1e6
            if 'G' in size:
                self.pysical_disk_size[ind] = float(size.replace('G', '')
                                                    .replace(',', '.')) * 1e9
            if 'T' in size:
                self.pysical_disk_size[ind] = float(size.replace('T', '')
                                                    .replace(',', '.')) * 1e12
            else:
                self.pysical_disk_size[ind] = int(size)

    def parse_disk_data(self,):
        self.disk_data = []
        for disk in self.pysical_disk:
            for line in self.lines:
                cur_line = line.split(maxsplit=17)
                if disk == cur_line[2]:
                    self.disk_data.append(cur_line)

    def process_disk_data(self,):
        self.read_bytes = np.roll(self.read_bytes, 1)
        self.write_bytes = np.roll(self.write_bytes, 1)
        for ind in range(self.amount_disks):
            self.read_bytes[ind, 0] = int(self.disk_data[ind][5]) * 512
            self.write_bytes[ind, 0] = int(self.disk_data[ind][9]) * 512

    def parse_network_info(self,):
        self.adapter_info = []
        for adapter in self.pysical_adapters:
            for line in self.lines:
                if adapter in line:
                    self.adapter_info.append(line.split())

    def process_network_info(self,):
        self.rx_bytes = np.roll(self.rx_bytes, 1)
        self.rx_packets = np.roll(self.rx_packets, 1)
        self.tx_bytes = np.roll(self.tx_bytes, 1)
        self.tx_packets = np.roll(self.tx_packets, 1)
        for ind in range(self.amount_net_adater):
            self.rx_bytes[ind, 0] = self.adapter_info[ind][1]
            self.rx_packets[ind, 0] = self.adapter_info[ind][2]
            self.tx_bytes[ind, 0] = self.adapter_info[ind][9]
            self.tx_packets[ind, 0] = self.adapter_info[ind][10]

    def get_cpuinfo(self,):
        self.read_file('cpuinfo')
        self.parse_cpuinfo()

    def refresh_stat(self,):
        self.read_file('stat')
        self.parse_stat()
        self.process_stat()
        self.get_cpu_clock_speed()
        return self.cpu_load

    def refresh_network(self,):
        self.read_file('net/dev')
        self.parse_network_info()
        self.process_network_info()
        self.get_max_connection_speed()
        return self.rx_bytes, self.tx_bytes, self.rx_packets, self.tx_packets

    def refresh_memory(self,):
        self.read_file('meminfo')
        self.parse_meminfo()
        cached = (self.buffers + self.cached)
        self.non_cached = self.memtotal - self.memfree - cached
        return self.memtotal, self.non_cached, self.swaptotal, self.swapfree

    def refresh_disks(self,):
        self.read_file('diskstats')
        self.parse_disk_data()
        self.process_disk_data()
        return self.read_bytes, self.write_bytes
