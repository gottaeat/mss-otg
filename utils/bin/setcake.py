#!/usr/bin/python3
# pylint: disable=bare-except
# pylint: disable=inconsistent-return-statements
# pylint: disable=line-too-long
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=missing-module-docstring
# pylint: disable=too-few-public-methods

import argparse
import logging
import os
import subprocess
import sys


class ANSIColors:
    RES = "\033[0;39m"

    LBLK = "\033[0;30m"
    LRED = "\033[0;31m"
    LGRN = "\033[0;32m"
    LYEL = "\033[0;33m"
    LBLU = "\033[0;34m"
    LMGN = "\033[0;35m"
    LCYN = "\033[0;36m"
    LWHI = "\033[0;37m"

    BBLK = "\033[1;30m"
    BRED = "\033[1;31m"
    BGRN = "\033[1;32m"
    BYEL = "\033[1;33m"
    BBLU = "\033[1;34m"
    BMGN = "\033[1;35m"
    BCYN = "\033[1;36m"
    BWHI = "\033[1;37m"

    def __init__(self):
        pass


class ShutdownHandler(logging.StreamHandler):
    def emit(self, record):
        if record.levelno >= logging.ERROR:
            sys.exit(1)


class SetCAKEFormatter(logging.Formatter):
    _c = ANSIColors()

    _FMT_DATE = "%H:%M:%S"

    _FMT_BEGIN = f"{_c.BBLK}[{_c.BWHI}%(name)s{_c.BBLK}]["
    _FMT_END = f"{_c.BBLK}]{_c.RES}"

    _FORMATS = {
        logging.NOTSET: _c.LCYN,
        logging.DEBUG: _c.BWHI,
        logging.INFO: _c.BBLU,
        logging.WARNING: _c.LGRN,
        logging.ERROR: _c.LRED,
        logging.CRITICAL: _c.LRED,
    }

    def format(self, record):
        finfmt = f"{self._FMT_BEGIN}{self._FORMATS.get(record.levelno)}"
        finfmt += f"%(levelname)-.1s{self._FMT_END} %(message)s"

        return logging.Formatter(
            fmt=finfmt, datefmt=self._FMT_DATE, validate=True
        ).format(record)


class SetCAKE:
    INGRESS_OPTS = "besteffort dual-srchost nat nowash no-ack-filter split-gso rtt 100ms noatm overhead 44"
    EGRESS_OPTS = "besteffort dual-dsthost nat wash ingress no-ack-filter split-gso rtt 100ms noatm overhead 44"

    def __init__(self):
        self.logger = None

        self.command = None

        self.iface = None
        self.ifb = None

        self.bw_down = None
        self.bw_up = None

    def _parse_args(self):
        parser = argparse.ArgumentParser(description="CAKE configurator.")
        subparsers = parser.add_subparsers(dest="command", required=True)

        start = subparsers.add_parser("start", help="configure CAKE for an interface.")
        start.add_argument("--iface", type=str, required=True)
        start.add_argument("--ifb", type=str, required=True)
        start.add_argument(
            "--down", type=int, required=True, help="qdisc bandwidth limit in Mbit/s"
        )
        start.add_argument(
            "--up", type=int, required=True, help="qdisc bandwidth limit in Mbit/s"
        )

        stop = subparsers.add_parser("stop", help="deconfigure CAKE")
        stop.add_argument("--iface", type=str, required=True)
        stop.add_argument("--ifb", type=str, required=True)

        args = parser.parse_args()

        self.command = args.command
        self.iface = args.iface
        self.ifb = args.ifb

        if self.command == "start":
            self.bw_down = args.down
            self.bw_up = args.up

    def _runcmd(self, string, ignore_err=False, quiet=True):
        cmdline = string.split(" ")

        try:
            proc = subprocess.run(cmdline, check=True, capture_output=True)
        except subprocess.CalledProcessError as except_obj:
            if not ignore_err:
                self.logger.error(
                    "command failed: %s", except_obj.stderr.decode("utf-8")
                )

        if not quiet:
            return (proc.returncode, proc.stdout.decode("utf-8"))

    def _stop(self):
        # iface
        self.logger.info("clearing state for %s", self.iface)
        self._runcmd(f"tc qdisc del dev {self.iface} ingress", ignore_err=True)
        self._runcmd(f"tc qdisc del dev {self.iface} root", ignore_err=True)

        # ifb
        self.logger.info("deleting %s (if it exists)", self.ifb)
        self._runcmd(f"ip link del {self.ifb}", ignore_err=True)

    def _info(self):
        msg = f" → interface: {self.iface}\n"
        msg += f" → ifb      : {self.iface}"

        for line in msg.split("\n"):
            self.logger.info(line)

    def _start(self):
        self._info()

        # just check if the sysfs dir for the iface exists, going off of
        # operstate gets shoddy, python has no proper api except for external
        # modules to parse the /flags and i don't have the mental capacity or
        # the care in the world to do the bitwise shit
        iface_path = f"/sys/class/net/{self.iface}/"

        if not os.path.isdir(iface_path):
            self.logger.error("interface %s does not exist.", self.iface)

        # set known state
        self._stop()

        # load module
        self.logger.info("loading the ifb module")
        self._runcmd("modprobe ifb numifbs=1")

        # create and bring up ifb0
        self.logger.info("creating and bringing up %s", self.ifb)
        self._runcmd(f"ip link add dev {self.ifb} up type ifb")
        self._runcmd(f"ip link set dev {self.ifb} up")

        # clear defaults
        self.logger.info("clearing qdisc for %s", self.ifb)
        self._runcmd(f"tc qdisc del dev {self.ifb} root", ignore_err=True)

        # create ingress chain
        self.logger.info("creating ingress chain for %s", self.iface)
        self._runcmd(f"tc qdisc add dev {self.iface} ingress")

        # redirect ingress to ifb
        self.logger.info("mirror ingress for %s to %s", self.iface, self.ifb)
        self._runcmd(
            f"tc filter add dev {self.iface} parent ffff: basic action mirred egress redirect dev {self.ifb}"
        )

        # egress shaping
        self.logger.info("setting egress shaping for %s", self.iface)
        self._runcmd(
            f"tc qdisc replace dev {self.iface} root cake bandwidth {self.bw_up}Mbit {self.EGRESS_OPTS}"
        )

        # ingress shaping
        self.logger.info("setting ingress shaping for %s with %s", self.iface, self.ifb)
        self._runcmd(
            f"tc qdisc replace dev {self.ifb} root cake bandwidth {self.bw_down}Mbit {self.EGRESS_OPTS}"
        )

    def run(self):
        self.logger = logging.getLogger("SetCAKE")
        self.logger.setLevel(logging.DEBUG)

        handler = logging.StreamHandler()
        handler.setLevel(logging.DEBUG)

        handler.setFormatter(SetCAKEFormatter())

        self.logger.addHandler(handler)
        self.logger.addHandler(ShutdownHandler())

        if os.getuid() != 0:
            self.logger.error("this script must be run as root.")

        self._parse_args()

        if self.command == "start":
            self._start()
        else:
            self._stop()


if __name__ == "__main__":
    sc = SetCAKE()
    sc.run()
