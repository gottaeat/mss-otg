#!/usr/bin/python
import argparse
import ssl
import urllib.request
from datetime  import datetime
from json      import loads
from re        import sub
from threading import Thread

## parse inputs
desc = '{current|weekly|hourly} weather data from mgm.gov.tr'
parser = argparse.ArgumentParser(description = desc)
parser.add_argument('--loc', type = str, default = "Ankara/Esenboga Havalimani")

args = parser.parse_args()
loc = args.loc

## funcs
def drawbox(string, charset):
 if charset == 'double':
  chars = {'1': '╔', '2': '╗', '3': '╚', '4': '╝', 'h': '═', 'v': '║'}
 elif charset == 'single':
  chars = {'1': '┌', '2': '┐', '3': '└', '4': '┘', 'h': '─', 'v': '│'}
 else:
  chars = {'1': '+', '2': '+', '3': '+', '4': '+', 'h': '-', 'v': '|'}

 a = string.split('\n')
 if a[-1] == '': a = a[:-1]

 for i in range(0, len(a)):
  a[i] = sub(r'^', chars['v'], a[i])

 width = len(max(a, key=len))

 for i in range(0, len(a)):
  a[i] = (f"{a[i]}{(width - len(a[i])) * ' '}{chars['v']}")

 a.insert(0, f"{chars['1']}{chars['h'] * (width - 1)}{chars['2']}")
 a.append(f"{chars['3']}{chars['h'] * (width - 1)}{chars['4']}")

 fin = ''
 finlen = len(a)
 for i in range(0, finlen):
  fin += a[i] + '\n'

 return fin

def convtime(tstamp):
 return datetime.strptime(tstamp,
                          "%Y-%m-%dT%H:%M:%S.%fZ"
                          ).strftime("%a %d %H:%M:%S")

def formatstring(string):
 string = sub(r'[Çç]', 'c', string)
 string = sub(r'[Öö]', 'o', string)
 string = sub(r'[Üü]', 'u', string)
 string = sub(r'[Ğğ]', 'g', string)
 string = sub(r'[İı]', 'i', string)
 string = sub(r'[Şş]', 's', string)

 return string.title()

def getdata(req):
 context          = ssl.create_default_context()
 context.options |= 0x4

 if ' ' in req: req = sub(r' ', '%20', req)

 rawdata = urllib.request.Request(req)
 rawdata.add_header('Origin', 'https://mgm.gov.tr')

 return loads(urllib.request.urlopen(rawdata, context=context).read().decode())

def getids(data):
 want, ids = ['merkezId',
              'gunlukTahminIstNo',
              'saatlikTahminIstNo'
             ], []

 for i in want: ids.append(str(data[i]))

 return ids

def getweat_curr(curreq):
 global currfin

 data   = getdata(curreq)[0]
 tstamp = convtime(data['veriZamani'])

 coderaw, tempraw, windraw, rainraw, moisraw = (data['hadiseKodu'],
                                                data['sicaklik'],
                                                data['ruzgarHiz'],
                                                data['yagis00Now'],
                                                data['nem'])

 code = coderaw.lower()          if coderaw != -9999 else "n/a"
 temp = f"{tempraw}"             if tempraw != -9999 else "n/a"
 wind = "{:.1f}".format(windraw) if windraw != -9999 else "n/a"
 rain = f"{rainraw}"             if rainraw != -9999 else "n/a"
 mois = f"{moisraw}"             if moisraw != -9999 else "n/a"

 currfin  = "  current weather\n"
 currfin += "  " + ('-' * (len(currfin) - 3)) + "\n"

 currfin += f"→ {tstamp}\n"
 currfin += f"→ {'code'       : >15} | {code :>5}\n"
 currfin += f"→ {'temperature': >15} | {temp :>5} C°\n"
 currfin += f"→ {'wind speed' : >15} | {wind :>5} km/s\n"
 currfin += f"→ {'rainfall'   : >15} | {rain :>5} mm\n"
 currfin += f"→ {'moisture'   : >15} | {mois :>5} %"

def getweat_hourly(hourlyreq):
 global hourfin

 if hourlyID == 'None':
  hourfin = "! hourly forecast is not available for this location"
 else:
  data = getdata(hourlyreq)[0]['tahmin']

  hourfin  = "  hourly forecast\n"
  hourfin += "  " + ('-' * (len(hourfin) - 3)) + "\n"

  datalen = len(data)
  for i in range(0, datalen):
   curdat = data[i]
   tstamp  = convtime(curdat['tarih'])
   coderaw = curdat['hadise']
   tempraw = curdat['sicaklik']
   feelraw = curdat['hissedilenSicaklik']
   moisraw = curdat['nem']
   wsperaw = curdat['ruzgarHizi']
   maxwraw = curdat['maksimumRuzgarHizi']

   code = coderaw.lower()          if coderaw != -9999 else "n/a"
   temp = f"{tempraw}"             if tempraw != -9999 else "n/a"
   feel = f"{feelraw}"             if feelraw != -9999 else "n/a"
   mois = f"{moisraw}"             if moisraw != -9999 else "n/a"
   wspe = "{:.1f}".format(wsperaw) if wsperaw != -9999 else "n/a"
   maxw = "{:.1f}".format(maxwraw) if maxwraw != -9999 else "n/a"

   hourfin += f"→ {tstamp} | {code : >5} {temp + '/' + feel + 'C°' : >9}"
   hourfin += f" {mois + '%' : >8} {wspe + '/' + maxw + ' km/h' : >15}"

   if i == (datalen - 1):
    continue
   else:
    hourfin += '\n'

def getweat_weekly(weeklyreq):
 global weekfin

 data = getdata(weeklyreq)[0]

 weekfin  = "  weekly forecast\n"
 weekfin += "  " + ('-' * (len(weekfin) - 3)) + "\n"

 datalen = int(((len(data) - 1 ) / 8) + 1)
 for i in range(1, datalen):
  i = str(i)

  tstamp  = convtime(data['tarihGun' + i])
  coderaw = data['hadiseGun'      + i]
  ltmpraw = data['enDusukGun'     + i]
  htmpraw = data['enYuksekGun'    + i]
  lmoiraw = data['enDusukNemGun'  + i]
  hmoiraw = data['enYuksekNemGun' + i]
  wsperaw = data['ruzgarHizGun'   + i]

  code = coderaw.lower()          if coderaw != "-9999" else "n/a"
  ltmp = f"{ltmpraw}"             if ltmpraw != "-9999" else "n/a"
  htmp = f"{htmpraw}"             if htmpraw != "-9999" else "n/a"
  lmoi = f"{lmoiraw}"             if lmoiraw != "-9999" else "n/a"
  hmoi = f"{hmoiraw}"             if hmoiraw != "-9999" else "n/a"
  wspe = "{:.1f}".format(wsperaw) if wsperaw != "-9999" else "n/a"

  weekfin += f"→ {tstamp} | {code : >5} {ltmp + '/' + htmp + 'C°' : >9}"
  weekfin += f" {lmoi + '/' + hmoi + '%' : >8} {wspe + ' km/h' : >15}"

  if i == str(datalen - 1):
   continue
  else:
   weekfin += '\n'

## action
if '/' not in loc:
 warn  = "locations should be separated with a /.\n"  
 warn += "(eg. 'Ankara/Çankaya'.)"
 print(drawbox(warn, 'double'), end='')
 exit(1)
else:
 loc = args.loc.split('/')

if len(loc) > 2:
 warn  = "location should be composed of a city and a province\n"
 warn += "separated with a /. (eg. 'Ankara/Çankaya'.)"
 print(drawbox(warn, 'double'), end='')
 exit(1)
else:
 for i in range(0, len(loc)):
  loc[i] = formatstring(sub(r'^\ |\ $', '', loc[i]))
  if i == 0:
   il = loc[0]
  elif i == 1:
   ilce = loc[1]

mgmhost = 'https://servis.mgm.gov.tr/web'
idreq   = mgmhost + '/merkezler?il=' + il + '&ilce=' + ilce

try:
 stationID, dailyID, hourlyID = getids(getdata(idreq)[0])
except:
 warn  = "location is not valid according to MGM.\n"
 print(drawbox(warn, 'double'), end='')
 exit(1)
 
weeklyreq = mgmhost + '/tahminler/gunluk?istno='  + dailyID
curreq    = mgmhost + '/sondurumlar?merkezid='    + stationID
hourlyreq = mgmhost + '/tahminler/saatlik?istno=' + hourlyID

## threads
curr_thread   = Thread(target=getweat_curr, args=(curreq,))
hourly_thread = Thread(target=getweat_hourly, args=(hourlyreq,))
weekly_thread = Thread(target=getweat_weekly, args=(weeklyreq,))

threads = []
for i in curr_thread, hourly_thread, weekly_thread: threads.append(i)
for i in threads: i.start()
for i in threads: i.join()

finprint = drawbox(f"{il}/{ilce} | ({stationID} | {dailyID} | {hourlyID})", 'single')
for i in currfin, hourfin, weekfin: finprint += drawbox(i, 'single')
print(drawbox(finprint, 'double'))
