configure_file(
    input: 'config.h.in',
    output: 'config.h',
    configuration: conf
)

executable(
    'dwm',
    files(
        'drw.c',
        'dwm.c',
        'util.c'
    ),
    dependencies: [
        deps['fontconfig'],
        deps['x11'],
        deps['xft'],
        deps['xinerama']
    ],
    c_args: common_args + [
        '-DVERSION="6.5-landfill"',
        '-D_XOPEN_SOURCE=700L'
    ],
    install: true
)
