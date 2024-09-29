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

conf = configuration_data()
setboxes = get_option('setboxes')
message('- setboxes:', setboxes)

if get_option('landfill')
    message('- landfill:')

    fontname = get_option('fontname')
    dmenufontsize = get_option('dmenufontsize')
    dwmfontsize = get_option('dwmfontsize')
    stfontsize = get_option('stfontsize')

    message(' - font name      :', fontname)
    message(' - dmenu font size:', dmenufontsize)
    message(' - dwm font size  :', dwmfontsize)
    message(' - st font size   :', stfontsize)

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

    subdir('landfill')
else
    message('- landfill: not building')
endif

subdir('utils')
