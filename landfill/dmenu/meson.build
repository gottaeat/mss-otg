dmenu_common_args = common_args + [
    '-D_POSIX_C_SOURCE=200809L',
    '-D_XOPEN_SOURCE=700'
]

configure_file(
    input: 'dmenu_conf.h.in',
    output: 'dmenu_conf.h',
    configuration: conf
)

executable(
    'dmenu',
    files(
        'dmenu.c',
        'drw.c',
        'util.c'
    ),
    dependencies: [
        deps['fontconfig'],
        deps['x11'],
        deps['xft'],
        deps['xinerama']
    ],
    c_args:
        dmenu_common_args + [
            '-DVERSION="5.3-landfill"',
        ],
    install: true
)

executable(
    'stest',
    files('stest.c'),
    c_args: dmenu_common_args,
    install: true
)

install_data(
    [
        'dmenu_path',
        'dmenu_run'
    ],
    install_dir: get_option('bindir')
)
