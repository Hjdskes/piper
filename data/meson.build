gnome = import('gnome')

desktopdir = join_paths(datadir, 'applications')
icondir = join_paths(datadir, 'icons', 'hicolor', 'scalable', 'apps')

gnome.compile_resources('piper', 'piper.gresource.xml',
			source_dir: '.',
			gresource_bundle: true,
			install: true,
			install_dir: pkgdatadir)

install_data('piper.desktop', install_dir: desktopdir)
install_data('piper.svg', install_dir: icondir)
