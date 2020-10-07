<p align="center" style="font-size:30px">

</p>
<p align="center" style="font-size:30px">
  <br>
  <img src="media/output.gif" align="center">
  <em>Linux activity monitor</em>
  <br>
</p>
<p align="center">
<a href="https://github.com/MatthiasSchinzel/CaRL/graphs/commit-activity">
    <img src="https://img.shields.io/badge/Maintained%3F-yes-green.svg">
</a>
<a href="https://github.com/MatthiasSchinzel/CaRL/blob/master/LICENSE">
    <img src="https://img.shields.io/github/license/MatthiasSchinzel/CaRL.svg">
</a>
<a href="https://github.com/MatthiasSchinzel/CaRL/tags/">
    <img src="https://img.shields.io/github/v/tag/MatthiasSchinzel/CaRL.svg?sort=semver">
</a>
<a href="https://github.com/MatthiasSchinzel">
    <img src="https://img.shields.io/badge/Need%20help%3F-Ask-27B89C">
</a>
<a href="https://github.com/MatthiasSchinzel">
    <img src="https://img.shields.io/badge/Car-Reinforcement%20Learning-red">
</a>
</p>
<p align="center">
  <a href="#key-features">Key Features</a> •
  <a href="#getting-started">Getting Started</a>
</p>

<img src="media/optimized.gif" align="center">  
<h2>
Key features
</h2>

[![forthebadge made-with-python](http://ForTheBadge.com/images/badges/made-with-python.svg)](https://www.python.org/)


Graphical visualization of the following data

* Running processes overview

* CPU utilization and per core clock speed

* GPU utilization and clock speed (so far only Nvidia). Should work with multiple GPUs (not tested)

* Memory and Swap utilization

* Network utilization (Wlan and Ethernet). Wlan link bandwidth is constantly updated.

* HDD/SSD utilization.


<h2>
Getting Started
</h2>

I wanted to have a graphical visualization of the load of most physical devices. The system monitor in ubuntu does a great job, but is not displaying HDD and SDD load as well as no GPU load. This tools brings all the information together to one place, similar to the task manager in windows.

### 1. Installation and run

Dependencies (Python 3):
```
pip install pyqtgraph, pyqt5
```
clone the project and cd into it. Then
```
python sysmon.py
```

If you want to monitor your Nvidia GPU, nvidia-smi has to be installed.

### 2. Data origin

Most data comes from the /proc directory.

In more detail:
* CPU: /proc/cpuinfo and /proc/stat
* Memory: /proc/meminfo
* Disks: /proc/diskstats
* Network: /proc/net/dev and ethtool(Ethernet)/iwconfig(Wlan)
* GPU: nviida-smi (if Nvidia GPU)
* Processes: 'ps -aux'

I this choice of data source makes the program usable across multiple linux distributions. (Only tested on Ubuntu 18.04 and 20.04)

### 3. To do

* Include support for Intel and AMD GPUs. I don't have any of these GPUs, so unfortunately I can't test it. Maybe I can get my hands on any of these GPUs in the future.

* Add more information about Wlan connection. (Signal strength etc.)

* Add more GPU infortmation (Process overview)

* Add dark mode

* Add GUI menu to modify parameters such as update interval, capture period
