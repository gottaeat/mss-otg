#!/usr/bin/python
# pylint: disable=missing-module-docstring,missing-class-docstring,missing-function-docstring
# pylint: disable=too-few-public-methods
# pylint: disable=invalid-name
# pylint: disable=redefined-outer-name

import argparse
import json
import socket
import sys
import urllib.parse
import urllib.request


class Colors:
    C_RES = "\033[0;39m"
    C_RED = "\033[1;31m"
    C_BLU = "\033[1;34m"
    C_WHI = "\033[1;37m"
    C_YEL = "\033[1;33m"

    def __init__(self):
        pass


class GetIP:
    def __init__(self, ip=None):
        self.ip = ip
        self.msg = None
        self.ip_parsed = None

    def _collect(self):
        req = "https://ipinfo.io"

        if self.ip:
            req += f"/{self.ip}"

        try:
            with urllib.request.urlopen(req) as f:
                data = f.read().decode()
        except urllib.error.HTTPError:
            self.ip_parsed = (False, "GET failed")
            return
        except urllib.error.URLError:
            self.ip_parsed = (False, "bad URL")
            return

        try:
            self.ip_parsed = (True, json.loads(data))
        except KeyError:
            self.ip_parsed = (False, "parse failed")
            return

    def _format(self):
        data = self.ip_parsed[1]

        max_len = 0
        for key in data.keys():
            if len(key) > max_len:
                max_len = len(key)

        c = Colors()
        msg = ""

        for key, val in data.items():
            if key == "readme":
                continue
            msg += f" {c.C_WHI}→ {c.C_RED}{key :<{max_len}}{c.C_BLU}:{c.C_RES} {val}\n"

        return msg.strip("\n")

    def run(self):
        self._collect()

        if not self.ip_parsed[0]:
            self.msg = self.ip_parsed[1]
            return

        self.msg = self._format()


if __name__ == "__main__":
    PARSER_DESC = "Get IP information from ipinfo.io."
    PARSER_IP_DESC = "List of IP addresses to be queried."
    parser = argparse.ArgumentParser(description=PARSER_DESC)
    parser.add_argument(
        "--ip", nargs="+", type=str, required=False, help=PARSER_IP_DESC
    )

    args = parser.parse_args()

    want_ip = args.ip

    c = Colors()

    if want_ip:
        for ip in want_ip:
            print(f"   {c.C_YEL}{ip}")

            getip = GetIP(socket.gethostbyname(ip))
            getip.run()

            print(f"{getip.msg}\n")

        sys.stdout.write("\x1b[1A\x1b[2K")
    else:
        getip = GetIP()
        getip.run()

        print(getip.msg)
