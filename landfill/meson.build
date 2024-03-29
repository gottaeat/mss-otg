# -- landfill -- #
project('landfill', 'c',
    version: '31',
    license: 'MIT',
    default_options: [
        'buildtype=plain',
        'prefix=/usr',
        'c_std=c99'
    ]
)

# -- global cflags -- #
add_global_arguments(
    [
        '-fno-builtin',
    ],
    language : 'c'
)

# -- templating -- #
conf = configuration_data()
conf.set('fontname', get_option('fontname'))
conf.set('dmenufontsize', get_option('dmenufontsize'))
conf.set('dwmfontsize', get_option('dwmfontsize'))
conf.set('stfontsize', get_option('stfontsize'))

# -- dep def -- #
dep_fontconfig = dependency('fontconfig')
dep_freetype2 = dependency('freetype2')
dep_x11 = dependency('x11')
dep_xft = dependency('xft')
dep_xinerama = dependency('xinerama')
dep_xrender = dependency('xrender')

cc = meson.get_compiler('c')
dep_m = cc.find_library('m')
dep_rt = cc.find_library('rt')
dep_util = cc.find_library('util')

# -- dmenu -- #
dmenu_src = [
    'dmenu/dmenu.c',
    'dmenu/drw.c',
    'dmenu/util.c'
]

stest_src = [
    'dmenu/stest.c'
]

dmenu_deps = [
    dep_fontconfig,
    dep_x11,
    dep_xft,
    dep_xinerama
]

dmenu_extra = [
    '-DVERSION="5.2-landfill"',
    '-DXINERAMA',
    '-D_BSD_SOURCE',
    '-D_DEFAULT_SOURCE',
    '-D_POSIX_C_SOURCE=200809L',
    '-D_XOPEN_SOURCE=700'
]

configure_file(
    input: 'config/dmenu_conf.h.in',
    output: 'dmenu_conf.h',
    configuration: conf
)

executable('dmenu', dmenu_src,
    dependencies: dmenu_deps,
    c_args: dmenu_extra,
    install: true
)

executable('stest', stest_src,
    c_args: dmenu_extra,
    install: true
)

install_data(
    [
        'dmenu/dmenu_path',
        'dmenu/dmenu_run'
    ],
    install_dir: get_option('bindir')
)

# -- dwm -- #
dwm_src = [
    'dwm/drw.c',
    'dwm/dwm.c',
    'dwm/util.c'
]

dwm_deps = [
    dep_fontconfig,
    dep_x11,
    dep_xft,
    dep_xinerama
]

dwm_extra = [
    '-DVERSION="6.4-landfill"',
    '-DXINERAMA',
    '-D_BSD_SOURCE',
    '-D_DEFAULT_SOURCE',
    '-D_XOPEN_SOURCE=700L'
]

configure_file(
    input: 'config/dwm_conf.h.in',
    output: 'dwm_conf.h',
    configuration: conf
)

executable('dwm', dwm_src,
    dependencies: dwm_deps,
    c_args: dwm_extra,
    install: true
)

# -- st -- #
st_src = [
    'st/st.c',
    'st/x.c'
]

st_deps = [
    dep_fontconfig,
    dep_freetype2,
    dep_m,
    dep_rt,
    dep_util,
    dep_x11,
    dep_xft,
    dep_xrender
]

st_extra = [
    '-DVERSION="0.9-landfill"',
    '-D_XOPEN_SOURCE=600'
]

configure_file(
    input: 'config/st_conf.h.in',
    output: 'st_conf.h',
    configuration: conf
)

executable('st', st_src,
    dependencies: st_deps,
    c_args: st_extra,
    install: true
)
