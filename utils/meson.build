project('utils',
 version: '61',
 license: 'GPL3',
 default_options: [
  'buildtype=plain',
  'prefix=/mss',
  'bindir=/mss/bin',
  'datadir=/mss/etc',
 ]
)

# 1 > files
files_bin = [
 'bin/0x0',
 'bin/cb',
 'bin/cblist',
 'bin/colortest',
 'bin/comptoggle',
 'bin/dn',
 'bin/ldir',
 'bin/maimclip',
 'bin/maimcrop',
 'bin/maimscrot',
 'bin/menuboi.sh',
 'bin/ossl',
 'bin/pkgup',
 'bin/setgov',
 'bin/setmon',
 'bin/setxkeeb',
 'bin/statusbar.py',
 'bin/suspendtodisk',
 'bin/syncboi',
 'bin/ttygrab',
 'bin/weather.py'
]

files_etc = [
 'etc/funcs',
 'etc/sourceme',
 'etc/sourceme-aliases',
 'etc/sourceme-build'
]

install_data(files_bin, install_dir: get_option('bindir'))
install_data(files_etc, install_dir: get_option('datadir'))
