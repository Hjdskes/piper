#!/usr/bin/env sh

# Update icon cache
gtk-update-icon-cache -f -t ${DESTDIR}/${MESON_INSTALL_PREFIX}/share/icons/hicolor

# Install new schemas
#glib-compile-schemas ${DESTDIR}/${MESON_INSTALL_PREFIX}/share/glib-2.0/schemas/
