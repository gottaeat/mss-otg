#!/usr/bin/python3
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=missing-module-docstring
# pylint: disable=too-few-public-methods

import ipaddress
import json
import socket
import sys
import urllib.parse
import urllib.request

from threading import Thread


class Colors:
    C_RES = "\033[0;39m"
    C_RED = "\033[1;31m"
    C_BLU = "\033[1;34m"
    C_WHI = "\033[1;37m"
    C_YEL = "\033[1;33m"

    def __init__(self):
        pass


c = Colors()


class QueryAPI:
    def __init__(self, host=None):
        self.host = host
        self.msg = ""

    def _collect(self):
        # query api
        req = "https://ipinfo.io"

        if self.host:
            req += f"/{self.host}"

        try:
            with urllib.request.urlopen(req) as f:
                data = f.read().decode()
        except urllib.error.HTTPError:
            self.msg += f" {c.C_WHI}→ {c.C_RES}GET failed"
            return
        except urllib.error.URLError:
            self.msg += f" {c.C_WHI}→ {c.C_RES}bad URL"
            return

        # load json
        try:
            host_json = json.loads(data)
        except:  # pylint: disable=bare-except
            self.msg += f" {c.C_WHI}→ {c.C_RES}parse failed"
            return

        # format
        max_len = 0
        for key in host_json.keys():
            max_len = max(max_len, len(key))

        for key, val in host_json.items():
            if key == "readme" and "ipinfo" in req:
                continue

            self.msg += f" {c.C_WHI}→ {c.C_RED}{key :<{max_len}}"
            self.msg += f"{c.C_BLU}:{c.C_RES} {val}\n"

    def run(self):
        self._collect()
        print(self.msg, end="")


class GetAPI:
    def __init__(self):
        self.hosts = sys.argv[1:]
        self.hosts_to_query = {}

    def run(self):  # pylint: disable=inconsistent-return-statements
        if not self.hosts:
            qa = QueryAPI()
            qa.msg = f"   {c.C_YEL}self query{c.C_RES}\n"
            return qa.run()

        self.query()

    def query(self):
        host_threads = []
        for host in self.hosts:
            host_thread = Thread(target=self.host_lookup, args=(host,))
            host_threads.append(host_thread)

        for host_thread in host_threads:
            host_thread.start()

        for host_thread in host_threads:
            host_thread.join()

        if not self.hosts_to_query:
            return

        for key, val in self.hosts_to_query.items():
            qa = QueryAPI(val)
            qa.msg = f"   {c.C_YEL}{key}{c.C_RES}\n"
            host_query_thread = Thread(target=qa.run)
            host_query_thread.start()

    def host_lookup(self, host):
        try:
            ipaddress.ip_address(host)
            self.hosts_to_query[host] = host
        except ValueError:
            try:
                host_ip = socket.gethostbyname(host)
                self.hosts_to_query[host] = host_ip
            except socket.gaierror:
                msg = f"   {c.C_YEL}{host}{c.C_RES}\n"
                msg += f" {c.C_WHI}→ {c.C_RES}not an ip or failed to resolve"
                print(msg)


if __name__ == "__main__":
    GetAPI().run()
