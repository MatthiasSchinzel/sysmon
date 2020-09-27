import subprocess

ps = str(subprocess.Popen(['ps', 'aux', '--sort=-pcpu'], stdout=subprocess.PIPE).communicate()[0])
processes = ps.split('\\n')
processes.pop(0)
processes.pop(-1)
process = []
for cur_process in processes:
    process.append([j for j in cur_process.split(maxsplit = 10)])

process[400]
