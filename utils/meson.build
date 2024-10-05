subdir('bin')
subdir('etc')
subdir('share')

if setboxes
    install_script = configure_file(
        input: 'setboxes.sh.in',
        output: 'setboxes.sh',
        configuration: conf
    )

    meson.add_install_script(install_script)
endif
