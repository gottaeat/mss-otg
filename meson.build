project(
    'otg',
    ['c'],
    version: '1.1',
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
setboxes = get_option('setboxes')
landfill = get_option('landfill')

# checks
if setboxes
    if not is_linux
        error('setboxes can be toggled on only on linux')
    endif

    if not landfill
        error('setboxes requires landfill')
    endif
endif

if landfill
    if not is_linux
        error('landfill can only be built on linux')
    endif

    if not setboxes
        error('landfill requires setboxes')
    endif
endif

# mssdir + msshomedir
mssdir = get_option('mssdir')
msshomedir = get_option('msshomedir')
conf.set('mssdir', mssdir)
conf.set('msshomedir', msshomedir)

# prints
message('- mssdir    :', mssdir)
message('- msshomedir:', msshomedir)
message('- setboxes  :', setboxes)

# landfill
if landfill

    fontname = get_option('fontname')
    dmenufontsize = get_option('dmenufontsize')
    dwmfontsize = get_option('dwmfontsize')
    stfontsize = get_option('stfontsize')

    conf.set('fontname', fontname)
    conf.set('dmenufontsize', dmenufontsize)
    conf.set('dwmfontsize', dwmfontsize)
    conf.set('stfontsize', stfontsize)

    cc = meson.get_compiler('c')

    add_project_arguments(
        cc.get_supported_arguments(
            ['-fno-builtin']
        ),
        language : ['c']
    )

    message('- landfill  :')
    message(' - font name      :', fontname)
    message(' - dmenu font size:', dmenufontsize)
    message(' - dwm font size  :', dwmfontsize)
    message(' - st font size   :', stfontsize)

    subdir('landfill')
else
    message('- landfill  : not building')
endif

# utils
subdir('utils')
