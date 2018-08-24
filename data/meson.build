gnome = import('gnome')

desktopdir = join_paths(datadir, 'applications')
icondir = join_paths(datadir, 'icons', 'hicolor', 'scalable', 'apps')
metainfodir = join_paths(datadir, 'metainfo')

conf = configuration_data()
conf.set('version', meson.project_version())
conf.set('url', 'https://github.com/libratbag/piper')

about_dialog = configure_file(input: 'ui/AboutDialog.ui.in',
			      output: 'AboutDialog.ui',
			      configuration: conf)

gnome.compile_resources('piper', 'piper.gresource.xml',
			source_dir: '.',
			dependencies: [about_dialog],
			gresource_bundle: true,
			install: true,
			install_dir: pkgdatadir)

install_data('org.freedesktop.Piper.desktop', install_dir: desktopdir)
install_data('org.freedesktop.Piper.svg', install_dir: icondir)

appdata = configure_file(input: 'org.freedesktop.Piper.appdata.xml.in',
                         output: 'org.freedesktop.Piper.appdata.xml',
                         configuration: conf,
                         install_dir: metainfodir)
