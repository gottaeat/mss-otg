configure_file(
    input: 'config.h.in',
    output: 'config.h',
    configuration: conf
)

executable(
    'st',
    files(
        'st.c',
        'x.c'
    ),
    dependencies: [
        deps['fontconfig'],
        deps['freetype2'],
        deps['m'],
        deps['rt'],
        deps['util'],
        deps['x11'],
        deps['xft'],
        deps['xrender']
    ],
    c_args: [
        '-DVERSION="0.9.2-landfill"',
        '-D_XOPEN_SOURCE=600'
    ],
    install: true
)
