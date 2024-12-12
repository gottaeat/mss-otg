project(
    'otg',
    ['c'],
    version: '1.3',
    license: 'MIT',
    default_options: [
        'prefix=/usr'
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

# checks
if setboxes
    if not is_linux
        error('setboxes can be toggled on only on linux')
    endif

    conf.set('is_setboxes', 1)
else
    conf.set('is_setboxes', 0)
endif

# mssdir + msshomedir
mssdir = get_option('mssdir')
msshomedir = get_option('msshomedir')
conf.set('mssdir', mssdir)
conf.set('msshomedir', msshomedir)

# utils
subdir('utils')

# prints
message('> mssdir     :', mssdir)
message('> msshomedir :', msshomedir)
message('> setboxes   :', setboxes)
