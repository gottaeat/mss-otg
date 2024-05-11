project('utils',
        version: '107',
        license: 'GPL3',
        default_options: [
            'buildtype=plain',
            'prefix=/mss',
        ]
)

files_bin = [
    'bin/0x0',
    'bin/cb',
    'bin/cblist',
    'bin/chromium',
    'bin/colortest',
    'bin/comptoggle',
    'bin/csv2pw.py',
    'bin/dn',
    'bin/dwmenu',
    'bin/fetch.py',
    'bin/getip.py',
    'bin/ldir',
    'bin/maimclip',
    'bin/maimcrop',
    'bin/maimscrot',
    'bin/ossl',
    'bin/pkgup',
    'bin/setbright',
    'bin/setcake.py',
    'bin/setgov',
    'bin/setmon',
    'bin/setxkeeb',
    'bin/statusbar.py',
    'bin/suspendtodisk',
    'bin/syncboi',
    'bin/ttygrab',
    'bin/weather.py',
    'bin/webm2mp3'
]

files_etc = [
    'etc/funcs',
    'etc/sourceme',
    'etc/sourceme-aliases',
    'etc/sourceme-build'
]

files_share = [
    'share/bash-handler',
    'share/multiwg-handler'
]

install_data(files_bin, install_dir: join_paths(get_option('prefix'), 'bin'))
install_data(files_etc, install_dir: join_paths(get_option('prefix'), 'etc'))
install_data(files_share, install_dir: join_paths(get_option('prefix'), 'share'))
