#!/usr/bin/python3
# pylint: disable=missing-module-docstring,missing-class-docstring,missing-function-docstring
# pylint: disable=too-few-public-methods,too-many-instance-attributes
# pylint: disable=invalid-name
# pylint: disable=raise-missing-from

import argparse
import urllib.parse
import urllib.request
import ssl
import json
import re
from datetime import datetime
from threading import Thread


class Location:
    def __init__(self):
        self.city = None
        self.district = None

    @staticmethod
    def stripstring(string):
        string = re.sub(r"[Çç]", "c", string)
        string = re.sub(r"[Öö]", "o", string)
        string = re.sub(r"[Üü]", "u", string)
        string = re.sub(r"[Ğğ]", "g", string)
        string = re.sub(r"[İı]", "i", string)
        string = re.sub(r"[Şş]", "s", string)

        return string.title()


class MGM:
    def __init__(self, location):
        self.location = location

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

        try:
            with urllib.request.urlopen(request, context=context) as f:
                data = json.loads(f.read().decode())
        except urllib.request.HTTPError as e:
            raise ValueError(f"HTTP {e.code}")
        except urllib.error.URLError as e:
            raise ValueError(f"URL {e.reason.errno}")
        except Exception as e:
            raise ValueError(f"Unknown Error: {e}")

        return data

    def _get_ids(self):
        loc_dict = {"il": self.location.city}

        if self.location.district:
            loc_dict["ilce"] = self.location.district

        data = self._get_data("merkezler", loc_dict)[0]
        self.station_id = data["merkezId"]
        self.daily_id = data["gunlukTahminIstNo"]
        self.hourly_id = data["saatlikTahminIstNo"]

    @staticmethod
    def _convtime(timestamp):
        return datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%fZ").strftime(
            "%a %d %H:%M:%S"
        )

    def _get_current(self):
        if not self.daily_id:
            self.current = (
                "! current weather information is not available for this location.\n"
            )
            return

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
        msg += f"→ {'code'       : >18} | {code :>5}\n"
        msg += f"→ {'temperature': >18} | {temp :>5} C°\n"
        msg += f"→ {'wind speed' : >18} | {wind :>5} km/s\n"
        msg += f"→ {'rainfall'   : >18} | {rain :>5} mm\n"
        msg += f"→ {'moisture'   : >18} | {moist :>5} %\n"

        self.current = msg

    def _get_daily(self):
        if not self.daily_id:
            msg = "! daily forecast is not available for this location.\n"

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

            msg += f"→ {timestamp : >18} | {code : >5} {temp_lo + '/' + temp_hi + 'C°' : >9}"
            msg += f" {moist_lo + '/' + moist_hi + '%' : >8} {wind + ' km/h' : >15}\n"

        self.daily = msg

    def _get_hourly(self):
        if not self.hourly_id:
            self.hourly = "! hourly forecast is not available for this location.\n"
            return

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

            msg += f"→ {timestamp : >18} | {code : >5} {temp + '/' + feel + 'C°' : >9}"
            msg += f" {moist + '%' : >8} {wind + '/' + wind_max + ' km/h' : >15}\n"

        self.hourly = msg

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

        scrape_msg = f"{self.current}\n{self.hourly}\n{self.daily}\n"
        prompt = "  api details\n"
        prompt += f"  {('-' * (len(prompt) - 3))}\n"
        if self.station_id:
            prompt += f"→           merkezId | {self.station_id : >5}\n"
        if self.daily_id:
            prompt += f"→  gunlukTahminIstNo | {self.daily_id : >5}\n"
        if self.hourly_id:
            prompt += f"→ saatlikTahminIstNo | {self.hourly_id : >5}"

        print(f"{scrape_msg}{prompt}")


if __name__ == "__main__":
    parser_desc = "Pull current/hourly/daily weather reports from the MGM API"
    parser = argparse.ArgumentParser(description=parser_desc)
    parser.add_argument("location", type=str, default="Ankara/Esenboga Havalimani")

    args = parser.parse_args()
    loc_arg = args.location.split("/")

    if len(loc_arg) > 2:
        err_msg = "location must be composed of a city, and if exists, a district."
        raise ValueError(err_msg)

    loc = Location()
    loc.city = loc.stripstring(re.sub(r"^\ |\ $", "", loc_arg[0]))

    if len(loc_arg) == 2:
        loc.district = loc.stripstring(re.sub(r"^\ |\ $", "", loc_arg[1]))

    wt = MGM(loc)
    wt.collect()
