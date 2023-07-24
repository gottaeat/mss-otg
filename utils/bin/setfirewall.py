#!/usr/bin/python
# pylint: disable=missing-module-docstring,missing-function-docstring
import os
import shutil
import subprocess
import argparse

# 1 > parse args
PARSER_DESC = "Create a baseline firewall using nftables with rules that do "
PARSER_DESC += "not collide with the non-internet-facing interfaces."
PARSER_TCP_DESC = "List of TCP ports allowed on the internet-facing interface."
PARSER_UDP_DESC = "List of UDP ports allowed on the internet-facing interface."
PARSER_DESK_DESC = "Install the NAT rules for allowing rootless HTTP(s) servers."

parser = argparse.ArgumentParser(description=PARSER_DESC)
parser.add_argument("--tcp", nargs="+", type=int, help=PARSER_TCP_DESC)
parser.add_argument("--udp", nargs="+", type=int, help=PARSER_UDP_DESC)
parser.add_argument("--desktop", action="store_true", help=PARSER_DESK_DESC)
args = parser.parse_args()

tcp_ports = args.tcp
udp_ports = args.udp
desktop = args.desktop

# pylint: disable=invalid-name
iface = None


# 2 > functions
def nftrun(string):
    cmdline = string.split(" ")
    cmdline.insert(0, "nft")
    subprocess.run(cmdline, check=True)


def genports(ports):
    for port in ports:
        if port <= 0 or port > 65535:
            raise ValueError(f"TCP port {port} is invalid.")

    ports, ports_str = list(set(ports)), ""

    for i in ports:
        ports_str += f"{i},"

    ports_str.strip(",")

    return ports_str


# 3 > prechecks
if os.getuid() != 0:
    raise ValueError("This script must be run as root.")

if not shutil.which("nft"):
    raise ValueError("`nft' is not found in path.")

with open("/proc/net/route", "r", encoding="utf-8") as f:
    for line in f.readlines():
        line = line.strip().split()
        if line[1] == "00000000":
            iface = line[0]
            break

if iface is None:
    raise ValueError("No interface with a default route.")

if tcp_ports is None and udp_ports is None:
    raise ValueError("You have not allowed any TCP or UDP ports.")

tcp_ports = genports(tcp_ports)
udp_ports = genports(udp_ports)

# 4 > action
print(f" > Default interface is: {iface}")
print("  - Flushing ruleset.")
nftrun("flush ruleset")

print("  - Creating tables:")
for table in ["myfilter", "mynat"]:
    nftrun(f"add table ip {table}")

print("  - Creating inet_service sets with the provided ports.")
for table in ["myfilter", "mynat"]:
    nftrun(
        f"add set ip {table} tcp_allow {{type inet_service; elements = {{{tcp_ports}}}}}"
    )
    nftrun(
        f"add set ip {table} udp_allow {{type inet_service; elements = {{{udp_ports}}}}}"
    )

print("  - Creating chains.")
for chain in ["input", "output", "forward"]:
    runstr = f"create chain ip myfilter {chain} {{type filter hook {chain}"
    runstr += " priority -200; policy accept;}"
    nftrun(runstr)

for chain in ["prerouting", "output"]:
    runstr = f"create chain ip mynat {chain} {{type nat hook {chain}"
    runstr += " priority mangle; policy accept;}"
    nftrun(runstr)

print("  - Creating handlers for the internet-facing interfaces.")
nftrun("create chain ip myfilter handle_eth_filter_input")
nftrun("create chain ip mynat handle_eth_nat_prerouting")
nftrun("create chain ip mynat handle_eth_nat_output")

print("  - Creating base filter<-input rules.")
nftrun("add rule ip myfilter input ct state established,related accept")
nftrun('add rule ip myfilter input iifname "lo" accept')
nftrun('add rule ip myfilter input iifname != "lo" ip daddr 127.0.0.0/8 drop')
nftrun("add rule ip myfilter input icmp type echo-request accept")
nftrun(f"add rule ip myfilter input iifname {iface} jump handle_eth_filter_input")

print("  - Creating the internet-facing interface handler rules for filter<-input.")
nftrun("add rule ip myfilter handle_eth_filter_input tcp dport @tcp_allow accept")
nftrun("add rule ip myfilter handle_eth_filter_input udp dport @udp_allow accept")
nftrun("add rule ip myfilter handle_eth_filter_input counter drop")

print("  - Creating base nat<-prerouting rules.")
nftrun("add rule ip mynat prerouting ct state established,related accept")
nftrun(f"add rule ip mynat prerouting iifname {iface} jump handle_eth_nat_prerouting")

if desktop:
    print(
        "  - Creating the internet-facing interface handler rules for nat<-prerouting."
    )
    nftrun("add rule ip mynat handle_eth_nat_prerouting tcp dport 80 redirect to :1337")
    nftrun(
        "add rule ip mynat handle_eth_nat_prerouting tcp dport 443 redirect to :1338"
    )

nftrun("add rule ip mynat handle_eth_nat_prerouting tcp dport @tcp_allow accept")
nftrun("add rule ip mynat handle_eth_nat_prerouting udp dport @udp_allow accept")
nftrun("add rule ip mynat handle_eth_nat_prerouting counter drop")

if desktop:
    print("  - Creating base nat<-output rules.")
    nftrun(f"add rule ip mynat output oifname {iface} jump handle_eth_nat_output")
    print("  - Creating the internet-facing interface handler rules for nat<-output.")
    nftrun(
        "add rule ip mynat handle_eth_nat_output ip daddr 127.0.0.1 tcp dport 80 redirect to :1337"
    )
    nftrun(
        "add rule ip mynat handle_eth_nat_output ip daddr 127.0.0.1 tcp dport 443 redirect to :1338"
    )

# 5 > write to disk
print(" > Writing changes to disk.")
with open("/etc/nftables.conf", "w", encoding="utf-8") as file:
    file.write("flush ruleset\n\n")
    # pylint: disable=consider-using-with
    subprocess.Popen(["nft", "-s", "list", "ruleset"], stdout=file)
