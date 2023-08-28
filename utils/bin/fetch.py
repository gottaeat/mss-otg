#!/usr/bin/python3
# pylint: disable=missing-module-docstring,missing-function-docstring
import re
import os
import socket
import datetime


# pylint: disable=missing-class-docstring,too-few-public-methods
class Colors:
    C_RES = "\033[0;39m"
    C_RED = "\033[1;31m"
    C_BLU = "\033[1;34m"
    C_WHI = "\033[1;37m"

    def __init__(self):
        pass


# pylint: disable=too-many-instance-attributes
class Fetch:
    def __init__(self):
        self.distro = None
        self.hostname = None
        self.kernel = None
        self.cpuname = None
        self.cpucores = None
        self.memtotal = None
        self.memavail = None
        self.memfree = None
        self.memcache = None
        self.uptime = None

    def _get_distro(self):
        # pylint: disable=invalid-name
        with open("/etc/os-release", "r", encoding="utf-8") as f:
            osrel = f.read().split("\n")

        if osrel[-1] == "":
            osrel = osrel[:-1]
        if osrel[0] == "":
            osrel = osrel[1:]

        osrel_parsed = {}
        for i in osrel:
            i = i.split("=")
            osrel_parsed[i[0]] = re.sub(r"\'|\"", "", i[1])

        self.distro = osrel_parsed["PRETTY_NAME"].lower()

    def _get_hostname(self):
        self.hostname = socket.gethostname()

    def _get_kernel(self):
        self.kernel = os.uname().release

    def _get_cpu(self):
        # pylint: disable=invalid-name
        with open("/proc/cpuinfo", "r", encoding="utf-8") as f:
            model_name = ""
            for line in f.readlines():
                if "model name" in line:
                    model_name = line.split("\t: ")[1].rstrip("\n")
                    break

        cpuname = (
            re.sub(
                r"with.*|@.*|AMD|Intel|\(R\)|\(TM\)|CPU|Processor|.-Core|..-Core",
                "",
                model_name,
            )
            .strip(" ")
            .lower()
        )

        while "  " in cpuname:
            cpuname = re.sub(r"  ", " ", cpuname)

        self.cpuname = cpuname
        self.cpucores = str(len(os.sched_getaffinity(0)))

    @staticmethod
    def _memstrip(line):
        return int(line.split(":")[1].lstrip(" ").rstrip(" kB\n"))

    def _get_mem(self):
        # pylint: disable=invalid-name
        with open("/proc/meminfo", "r", encoding="utf-8") as f:
            memlines = f.readlines()

        memfull = {}
        for _, line in enumerate(memlines):
            isplit = line.split(":")
            memfull[isplit[0]] = int(isplit[1].lstrip(" ").rstrip(" kB\n"))

        self.memtotal = int(memfull["MemTotal"] / 1024)
        self.memavail = int(memfull["MemAvailable"] / 1024)
        self.memfree = int(memfull["MemFree"] / 1024)
        self.memcache = int(
            (memfull["Cached"] + memfull["Buffers"] + memfull["SReclaimable"]) / 1024
        )

    def _get_uptime(self):
        # pylint: disable=invalid-name
        with open("/proc/uptime", "r", encoding="utf-8") as f:
            self.uptime = datetime.timedelta(seconds=int(float(f.read().split(" ")[0])))

    def collect(self):
        self._get_distro()
        self._get_hostname()
        self._get_kernel()
        self._get_cpu()
        self._get_mem()
        self._get_uptime()


if __name__ == "__main__":
    fetch = Fetch()
    fetch.collect()

    distro = fetch.distro
    hostname = fetch.hostname
    kernel = fetch.kernel
    uptime = fetch.uptime

    cpu = f"{fetch.cpuname} ({fetch.cpucores})"
    mem = f"{fetch.memavail}/{fetch.memtotal}m ({fetch.memfree}+{fetch.memcache})"

    c = Colors()

    finmsg = f" {c.C_WHI}→ {c.C_RED}host   {c.C_BLU}:{c.C_RES} {hostname}\n"
    finmsg += f" {c.C_WHI}→ {c.C_RED}os     {c.C_BLU}:{c.C_RES} {distro}\n"
    finmsg += f" {c.C_WHI}→ {c.C_RED}kernel {c.C_BLU}:{c.C_RES} {kernel}\n"
    finmsg += f" {c.C_WHI}→ {c.C_RED}cpu    {c.C_BLU}:{c.C_RES} {cpu}\n"
    finmsg += f" {c.C_WHI}→ {c.C_RED}mem    {c.C_BLU}:{c.C_RES} {mem}\n"
    finmsg += f" {c.C_WHI}→ {c.C_RED}uptime {c.C_BLU}:{c.C_RES} {uptime}\n"

    print(finmsg, end="")
