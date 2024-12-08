project(
    'otg',
    ['c'],
    version: '1.3',
    license: 'MIT',
    default_options: [
        'buildtype=plain',
        'prefix=/usr',
        'c_std=c99'
    ]
)

# init config
conf = configuration_data()

# is_linux
is_linux = host_machine.system() == 'linux'

if is_linux
    conf.set('is_linux', 1)
else
    conf.set('is_linux', 0)
endif

setboxes = get_option('setboxes')
landfill = get_option('landfill')
build_st = get_option('st')
build_dwm = get_option('dwm')
build_dmenu = get_option('dmenu')

# checks
if setboxes
    if not is_linux
        error('setboxes can be toggled on only on linux')
    endif

    conf.set('is_setboxes', 1)
else
    conf.set('is_setboxes', 0)
endif

if landfill
    if not is_linux
        error('landfill can only be built on linux')
    endif

    if not setboxes
        error('landfill requires setboxes')
    endif
else
    if build_st or build_dwm or build_dmenu
        error('cannot build st, dwm, or dmenu without landfill being enabled')
    endif
endif

if build_dwm
    if build_st
        conf.set('dwm_terminal', 'st')
    else
        conf.set('dwm_terminal', 'alacritty')
    endif
endif

# mssdir + msshomedir
mssdir = get_option('mssdir')
msshomedir = get_option('msshomedir')
conf.set('mssdir', mssdir)
conf.set('msshomedir', msshomedir)

# landfill
if landfill
    fontname = get_option('fontname')
    fontsize = get_option('fontsize')

    conf.set('fontname', fontname)
    conf.set('fontsize', fontsize)

    cc = meson.get_compiler('c')

    add_project_arguments(
        cc.get_supported_arguments(
            ['-fno-builtin']
        ),
        language : ['c']
    )

    subdir('landfill')
endif

# utils
subdir('utils')

# prints
message('> mssdir     :', mssdir)
message('> msshomedir :', msshomedir)
message('> setboxes   :', setboxes)

if landfill
    message('> landfill   :')
    message('  - font name:', fontname)
    message('  - font size:', fontsize)
    message('  - building :')
    message('    ! st     :', build_st)
    message('    ! dwm    :', build_dwm)
    message('    ! dmenu  :', build_dmenu)
else
    message('> landfill   : not building')
endif
