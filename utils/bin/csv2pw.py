#!/usr/bin/python3
# pylint: disable=missing-module-docstring,invalid-name,raise-missing-from
import csv
import sys
import os.path

try:
    csvfile = sys.argv[1]
except KeyError:
    raise ValueError("E: no file provided.")

if not os.path.exists(csvfile):
    raise ValueError(f"E: {csvfile} does not exist.")

if not os.path.isfile(csvfile):
    raise ValueError(f"E: {csvfile} is not a file.")

with open(csvfile, "r", newline="", encoding="utf-8") as file:
    csvlist = list(csv.DictReader(file))

maxlen1, maxlen2 = 0, 0
try:
    for _, c in enumerate(csvlist):
        len1 = len(c["name"])
        len2 = len(c["username"])
        if len1 > maxlen1:
            maxlen1 = len1
        if len2 > maxlen2:
            maxlen2 = len2
except KeyError:
    raise ValueError(f"E: {csvfile} is not a Chromium password export.")

passwd = ""
for _, i in enumerate(csvlist):
    pw_name = i["name"] if len(i["name"]) != 0 else "-"
    pw_user = i["username"] if len(i["username"]) != 0 else "-"
    pw_passwd = i["password"] if len(i["password"]) != 0 else "-"

    passwd += f"{pw_name:<{maxlen1}} {pw_user:<{maxlen2}} {pw_passwd}\n"

with open("browser_passwd.txt", "w", encoding="utf-8") as file:
    file.write(passwd)
