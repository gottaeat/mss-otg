input_files = [
    'funcs',
    'sourceme',
    'sourceme-aliases',
    'sourceme-build'
]

foreach file: input_files
    configured_file = configure_file(
        input: file,
        output: file,
        configuration : conf,
        install: true,
        install_dir: mssdir / 'etc'
    )
endforeach
