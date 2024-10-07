input_files = [
    '0x0',
    'cb',
    'cblist',
    'colortest',
    'csv2pw.py',
    'dn',
    'getip.py',
    'ldir',
    'ossl',
    'statusbar.py',
    'syncboi',
    'weather.py',
    'webm2mp3'
]

input_files_landfill = [
    'chromium',
    'comptoggle',
    'dwmenu',
    'maimclip',
    'maimcrop',
    'maimscrot',
    'setbright',
    'setmon',
    'setxkeeb'
]

input_files_linux = [
    'fetch.py',
    'setcake.py',
    'setgov',
    'suspendtodisk',
    'ttygrab'
]

# merge
if is_linux
  input_files += input_files_linux
endif

if landfill
  input_files += input_files_landfill
endif

# template
foreach file: input_files
    configured_file = configure_file(
        input: file,
        output: file,
        configuration: conf,
        install: true,
        install_dir: mssdir / 'bin'
    )
endforeach
