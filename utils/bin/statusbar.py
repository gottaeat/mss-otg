#!/usr/bin/python
#statusbar.py
#Copyright (C) 2023 gottaeat
#
#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with this program.  If not, see <http://www.gnu.org/licenses/>.

import argparse
import socket
import ssl
from os        import popen, getloadavg, listdir, path
from os.path   import exists
from sys       import stdout, argv
from re        import sub
from time      import sleep, strftime, gmtime
from json      import loads
from threading import Thread

# 1 > vars
# 1.1 > parse inputs
parser = argparse.ArgumentParser(description='statusbar for x11 and tmux.')
parser.add_argument('--tmux', action = 'store_true')
parser.add_argument('--debug', action = 'store_true')
parser.add_argument('--host', type = str, default = 'localhost')
parser.add_argument('--port', type = int, default = 6600)

tmux = parser.parse_known_args()[0].tmux

if not tmux:
    parser.add_argument('--area', type = str, required = True)
    parser.add_argument('--interval', type = int, default = 60)

args = parser.parse_args()

if not tmux:
    area = args.area
    interval = args.interval

debug = args.debug

if debug and tmux:
    raise Exception("tmux and debug args cannot be set at the same time.")

# 1.2 > tmux escapes
cs, cr = '#[fg=white bg=black]', '#[default]'
cc = cr + ' ' + cs

# 1.3 > set address for mpd
host = socket.gethostbyname(args.host)
port = args.port
address = (host, port)

# 1.4 > mgm
if not tmux:
    mgmhost = 'servis.mgm.gov.tr'
    mgmreq  = '/web/sondurumlar?merkezid=' + area
    mgmget  = 'GET ' + mgmreq + ' HTTP/1.1\r\n'
    mgmget += 'Host: servis.mgm.gov.tr\r\n'
    mgmget += 'Origin: https://mgm.gov.tr\r\n'
    mgmget += '\r\n'

# 1.5 > pseudofs paths
bat0_path = '/sys/class/power_supply/BAT0/'
meminfo_path = '/proc/meminfo'
route_path = '/proc/net/route'

if not tmux:
    hwmonfile_path = '/sys/class/hwmon/'
    ibmfan_path = '/proc/acpi/ibm/fan'
    is_thinkpad =  path.isfile(ibmfan_path)

# 1.6 > find file to read the package temp for the cpu from
if not tmux:
    tempfile_list = []

    for dirs in listdir(hwmonfile_path):
        for i in listdir(hwmonfile_path + dirs):
            fulltemp_path = hwmonfile_path + dirs + '/' + i
            if "_label" in fulltemp_path:
                tempfile_list.append(fulltemp_path)

    labels = ['Tctl', 'Package', 'Core 0']

    for i in range(0, len(tempfile_list)):
       tmpread = open(tempfile_list[i])
       tmpread_contents = sub(r"\n", "", tmpread.read())
       tmpread.close()

       if any([label in tmpread_contents for label in labels]):
           final_tempfile = sub(r"label", "input", tempfile_list[i])
           break
       else:
           final_tempfile = None

# 2 > funcs
# 2.1 > applet funcs
def mpdcheck():
    try:
        check = socket.socket()
        check.connect(address)
    except ConnectionRefusedError:
        return False # dead
    else:
        mpdcheck = check.recv(1024).decode()
        check.close()

        if 'OK MPD' in mpdcheck:
            return True # alive
        else:
            return False # not mpd

def mpdparse(response):
    final = {}
    for line in response:
        data = line.split(':', maxsplit=1)
        final[data[0]] = data[1].lstrip()

    return final

def mpdquery(query):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(address)
    client.send(query.encode())

    sockfile = client.makefile(mode='r')

    raw = ""
    while True:
        line = sockfile.readline()

        if "OK MPD " in line:
            continue
        if line == '\r\n':
            continue
        elif "OK\n" in line:
            break
        else:
            raw += line

    client.close()

    querylist = raw.split('\n')
    querylist.remove('')
    return querylist

# 2.2 > applets
def sb_mpd():
    if mpdcheck():
        status  = mpdparse(mpdquery('status\n'))
        cursong = mpdparse(mpdquery('currentsong\n'))
 
        if len(cursong) == 0:
             return 'idle'
        else:
            if 'Title' in cursong.keys():
                songname = cursong['Title']
            else:
                songname = sub(r"^.*\/|\.[^.]*$", "", cursong['file'])
 
            if len(songname) >= 20:
                songname = songname[0:17] + "..."
 
            if status['state'] == 'pause':
                indic = '[#]'
            else:
                cur_dur = float(cursong['duration']) - float(status['elapsed'])

                if cur_dur >= 3600:
                     timeshit = '%H:%M:%S'
                else:
                     timeshit = '%M:%S'
 
                indic = f"[{strftime(timeshit, gmtime(cur_dur))}]"

            return f"{indic} {songname}"
    else:
        return 'ded'

def sb_dat():
    return strftime("%a %d %H:%M:%S")

def sb_lavg():
    return "{:.2f}".format(getloadavg()[0])

def sb_mem():
    mem_data = open(meminfo_path, 'r')

    for line in mem_data.readlines():
        if 'MemAvailable' in line:
            final_mem = f"{int(int(line.split()[1]) / 1024)}m"

    mem_data.close()

    return final_mem

def sb_temp():
    if final_tempfile is None:
        temp_formatted = None
    else:
        temp_data  = open(final_tempfile)
        temp_formatted = f"{int(int(temp_data.read()) / 1000)}c"
        temp_data.close()

    return temp_formatted

def sb_ibmfan():
    try:
        ibmfan_data = open(ibmfan_path, 'r')
    except FileNotFoundError:
        return None
    else:
        for line in ibmfan_data.readlines():
            if 'speed:' in line:
                rpm = line.split()[1]
            elif 'level:' in line:
               level = line.split()[1]

    ibmfan_data.close()

    if level == 'disengaged':
        level = 'd'
    elif level == 'auto':
        level = 'a'

    return f"{rpm}/{level}"

def sb_weather():
    global weat
    weat = 'cookin'

    while True:
        context = ssl.create_default_context()
        context.options |= 0x4

        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        clienttls = context.wrap_socket(socket.socket(socket.AF_INET,
                                                      socket.SOCK_STREAM),
                                        server_side = False,
                                        server_hostname = mgmhost)

        try:
            mgmip = socket.gethostbyname(mgmhost)
        except:
            weat = 'no conn'
            sleep(10)
        else:
            clienttls.connect((mgmip, 443))
            clienttls.send(mgmget.encode())

            data = clienttls.recv(1024)
            cutat = int(data.decode().find('\r\n\r\n')) + 4
            data = loads(data[cutat:])[0]

            coderaw, tempraw, windraw, rainraw = (data['hadiseKodu'],
                                                  data['sicaklik'],
                                                  data['ruzgarHiz'],
                                                  data['yagis00Now'])

            temp = f"{tempraw}°" if str(tempraw) != "-9999" else "n/a"
            code = coderaw.lower() if str(coderaw) != "-9999" else "n/a"
            wind = "{:.1f}km/h".format(windraw) if str(windraw) != "-9999" else "n/a"
            rain = f"{rainraw}mm" if str(rainraw) != "-9999" else "n/a"
 
            weat = f"{temp} {code} {wind} {rain}"

            sleep(interval)

def sb_bw():
    iface = ''
    gway_data = open(route_path, 'r')

    for line in gway_data.readlines():
        mod_line = line.strip().split()
        if mod_line[1] == '00000000':
            iface = mod_line[0]

    gway_data.close()

    if len(iface) == 0:
        sleep(1)
        return "no conn"
    else:
        rxstatpath = "/sys/class/net/" + iface + "/statistics/rx_bytes"
        txstatpath = "/sys/class/net/" + iface + "/statistics/tx_bytes"

        rx_f = open(rxstatpath, "r"); rx1 = int(rx_f.read()); rx_f.seek(0)
        tx_f = open(txstatpath, "r"); tx1 = int(tx_f.read()); tx_f.seek(0)

        for i in rx_f, tx_f: i.seek(0)

        sleep(1)

        rx2 = int(rx_f.read()); tx2 = int(tx_f.read())
        kb_rx = int((rx2 - rx1) / 1024); kb_tx = int((tx2 - tx1) / 1024)
        t_rx  = int(rx2 / 1048576); t_tx  = int(tx2 / 1048576)

        return f"{iface} {kb_rx}↓↑{kb_tx} [{t_rx}+{t_tx}]"

def sb_bat():
    if exists(bat0_path + "status"):
        batcap_f = open(bat0_path + "capacity", "r")
        batcap = "%" + sub(r"\n", "", batcap_f.read())
        batcap_f.close()

        batstat_f = open(bat0_path + "status", "r")
        batstat_d = batstat_f.readline().strip('\n')

        if batstat_d == "Discharging":
            batstat = "d"
        elif batstat_d == "Not charging":
            batstat = "n"
        else:
            batstat = "c"

        batstat_f.close()

        return f"{batstat}{batcap}"
    else:
        return "nb"

# 3 > action
# 3.1 > printing methods
def setroot_print(status):
    popen("xsetroot -name " + status)

def debug_print(status):
    stdout.write('\x1b[1A\x1b[2K')
    print(status)

def tmux_print(status):
    print(status)

if debug:
    print_method = debug_print
elif tmux:
    print_method = tmux_print
else:
    print_method = setroot_print

def main():
    if tmux:
        finprint  = f"{cs} {sb_mpd()} {cc} {sb_dat()} {cc} "
        finprint += f"{sb_lavg()} {sb_mem()} {cc} {sb_bat()} {cr} "

        print_method(finprint)
    else:
        while True:
            finprint  = f"\" {sb_bw()} ¦ {sb_lavg()} {sb_mem()} {sb_temp()}"

            if is_thinkpad: finprint += f"/{sb_ibmfan()} {sb_bat()}"

            finprint += f" ¦ {weat} ¦ {sb_mpd()} ¦ {sb_dat()} \""

            print_method(finprint)

# 3.2 > separate thread for weather, 
weather_thread = Thread(target=sb_weather)
weather_thread.daemon = True
weather_thread.start()

# 3.3 > reddit
if __name__ == "__main__":
    main()
