import subprocess

ps = str(subprocess.Popen(['nvidia-smi', 'dmon', '-c', '1'], stdout=subprocess.PIPE).communicate()[0])
processes = ps.split('\\n')
processes.pop(0)
processes.pop(0)
processes.pop(-1)
process = []
for cur_process in processes:
    process.append([j for j in cur_process.split(maxsplit = 9)])


ps = str(subprocess.Popen(['command -v nvidia-sm'], stdout=subprocess.PIPE, shell=True).communicate()[0].decode("utf-8") )
processes = ps.strip('\n')
if not processes:
    print('nvidia-smi not detected')

ps = str(subprocess.Popen(['nvidia-smi', '-L'], stdout=subprocess.PIPE).communicate()[0].decode("utf-8"))
processes = ps.split('\n')
processes.pop(-1)
id = 0
gpu_num = len(processes)
gpu_name = []
for gpu in processes:
    gpu = gpu..replace('GPU ' + str(id) + ': ', '')
    gpu = gpu.split('(')
    gpu_name.append(gpu[0].rstrip())
    id += 1


ps = str(subprocess.Popen(['cat /sys/devices/system/cpu/cpu*/cpufreq/scaling_cur_freq'], stdout=subprocess.PIPE, shell=True).communicate()[0].decode("utf-8"))

ps = str(subprocess.Popen(['ls -l /sys/class/net/'], stdout=subprocess.PIPE, shell=True).communicate()[0].decode("utf-8"))
processes = ps.split('\n')
processes.pop(0)
processes.pop(-1)
pysical_adapters = []
for line in processes:
    if 'virtual' not in line:
        pysical_adapters.append(line.split()[8])

with open('/proc/' + 'net/dev', 'r') as reader:
    file = reader.read()
lines = file.splitlines()

adapter_info = []
for line in lines:
    for adapter in pysical_adapters:
        if adapter in line:
            adapter_info.append(line.split())

max_connection_speed = []
for adapter in pysical_adapters:
    if 'wlan' not in adapter:
        ps = str(subprocess.Popen(['ethtool ' + adapter + ' | grep -i speed'], stdout=subprocess.PIPE, shell=True).communicate()[0].decode("utf-8"))
        processes = ps.split('\n')
        processes.pop(-1)
        max_connection_speed.append(processes[-1].replace('\tSpeed: ', ''))
