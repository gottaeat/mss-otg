input_files = [
    'bash-handler',
]

if is_linux
    input_files += 'multiwg-handler'
endif

foreach file: input_files
    configured_file = configure_file(
        input: file,
        output: file,
        configuration : conf,
        install: true,
        install_dir: mssdir / 'share'
    )
endforeach

install_script = configure_file(
    input: 'install_symlinks.sh.in',
    output: 'install_symlinks.sh',
    configuration: conf
)

meson.add_install_script(install_script)
