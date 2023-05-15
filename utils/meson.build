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
 'etc/funcs',
 'etc/sourceme',
 'etc/sourceme-aliases',
 'etc/sourceme-build'
]

files_etc = [
 'etc/funcs',
 'etc/sourceme',
 'etc/sourceme-aliases',
 'etc/sourceme-build'
]

install_data(files_bin, install_dir: get_option('bindir'))
install_data(files_etc, install_dir: get_option('datadir'))
