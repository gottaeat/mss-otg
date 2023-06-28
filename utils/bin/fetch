#!/usr/bin/python
import re
import os
import socket
import datetime

# colors
c_res='\033[0;39m'
cb_red='\033[1;31m'
cb_blu='\033[1;34m'
cb_whi='\033[1;37m'

# distro
osrel_data = open('/etc/os-release', 'rb')
osrel = osrel_data.read().decode().split('\n')
osrel_data.close()

if osrel[-1] == '': osrel = osrel[:-1]
if osrel[0] == '': osrel = osrel[1:]

osrel_parsed = {}
for i in osrel:
    i = i.split('=')
    osrel_parsed[i[0]] = re.sub(r'\'|\"', '', i[1])

distro = osrel_parsed['PRETTY_NAME'].lower()

# host
hostname = socket.gethostname()

# kernel
kernel = os.uname().release

# cpu
cpu_data = open('/proc/cpuinfo', 'r')

model_name = ''
for line in cpu_data.readlines():
    if 'model name' in line:
        model_name = line.split('\t: ')[1].rstrip('\n')
        break

cpu_data.close()

cpuname = re.sub(r'with.*|@.*|AMD|Intel|\(R\)|\(TM\)|CPU|Processor|.-Core|..-Core',
                 '', model_name).strip(' ').lower()

while '  ' in cpuname:
    cpuname = re.sub(r'  ', ' ', cpuname)

cpucores = str(len(os.sched_getaffinity(0)))
cpu = f"{cpuname} ({cpucores})"

# mem
def memstrip(line):
    return int(line.split(':')[1].lstrip(' ').rstrip(' kB\n'))

mem_data = open('/proc/meminfo', 'r')
memlines = mem_data.readlines()
mem_data.close()

memfull = {}
for i in range(0, len(memlines)):
    isplit = memlines[i].split(':')
    memfull[isplit[0]] = int(isplit[1].lstrip(' ').rstrip(' kB\n'))

memtotal = int(memfull['MemTotal'] / 1024)
memavail = int(memfull['MemAvailable'] / 1024)
memfree  = int(memfull['MemFree'] / 1024)
memcache = int((memfull['Cached'] + memfull['Buffers'] + memfull['SReclaimable']) / 1024)
mem = f"{memavail}/{memtotal}m ({memfree}+{memcache})"

# uptime
uptime_data = open('/proc/uptime', 'r')
uptime = datetime.timedelta(seconds=int(float(uptime_data.read().split(' ')[0])))

# final
finmsg  = f" {cb_whi}→ {cb_red}host   {cb_blu}:{c_res} {hostname}\n"
finmsg += f" {cb_whi}→ {cb_red}os     {cb_blu}:{c_res} {distro}\n"
finmsg += f" {cb_whi}→ {cb_red}kernel {cb_blu}:{c_res} {kernel}\n"
finmsg += f" {cb_whi}→ {cb_red}cpu    {cb_blu}:{c_res} {cpu}\n"
finmsg += f" {cb_whi}→ {cb_red}mem    {cb_blu}:{c_res} {mem}\n"
finmsg += f" {cb_whi}→ {cb_red}uptime {cb_blu}:{c_res} {uptime}\n"

print(finmsg,end='')
