project('piper',
	version: '0.2.1',
	license: 'GPLv2',
	meson_version: '>= 0.40.0')

# Dependencies
dependency('python3', required: true)
dependency('pygobject-3.0', required: true)
#TODO: soon this will need to be >= 0.4 with the addition of signals
#dependency('ratbagd', required: true, version: '>= 0.3')

datadir = get_option('datadir')
pkgdatadir = join_paths(datadir, meson.project_name())

subdir('data')

# Find the directory to install our Python code
python = import('python3')
py3 = python.find_python()
message('Getting Python3 install dir')
python_dir = python.sysconfig_path('purelib')
if not python_dir.endswith('site-packages')
	error('Python3 purelib path seems invalid')
endif
install_subdir('piper', install_dir: python_dir)

conf = configuration_data()
# Not sure why it is necessary to explicitly handle the prefix here...
conf.set('pkgdatadir', join_paths(get_option('prefix'), pkgdatadir))

configure_file(input: 'piper.in',
	       output: 'piper',
	       configuration: conf,
	       install_dir: 'bin')

# TODO: Is still needed?
#meson.set_install_script('meson_install.sh')
