#!/usr/bin/python
# pylint: disable=missing-module-docstring,missing-class-docstring,missing-function-docstring
# pylint: disable=invalid-name
# pylint: disable=too-few-public-methods
# pylint: disable=bare-except
import argparse
import json
import os
import re
import socket
import ssl
import sys
import time
import urllib.parse
import urllib.request

from threading import Thread


# mpd
class MPD:
    def __init__(self, mpd_host, mpd_port):
        self._address = (socket.gethostbyname(mpd_host), mpd_port)

    def _check_status(self):
        try:
            check = socket.socket()
            check.connect(self._address)
        except ConnectionRefusedError:
            return (False, "dead")

        mpd_check = check.recv(1024).decode()
        if "OK MPD" in mpd_check:
            status = (True, "alive")
        else:
            status = (False, "not MPD")

        check.close()
        return status

    def _query(self, query):
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(self._address)
        client.send(query.encode())

        sockfile = client.makefile(mode="r")

        raw = ""
        while True:
            line = sockfile.readline()

            if "OK MPD " in line:
                continue
            if line == "\r\n":
                continue
            if "OK\n" in line:
                break

            raw += line

        client.close()

        querylist = raw.split("\n")
        querylist.remove("")

        return querylist

    @staticmethod
    def _parse(response):
        final = {}
        for line in response:
            data = line.split(":", maxsplit=1)
            final[data[0]] = data[1].lstrip()

        return final

    def run(self):
        daemon_status = self._check_status()

        if daemon_status[0] is not True:
            return daemon_status[1]

        status = self._parse(self._query("status\n"))
        cursong = self._parse(self._query("currentsong\n"))

        if len(cursong) == 0:
            return "idle"

        if cursong["volume"] == "n/a":
            return "idle"

        songname = cursong.get("Title", re.sub(r"^.*\/|\.[^.]*$", "", cursong["file"]))

        if len(songname) >= 20:
            songname = songname[0:17] + "..."

        if status["state"] == "pause":
            indic = "[#]"
        else:
            cur_dur = float(cursong["duration"]) - float(status["elapsed"])

            if cur_dur >= 3600:
                timeshit = "%H:%M:%S"
            else:
                timeshit = "%M:%S"

            indic = f"[{time.strftime(timeshit, time.gmtime(cur_dur))}]"

        return f"{indic} {songname}"


# scrape
class Scrape:
    def __init__(self, area):
        self.area = area
        self.mgm = "cookin"
        self.yahoo = "cookin"
        self.binance = "cookin"

    def get_mgm(self):
        context = ssl.create_default_context()
        context.options |= 0x4

        url = "https://servis.mgm.gov.tr/web/sondurumlar?"
        params = urllib.parse.urlencode({"merkezid": self.area})

        req = url + params
        headers = {"Origin": "https://mgm.gov.tr"}

        req = urllib.request.Request(req, headers=headers)

        while True:
            try:
                with urllib.request.urlopen(req, context=context) as f:
                    data = f.read().decode()
            except urllib.request.HTTPError as e:
                self.mgm = f"HTTP {e.code}"
                time.sleep(err_sleep)
            except urllib.error.URLError as e:
                self.mgm = f"URL {e.reason.errno}"
                time.sleep(err_sleep)
            except:
                self.mgm = "Error"
                time.sleep(err_sleep)
            else:
                try:
                    data = json.loads(data)[0]
                    code = data["hadiseKodu"]
                    temp = data["sicaklik"]
                    wind = data["ruzgarHiz"]
                    rain = data["yagis00Now"]

                    temp = f"{temp}°" if str(temp) != "-9999" else "n/a"
                    code = code.lower() if str(code) != "-9999" else "n/a"
                    wind = f"{wind:.1f}km/h" if str(wind) != "-9999" else "n/a"
                    rain = f"{rain}mm" if str(rain) != "-9999" else "n/a"

                    self.mgm = f"{temp} {code} {wind} {rain}"
                except:
                    self.mgm = "Parse Error"
                    time.sleep(err_sleep)
                else:
                    time.sleep(interval)

    def get_yahoo(self):
        url = "https://query1.finance.yahoo.com/v8/finance/chart/"
        params = urllib.parse.urlencode({"USDTRY": "X"})
        req = url + params

        while True:
            try:
                with urllib.request.urlopen(req) as f:
                    data = f.read().decode()
            except urllib.request.HTTPError as e:
                self.yahoo = f"HTTP {e.code}"
                time.sleep(err_sleep)
            except urllib.error.URLError as e:
                self.yahoo = f"URL {e.reason.errno}"
                time.sleep(err_sleep)
            except:
                self.yahoo = "Error"
                time.sleep(err_sleep)
            else:
                try:
                    self.yahoo = json.loads(data)["chart"]["result"][0]["meta"][
                        "regularMarketPrice"
                    ]
                except:
                    self.yahoo = "Parse Error"
                    time.sleep(err_sleep)
                else:
                    time.sleep(interval)

    def get_binance(self):
        url = "https://api.binance.com/api/v3/ticker/price?"
        params = urllib.parse.urlencode({"symbol": "USDTTRY"})
        req = url + params

        while True:
            try:
                with urllib.request.urlopen(req) as f:
                    data = f.read().decode()
            except urllib.request.HTTPError as e:
                self.binance = f"HTTP {e.code}"
                time.sleep(err_sleep)
            except urllib.error.URLError as e:
                self.binance = f"URL {e.reason.errno}"
                time.sleep(err_sleep)
            except:
                self.binance = "Error"
                time.sleep(err_sleep)
            else:
                try:
                    self.binance = float(json.loads(data)["price"].rstrip("0"))
                except:
                    self.binance = "Parse Error"
                    time.sleep(err_sleep)
                else:
                    time.sleep(interval)


# procfs
IBMFAN_PATH = "/proc/acpi/ibm/fan"


def get_loadavg():
    return f"{os.getloadavg()[0]:.2f}"


def get_mem():
    with open("/proc/meminfo", "r", encoding="utf-8") as f:
        for line in f.readlines():
            if "MemAvailable" in line:
                mem_info = f"{int(int(line.split()[1]) / 1024)}m"
                break

    return mem_info


def get_temp():
    hwmon_dir = "/sys/class/hwmon/"
    labels = ["Tctl", "Package", "Core 0"]

    tempfile_list, tempfile = [], None
    for d in os.listdir(hwmon_dir):
        for file in os.listdir(hwmon_dir + d):
            fullpath = f"{hwmon_dir}{d}/{file}"
            if "_label" in fullpath:
                tempfile_list.append(fullpath)

    for _, file in enumerate(tempfile_list):
        with open(file, "r", encoding="utf-8") as f:
            f_contents = re.sub(r"\n", "", f.read())
        if any(label in f_contents for label in labels):
            tempfile = re.sub(r"label", "input", file)
            break

    if tempfile is None:
        return None

    with open(tempfile, "r", encoding="utf-8") as f:
        return f"{int(int(f.read()) / 1000)}c"


def get_ibmfan():
    with open(IBMFAN_PATH, "r", encoding="utf-8") as f:
        for line in f.readlines():
            if "speed:" in line:
                rpm = line.split()[1]
            if "level:" in line:
                level = line.split()[1]

    if level == "disengaged":
        level = "d"

    if level == "auto":
        level = "a"

    return f"{rpm}/{level}"


def get_battery():
    bat0_path = "/sys/class/power_supply/BAT0"

    if not os.path.exists(f"{bat0_path}/status"):
        return "nb"

    with open(f"{bat0_path}/capacity", "r", encoding="utf-8") as f:
        bat_cap = "%" + re.sub(r"\n", "", f.read())

    with open(f"{bat0_path}/status", "r", encoding="utf-8") as f:
        bat_stat = f.readline().strip("\n")

    if bat_stat == "Discharging":
        bat_stat = "d"
    elif bat_stat == "Not charging":
        bat_stat = "n"
    else:
        bat_stat = "c"

    return f"{bat_stat}{bat_cap}"


def get_bandwidth():
    iface = None
    with open("/proc/net/route", "r", encoding="utf-8") as f:
        for line in f.readlines():
            line = line.strip().split()
            if line[1] == "00000000":
                iface = line[0]
                break

    if iface is None:
        time.sleep(1)
        return "no conn"

    rx_path = f"/sys/class/net/{iface}/statistics/rx_bytes"
    tx_path = f"/sys/class/net/{iface}/statistics/tx_bytes"

    with open(rx_path, "r", encoding="utf-8") as f:
        rx_before = int(f.read())

    with open(tx_path, "r", encoding="utf-8") as f:
        tx_before = int(f.read())

    time.sleep(1)

    with open(rx_path, "r", encoding="utf-8") as f:
        rx_after = int(f.read())

    with open(tx_path, "r", encoding="utf-8") as f:
        tx_after = int(f.read())

    rx_rate = int((rx_after - rx_before) / 1024)
    tx_rate = int((tx_after - tx_before) / 1024)

    rx_total = int(rx_after / (1024**2))
    tx_total = int(tx_after / (1024**2))

    return f"{iface} {rx_rate}↓↑{tx_rate} [{rx_total}+{tx_total}]"


def get_date():
    return time.strftime("%a %d %H:%M:%S")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Statusbar generator for tmux and X11")
    subparsers = parser.add_subparsers(dest="command", required=True)

    tmux = subparsers.add_parser(
        "tmux", help="Print in the tmux specific format, without a loop"
    )
    tmux.add_argument("--host", type=str, default="localhost", help="MPD host")
    tmux.add_argument("--port", type=int, default=6600, help="MPD port")

    x11 = subparsers.add_parser("x11", help="Call xsetroot, run in a loop")
    x11.add_argument("--area", type=int, required=True, help="MGM area code")
    x11.add_argument(
        "--interval", default=60, help="Interval that the APIs should be queried at"
    )
    x11.add_argument("--host", type=str, default="localhost", help="MPD host")
    x11.add_argument("--port", type=int, default=6600, help="MPD port")
    x11.add_argument(
        "--debug",
        action="store_true",
        help="Print to the stdout instead of calling xsetroot",
    )

    args = parser.parse_args()

    if args.command == "x11":
        interval = args.interval
        host = args.host
        port = args.port

        err_sleep = 10
        scrape = Scrape(args.area)

        threads = []
        mgm_thread = Thread(target=scrape.get_mgm, daemon=True)
        threads.append(mgm_thread)

        yahoo_thread = Thread(target=scrape.get_yahoo, daemon=True)
        threads.append(yahoo_thread)

        binance_thread = Thread(target=scrape.get_binance, daemon=True)
        threads.append(binance_thread)

        for job in threads:
            job.start()

        while True:
            finprint = '"'
            finprint += f" {get_bandwidth()}"
            finprint += f" ¦ {get_loadavg()} {get_mem()} {get_temp()}"

            if os.path.isfile(IBMFAN_PATH):
                finprint += f"/{get_battery()} {get_ibmfan()}"

            finprint += f" ¦ {scrape.mgm} ¦ {scrape.yahoo}/{scrape.binance}"
            finprint += f" ¦ {MPD(args.host, args.port).run()}"
            finprint += f" ¦ {get_date()}"
            finprint += '"'

            if args.debug is True:
                sys.stdout.write("\x1b[1A\x1b[2K")
                print(finprint)
            else:
                os.popen(f"xsetroot -name {finprint}")

    if args.command == "tmux":
        p_set, p_reset = "#[fg=white bg=black]", "#[default]"
        p_block = f"{p_reset} {p_set}"

        finprint = f"{p_set} {MPD(args.host, args.port).run()} {p_block} "
        finprint += f"{get_date()} {p_block} "
        finprint += f"{get_loadavg()} {get_mem()} {p_block} "
        finprint += f"{get_battery()} {p_reset} "

        print(finprint)
