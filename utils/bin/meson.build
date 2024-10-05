input_files = [
    '0x0',
    'cb',
    'cblist',
    'chromium',
    'colortest',
    'comptoggle',
    'csv2pw.py',
    'dn',
    'dwmenu',
    'fetch.py',
    'getip.py',
    'ldir',
    'maimclip',
    'maimcrop',
    'maimscrot',
    'ossl',
    'setbright',
    'setcake.py',
    'setgov',
    'setmon',
    'setxkeeb',
    'statusbar.py',
    'suspendtodisk',
    'syncboi',
    'ttygrab',
    'weather.py',
    'webm2mp3'
]

foreach file: input_files
    configured_file = configure_file(
        input: file,
        output: file,
        configuration: conf,
        install: true,
        install_dir: mssdir / 'bin'
    )
endforeach
