#!/usr/bin/python3
# pylint: disable=bare-except
# pylint: disable=inconsistent-return-statements
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=missing-module-docstring

import json
import os
import platform
import re
import socket
import ssl
import sys
import time
import urllib.parse
import urllib.request


# - - utils - - #
def get_url(
    url, headers={}, tls_context=None
):  # pylint: disable=dangerous-default-value
    # set useragent
    headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    headers["User-Agent"] += "AppleWebKit/537.36 (KHTML, like Gecko) "
    headers["User-Agent"] += "Chrome/126.0.0.0 Safari/537.36"

    request = urllib.request.Request(
        url,
        headers=headers,
    )

    # get response
    if tls_context:
        response = urllib.request.urlopen(
            request, context=tls_context
        )  # pylint: disable=consider-using-with
    else:
        response = urllib.request.urlopen(  # pylint: disable=consider-using-with
            request
        )

    # - - content-type - - #
    content_type = response.getheader("Content-Type")

    if not content_type:
        response.close()
        raise ValueError("Content-Type header was not found")

    content_type = content_type.split(";")

    # check if we take the mimetype
    mimetype = content_type[0]

    if mimetype not in (
        "application/javascript",
        "application/json",
        "application/xml",
        "text/html",
        "text/javascript",
    ):
        response.close()
        raise ValueError(f'"{mimetype}" is not an accepted mimetype')

    # check if charset was specified
    try:
        charset = content_type[1].split("charset=")[1]
    except IndexError:
        charset = "utf-8"

    # - - content-length - - #
    content_length = response.getheader("Content-Length")
    max_size = 1024 * 1024 * 5

    if content_length:
        if int(content_length) > max_size:
            response.close()
            content_size = content_length / 1024 / 1024
            raise ValueError(f"file is larger than 5MB ({content_size})")

    # read data
    data = response.read(max_size + 1)
    response.close()

    if len(data) > max_size:
        raise ValueError("file is larger than 5MB")

    if len(data) == 0:
        raise ValueError("empty data returned")

    # decode data
    try:
        data = data.decode(encoding=charset)
    except:
        try:
            data = data.decode(encoding="utf-8")
        except UnicodeDecodeError:
            data = data.decode(encoding="latin-1")

    return data


# - - mpd client - - #
class MPD:  # pylint: disable=too-few-public-methods
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

        if not daemon_status[0]:
            return daemon_status[1]

        status = self._parse(self._query("status\n"))

        if status["state"] == "stop":
            return "idle"

        cursong = self._parse(self._query("currentsong\n"))

        if len(cursong) == 0:
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


def module_mpd():
    return MPD("localhost", 6600).run()


# - - scrape modules - - #
def module_mgm(area):
    context = ssl.create_default_context()
    context.options |= 0x4

    try:
        data = get_url(
            f"https://servis.mgm.gov.tr/web/sondurumlar?merkezid={area}",
            {"Origin": "https://mgm.gov.tr"},
            context,
        )
    except:
        return "GET failed"

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

        return f"{temp} {code} {wind} {rain}"
    except:
        return "parse failed"


def module_yahoo():
    try:
        data = get_url("https://query1.finance.yahoo.com/v8/finance/chart/USDTRY=X")
    except:
        return "GET failed"

    try:
        return json.loads(data)["chart"]["result"][0]["meta"]["regularMarketPrice"]
    except:
        return "parse failed"


def module_binance():
    try:
        data = get_url("https://api.binance.com/api/v3/ticker/price?symbol=USDTTRY")
    except:
        return "GET failed"

    try:
        return float(json.loads(data)["price"].rstrip("0"))
    except:
        return "parse failed"


# - - tmpfs modules - - #
def module_mem():
    with open("/proc/meminfo", "r", encoding="utf-8") as f:
        for line in f.readlines():
            if "MemAvailable" in line:
                mem_info = f"{int(int(line.split()[1]) / 1024)}m"
                break

    return mem_info


def module_temp():
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

    if tempfile:
        with open(tempfile, "r", encoding="utf-8") as f:
            return f"{int(int(f.read()) / 1000)}c"

    return "no tempfile"


def module_ibmfan():
    rpm, level = "", ""
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


def module_battery():
    bat0_path = "/sys/class/power_supply/BAT0"

    if not os.path.exists(f"{bat0_path}/status"):
        return "nb"

    try:
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
    except FileNotFoundError:
        return "nb"

    return f"{bat_stat}{bat_cap}"


def module_bandwidth():
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

    try:
        with open(rx_path, "r", encoding="utf-8") as f:
            rx_before = int(f.read())

        with open(tx_path, "r", encoding="utf-8") as f:
            tx_before = int(f.read())

        time.sleep(1)

        with open(rx_path, "r", encoding="utf-8") as f:
            rx_after = int(f.read())

        with open(tx_path, "r", encoding="utf-8") as f:
            tx_after = int(f.read())
    except FileNotFoundError:
        return "no conn"

    rx_rate = int((rx_after - rx_before) / 1024)
    tx_rate = int((tx_after - tx_before) / 1024)

    rx_total = int(rx_after / (1024**2))
    tx_total = int(tx_after / (1024**2))

    return f"{iface} {rx_rate}↓↑{tx_rate} [{rx_total}+{tx_total}]"


# - - misc modules - - #
def module_date():
    return time.strftime("%a %d %H:%M:%S")


def module_loadavg():
    return f"{os.getloadavg()[0]:.2f}"


# - - handlers - - #
IBMFAN_PATH = "/proc/acpi/ibm/fan"
MODULE_LIST = {
    "mpd": module_mpd,
    "mgm": module_mgm,
    "yahoo": module_yahoo,
    "binance": module_binance,
    "mem": module_mem,
    "temp": module_temp,
    "ibmfan": module_ibmfan,
    "battery": module_battery,
    "bandwidth": module_bandwidth,
    "date": module_date,
    "loadavg": module_loadavg,
}


def handle_tmux():
    p_set = "#[fg=white bg=black]"
    p_reset = "#[default]"
    p_block = f"{p_reset} {p_set}"

    finprint = f"{p_set} "
    if platform.system() == "Linux":
        finprint += f"{module_mpd()} {p_block} "
        finprint += f"{module_date()} {p_block} "
        finprint += f"{module_loadavg()} {module_mem()} {p_block} "
        finprint += f"{module_battery()}"
    else:
        finprint += f"{module_date()} {p_block} {module_loadavg()}"

    return finprint


def handle_modules(args):
    try:
        if args[0] in MODULE_LIST:
            if args[0] == "mgm":
                try:
                    return print(MODULE_LIST["mgm"](args[1]))
                except IndexError:
                    print("mgm module requires an area code")
                    sys.exit(1)
            return print(MODULE_LIST[args[0]]())
    except IndexError:
        print("must specify a module name")
        sys.exit(1)

    print(f"module {args[0]} does not exist")
    sys.exit(1)


# - - action - - #
def help_prompt():
    print("statusbar.py {module <module> <module_args>|tmux}")
    sys.exit(1)


def run():
    args = sys.argv[1:]

    if not args or args[0] not in ["module", "tmux"]:
        help_prompt()

    if args[0] == "tmux":
        return print(handle_tmux())

    if args[0] == "module":
        return handle_modules(args[1:])

    help_prompt()


if __name__ == "__main__":
    run()
