#!/usr/bin/python3
# pylint: disable=missing-module-docstring,missing-class-docstring,missing-function-docstring
# pylint: disable=too-few-public-methods,too-many-instance-attributes
# pylint: disable=invalid-name

import argparse
import urllib.parse
import urllib.request
import ssl
import json
import re
import unicodedata
from datetime import datetime
from threading import Thread


class MGM:
    def __init__(self, city, province):
        self.il = city
        self.ilce = province

        self.station_id = None
        self.daily_id = None
        self.hourly_id = None

        self.current = None
        self.daily = None
        self.hourly = None

    def _get_data(self, request, params):
        context = ssl.create_default_context()
        context.options |= 0x4

        params = urllib.parse.urlencode(params)
        url = f"https://servis.mgm.gov.tr/web/{request}?{params}"
        headers = {"Origin": "https://mgm.gov.tr"}

        request = urllib.request.Request(f"{url}", headers=headers)

        with urllib.request.urlopen(request, context=context) as f:
            data = json.loads(f.read().decode())

        return data

    def _get_ids(self):
        data = self._get_data("merkezler", {"il": self.il, "ilce": self.ilce})[0]
        self.station_id = data["merkezId"]
        self.daily_id = data["gunlukTahminIstNo"]
        self.hourly_id = data["saatlikTahminIstNo"]

    @staticmethod
    def _convtime(timestamp):
        return datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%fZ").strftime(
            "%a %d %H:%M:%S"
        )

    def _get_current(self):
        if self.daily_id is None:
            msg = "! current weather information is not available for this location.\n"
        else:
            data = self._get_data("sondurumlar", {"merkezid": self.station_id})[0]

            timestamp = self._convtime(data["veriZamani"])

            code = data["hadiseKodu"]
            temp = data["sicaklik"]
            wind = data["ruzgarHiz"]
            rain = data["yagis00Now"]
            moist = data["nem"]

            code = code.lower() if code != -9999 else "n/a"
            temp = temp if temp != -9999 else "n/a"
            wind = f"{wind:.1f}" if wind != -9999 else "n/a"
            rain = rain if rain != -9999 else "n/a"
            moist = moist if moist != -9999 else "n/a"

            msg = "  current weather\n"
            msg += f"  {('-' * (len(msg) - 3))}\n"
            msg += f"→ {timestamp}\n"
            msg += f"→ {'code'       : >15} | {code :>5}\n"
            msg += f"→ {'temperature': >15} | {temp :>5} C°\n"
            msg += f"→ {'wind speed' : >15} | {wind :>5} km/s\n"
            msg += f"→ {'rainfall'   : >15} | {rain :>5} mm\n"
            msg += f"→ {'moisture'   : >15} | {moist :>5} %\n"

        self.current = drawbox(msg, "single")

    def _get_daily(self):
        if self.daily_id is None:
            msg = "! daily forecast is not available for this location.\n"
        else:
            data = self._get_data("tahminler/gunluk", {"istno": self.daily_id})[0]

            msg = "  weekly forecast\n"
            msg += f"  {('-' * (len(msg) - 3))}\n"

            for day in range(1, 6):
                timestamp = self._convtime(data[f"tarihGun{day}"])

                code = data[f"hadiseGun{day}"]
                temp_lo = data[f"enDusukGun{day}"]
                temp_hi = data[f"enYuksekGun{day}"]
                moist_lo = data[f"enDusukNemGun{day}"]
                moist_hi = data[f"enYuksekNemGun{day}"]
                wind = data[f"ruzgarHizGun{day}"]

                code = code.lower() if code != "-9999" else "n/a"
                temp_lo = f"{temp_lo}" if temp_lo != "-9999" else "n/a"
                temp_hi = f"{temp_hi}" if temp_hi != "-9999" else "n/a"
                moist_lo = f"{moist_lo}" if moist_lo != "-9999" else "n/a"
                moist_hi = f"{moist_hi}" if moist_hi != "-9999" else "n/a"
                wind = f"{wind:.1f}" if wind != "-9999" else "n/a"

                msg += (
                    f"→ {timestamp} | {code : >5} {temp_lo + '/' + temp_hi + 'C°' : >9}"
                )
                msg += (
                    f" {moist_lo + '/' + moist_hi + '%' : >8} {wind + ' km/h' : >15}\n"
                )

        self.daily = drawbox(msg, "single")

    def _get_hourly(self):
        if self.hourly_id is None:
            msg = "! hourly forecast is not available for this location.\n"
        else:
            data = self._get_data("tahminler/saatlik", {"istno": self.hourly_id})[0][
                "tahmin"
            ]

            msg = "  hourly forecast\n"
            msg += f"  {('-' * (len(msg) - 3))}\n"

            for _, day in enumerate(data):
                timestamp = self._convtime(day["tarih"])

                code = day["hadise"]
                temp = day["sicaklik"]
                feel = day["hissedilenSicaklik"]
                moist = day["nem"]
                wind = day["ruzgarHizi"]
                wind_max = day["maksimumRuzgarHizi"]

                code = code.lower() if code != -9999 else "n/a"
                temp = str(temp) if temp != -9999 else "n/a"
                feel = str(feel) if feel != -9999 else "n/a"
                moist = str(moist) if moist != -9999 else "n/a"
                wind = f"{wind:.1f}" if wind != -9999 else "n/a"
                wind_max = f"{wind_max:.1f}" if wind_max != -9999 else "n/a"

                msg += f"→ {timestamp} | {code : >5} {temp + '/' + feel + 'C°' : >9}"
                msg += f" {moist + '%' : >8} {wind + '/' + wind_max + ' km/h' : >15}\n"

        self.hourly = drawbox(msg, "single")

    def collect(self):
        self._get_ids()

        threads = []
        current_thread = Thread(target=self._get_current, daemon=False)
        daily_thread = Thread(target=self._get_daily, daemon=False)
        hourly_thread = Thread(target=self._get_hourly, daemon=False)

        threads.append(current_thread)
        threads.append(daily_thread)
        threads.append(hourly_thread)

        for job in threads:
            job.start()

        for job in threads:
            job.join()

        return drawbox(f"{self.current}{self.hourly}{self.daily}", "double")


def unilen(string):
    width = 0
    for i in string:
        if unicodedata.category(i)[0] in ("M", "C"):
            continue
        w = unicodedata.east_asian_width(i)
        if w in ("N", "Na", "H", "A"):
            width += 1
        else:
            width += 2
    return width


def drawbox(string, charset):
    if charset == "double":
        chars = {"1": "╔", "2": "╗", "3": "╚", "4": "╝", "h": "═", "v": "║"}
    elif charset == "single":
        chars = {"1": "┌", "2": "┐", "3": "└", "4": "┘", "h": "─", "v": "│"}
    elif charset == "thic":
        chars = {"1": "╔", "2": "╗", "3": "╚", "4": "╝", "h": "─", "v": "│"}
    else:
        chars = {"1": "+", "2": "+", "3": "+", "4": "+", "h": "-", "v": "|"}

    string = string.split("\n")

    if string[-1] == "":
        string = string[:-1]
    if string[0] == "":
        string = string[1:]

    for i, _ in enumerate(string):
        string[i] = re.sub(r"^", chars["v"], string[i])

    width = 0
    for i, _ in enumerate(string):
        if unilen(string[i]) > width:
            width = unilen(string[i])

    for i, _ in enumerate(string):
        string[i] = f"{string[i]}{(width - unilen(string[i])) * ' '}{chars['v']}"

    string.insert(0, f"{chars['1']}{chars['h'] * (width - 1)}{chars['2']}")
    string.append(f"{chars['3']}{chars['h'] * (width - 1)}{chars['4']}")

    fin = ""
    for i, line in enumerate(string):
        fin += line + "\n"

    return fin


def stripstring(string):
    string = re.sub(r"[Çç]", "c", string)
    string = re.sub(r"[Öö]", "o", string)
    string = re.sub(r"[Üü]", "u", string)
    string = re.sub(r"[Ğğ]", "g", string)
    string = re.sub(r"[İı]", "i", string)
    string = re.sub(r"[Şş]", "s", string)

    return string.title()


if __name__ == "__main__":
    PARSER_DESC = "Pull current/hourly/daily weather reports from the MGM API"

    parser = argparse.ArgumentParser(description=PARSER_DESC)
    parser.add_argument("-l", "--loc", type=str, default="Ankara/Esenboga Havalimani")

    args = parser.parse_args()
    location = args.loc

    if "/" not in location:
        warn = "Location should be separated with a /.\n"
        warn += "(eg. 'Ankara/Çankaya')"
        raise ValueError(drawbox(warn, "double"), end="")

    location = location.split("/")

    if len(location) > 2:
        warn = "Location should be composed of a city and a province\n"
        warn += "separated with a /. (eg. 'Ankara/Çankaya')"
        raise ValueError(drawbox(warn, "double"), end="")

    for num, val in enumerate(location):
        location[num] = stripstring(re.sub(r"^\ |\ $", "", val))

    weather = MGM(location[0], location[1])
    weather = weather.collect()
    print(weather, end="")
