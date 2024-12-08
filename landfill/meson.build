conf.set('fontname', get_option('fontname'))
conf.set('fontsize', get_option('fontsize'))

deps = {
    'fontconfig': dependency('fontconfig'),
    'freetype2': dependency('freetype2'),
    'x11': dependency('x11'),
    'xft': dependency('xft'),
    'xinerama': dependency('xinerama'),
    'xrender': dependency('xrender'),
    'm': cc.find_library('m'),
    'rt': cc.find_library('rt'),
    'util': cc.find_library('util')
}

common_args = [
    '-D_BSD_SOURCE',
    '-D_DEFAULT_SOURCE',
    '-DXINERAMA'
]

if build_dmenu
    subdir('dmenu')
endif

if build_dwm
    subdir('dwm')
endif

if build_st
    subdir('st')
endif
