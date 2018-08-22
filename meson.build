project('piper',
	version: '0.2.901',
	license: 'GPLv2',
	meson_version: '>= 0.40.0')

# Dependencies
dependency('python3', required: true)
dependency('pygobject-3.0', required: true)
if not get_option('ignore-ratbagd-dependency')
    ratbagd = find_program('ratbagd', required: false)
    if not ratbagd.found()
      error('Dependency libratbag not found!')
    endif
endif

# Gtk version required
gtk_major_version = 3
gtk_minor_version = 22

prefix = get_option('prefix')
datadir = join_paths(prefix, get_option('datadir'))
localedir = join_paths(prefix, get_option('localedir'))
pkgdatadir = join_paths(datadir, meson.project_name())
bindir = join_paths(prefix, get_option('bindir'))

subdir('data')
subdir('po')

# Find the directory to install our Python code
python = import('python3')
py3 = python.find_python()
message('Getting Python3 install dir')
python_dir = python.sysconfig_path('purelib')
if not python_dir.endswith('site-packages')
	error('Python3 purelib path seems invalid')
endif
install_subdir('piper', install_dir: python_dir)

config_piper = configuration_data()
config_piper.set('pkgdatadir', pkgdatadir)
config_piper.set('localedir', localedir)
config_piper.set('gtk_major_version', gtk_major_version)
config_piper.set('gtk_minor_version', gtk_minor_version)
config_piper.set('devel', '')

config_piper_devel = config_piper
config_piper_devel.set('pkgdatadir', join_paths(meson.build_root(), 'data'))
config_piper_devel.set('localedir', join_paths(meson.build_root(), 'po'))
config_piper_devel.set('devel', '''
sys.path.insert(1, '@0@')
print('Running from source tree, using local files')
'''.format(meson.source_root()))

configure_file(input: 'piper.in',
	       output: 'piper',
	       configuration: config_piper,
	       install_dir: bindir)

configure_file(input: 'piper.in',
	       output: 'piper.devel',
	       configuration: config_piper_devel)

meson.add_install_script('meson_install.sh')
