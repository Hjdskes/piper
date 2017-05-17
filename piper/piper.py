#!/usr/bin/python3
# vim: set expandtab shiftwidth=4 tabstop=4

from ratbagd import *
import os

import gi
gi.require_version('Gio', '2.0')
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gio

class Piper(Gtk.Window):

    def _show_error(self, message):
        box = self._builder.get_object("piper-error-box")

        btn = self._builder.get_object("piper-error-button")
        btn.connect("clicked", Gtk.main_quit)

        error = self._builder.get_object("piper-error-body-label")
        error.set_text(message)

        self.add(box)
        self.show()

    def _show_btnmap_dialog(self, button):
        dialog = self._builder.get_object("piper-btnmap-dialog")
        dialog.set_transient_for(self)

        sb = self._builder.get_object("piper-btnmap-btnmap-spinbutton")
        sb.connect("value-changed", self.on_btnmap_changed, button)

        c = self._builder.get_object("piper-btnmap-custommap-combo")
        # select the currently selected function
        tree = c.get_model()
        it = tree.get_iter_first()
        while it:
            v = button.special
            if tree.get_value(it, 1) == v:
                c.set_active_iter(it)
                break;
            it = tree.iter_next(it)
        if it == None:
            c.set_active_iter(tree.get_iter_first())

        c.connect("changed", self.on_custommap_changed, button)

        radio = self._builder.get_object("piper-btnmap-btnmap-radio")
        radio.connect("toggled", self.on_actiontype_changed_button, button)
        radio.set_active(button.action_type == "button")

        radio = self._builder.get_object("piper-btnmap-keymap-radio")
        radio.connect("toggled", self.on_actiontype_changed_key, button)
        radio.set_active(button.action_type == "key")

        radio = self._builder.get_object("piper-btnmap-keyseqmap-radio")
        radio.connect("toggled", self.on_actiontype_changed_macro, button)
        radio.set_active(button.action_type == "macro")

        radio = self._builder.get_object("piper-btnmap-custommap-radio")
        radio.connect("toggled", self.on_actiontype_changed_special, button)
        radio.set_active(button.action_type == "special")

        response = dialog.run()

        self._update_from_device()

        dialog.hide()

    def __init__(self):
        Gtk.Window.__init__(self, title="Piper")
        main_window = Gtk.Builder()
        main_window.add_from_resource("/org/freedesktop/Piper/piper.ui")
        self._builder = main_window;
        self._signal_ids = []
        self._initialized = False
        self._button_function_labels = []

        self._ratbag_device = self._fetch_ratbag_device()
        if self._ratbag_device == None:
            return

        self._profile_buttons = []
        self._current_profile = self._ratbag_device.active_profile

        grid = main_window.get_object("piper-grid")
        self._init_header(self._ratbag_device)
        self.add(grid)

        # load the right image
        svg = self._ratbag_device.svg_path
        img = main_window.get_object("piper-image-device")
        if not os.path.isfile(svg):
            img.set_from_resource("/org/freedesktop/Piper/404.svg")
        else:
            img.set_from_file(svg)

        # init the current profile's data
        p = self._current_profile
        self._init_report_rate(main_window, p)
        self._init_resolution(main_window, p)
        self._init_buttons(main_window, p)

        self._update_from_device()
        self._connect_signals()
        self._initialized = True

        self.connect("delete-event", Gtk.main_quit)
        self.show()

    def  _init_header(self, device):
        hb = Gtk.HeaderBar()
        hb.set_show_close_button(True)
        hb.props.title = "{}".format(device.description)
        self.set_titlebar(hb)

        # apply/reset buttons
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        Gtk.StyleContext.add_class(box.get_style_context(), "linked")

        button = Gtk.Button()
        icon = Gio.ThemedIcon(name="edit-undo-symbolic")
        image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
        button.add(image)
        button.connect("clicked", self.on_button_reset_clicked)
        box.add(button)

        button = Gtk.Button()
        icon = Gio.ThemedIcon(name="document-save-symbolic")
        image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
        button.add(image)
        button.connect("clicked", self.on_button_save_clicked)
        box.add(button)

        hb.pack_end(box)

        # Profile buttons
        profiles = device.profiles
        if len(profiles) > 1:
            box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
            Gtk.StyleContext.add_class(box.get_style_context(), "linked")

            for i, p in enumerate(profiles):
                button = Gtk.ToggleButton("Profile {}".format(i))
                box.add(button)
                self._profile_buttons.append(button)
            hb.pack_start(box)

        hb.show_all()

    def _fetch_ratbag_device(self):
        """
        Get the first ratbag device available. If there are multiple
        devices, an error message is printed and we default to the first
        one.
        Otherwise, an error is shown and we return None.
        """
        try:
            ratbag = Ratbagd()
        except RatbagdDBusUnavailable:
            ratbag = None

        if ratbag == None:
            self._show_error("Can't connect to ratbagd on DBus. That's quite unfortunate.")
            return None
        if len(ratbag.devices) == 0:
            self._show_error("Could not find any devices. Do you have anything vaguely mouse-looking plugged in?")
            return None

        if len(ratbag.devices) > 1:
            print("Ooops, can't deal with more than one device. My bad.")
            for d in ratbag.devices[1:]:
                print("Ignoring device {}".format(d.name))

        d = ratbag.devices[0]
        p = d.profiles
        if len(p) == 1 and len(p[0].resolutions) == 1:
            self._show_error("Device {} does not support switchable resolutions".format(d.name))
            return None

        return d

    def _init_resolution(self, builder, profile):
        res = profile.resolutions
        nres = len(profile.resolutions)

        self._resolution_buttons = []
        self._resolution_adjustments = []
        for i in range(0, 5):
            sb = builder.get_object("piper-xres-spinbutton{}".format(i + 1))
            self._resolution_buttons.append(sb)
            adj = builder.get_object("piper-xres-adjustment{}".format(i + 1))
            self._resolution_adjustments.append(adj)

        nres_spin = builder.get_object("piper-nresolutions-spin")
        self._nres_button = nres_spin
        nres_spin.set_range(1, nres)

    def _init_report_rate(self, builder, profile):
        # Note: we simplify here, the UI only allows one report rate and it
        # will be applied to all resolutions
        rate = profile.active_resolution.report_rate
        r500 = builder.get_object("piper-report-rate-500")
        r1000 = builder.get_object("piper-report-rate-1000")
        r500.connect("toggled", self.on_resolution_rate_changed, 500)
        r1000.connect("toggled", self.on_resolution_rate_changed, 1000)

        self._rate_buttons = { 500 : r500,
                               1000 : r1000 }

    def _init_buttons(self, builder, profile):
        lb = builder.get_object("piper-buttons-listbox")
        lb.remove(builder.get_object("piper-button-listboxrow"))

        for i, b in enumerate(profile.buttons):
            lbr = self._init_button_row(b)
            lb.add(lbr)

        self._set_button_row_function_labels(profile)

        lb.show_all()

    def _init_button_row(self, button):
        # FIXME: can't I duplicate this from builder?
        lbr = Gtk.ListBoxRow()
        lbr.height_request = 80
        lbr.width_request = 100
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        l1 = Gtk.Label()
        l1.set_markup("<b>Button {}</b>".format(button.index))
        l1.set_margin_left(12)
        l1.set_margin_top(8)
        l1.set_margin_bottom(8)
        l1.height_request = 32
        box.add(l1)

        l2 = Gtk.Label("...function...")
        l2.set_justify(Gtk.Justification.LEFT)
        l2.set_hexpand(True)
        l2.set_margin_left(12)
        l2.set_xalign(0)
        box.add(l2)
        self._button_function_labels.append(l2)

        btn = Gtk.Button("...")
        btn.connect("clicked", self.on_button_click, button)
        box.add(btn)
        lbr.add(box)
        return lbr

    def _set_button_row_function_labels(self, profile):
        buttons = profile.buttons
        for l, button in zip(self._button_function_labels, buttons):
            action = button.action_type
            if action == "button":
                text = "Button {} click".format(button.button)
            elif action == "key":
                text = "Key event: {}".format(button.key[0])
            elif action == "macro":
                text = "Macro (unsupported, sorry)"
            elif action == "special":
                v = button.special
                c = self._builder.get_object("piper-btnmap-custommap-combo")
                tree = c.get_model()
                it = tree.get_iter_first()
                while it:
                    if tree.get_value(it, 1) == v:
                        text = "{}".format(tree[it][0])
                        break;
                    it = tree.iter_next(it)

                if it == None:
                    text = "Unknown special {}".format(v)
            else:
                text = "!help, I'm confused!"

            l.set_text(text)


    def _connect_signals(self):
        """
        Connect signals for those buttons that cause a write to the device.
        We do this separate so we can disconnect them again before we update
        the profile from the device. Otherwise, any widget.set_value() will
        trigger the matching callback and tries to write to the device.
        """
        s = []
        for i, b in enumerate(self._resolution_buttons):
            s.append(b.connect("value-changed", self.on_resolutions_changed, i))

        s.append(self._nres_button.connect("value-changed", self.on_nresolutions_changed, self._builder))

        for i, b in enumerate(self._profile_buttons):
            s.append(b.connect("toggled", self.on_button_profile_toggled, i))

        self._signal_ids = []

    def _disconnect_signals(self):
        """
        Disconnect all previously connected signals.
        """
        for s in self._signal_ids:
            self.disconnect(s)
        self._signal_ids = []

    def on_resolution_rate_changed(self, widget, new_rate):
        if not widget.get_active():
            return

        res = self._current_profile.active_resolution.report_rate = new_rate

    def on_nresolutions_changed(self, widget, builder):
        nres = widget.get_value_as_int()
        for i in range(0, 5):
            sb = builder.get_object("piper-xres-spinbutton{}".format(i + 1))
            sb.set_sensitive(nres > i)

        self._adjust_sensitivity_ranges()

    def on_resolutions_changed(self, widget, index):
        self._adjust_sensitivity_ranges()
        value = widget.get_value()
        self._current_profile.resolutions[index].resolution = (value, value)

    def on_button_save_clicked(self, widget):
        print("FIXME: I should save this to the device now")

    def on_button_reset_clicked(self, widget):
        self._update_from_device()

    def on_button_profile_toggled(self, widget, idx):
        if not widget.get_active():
            return

        self._disconnect_signals()

        for b in self._profile_buttons:
            if b != widget:
                b.set_active(False)

        self._current_profile = self._ratbag_device.profiles[idx]
        self._update_from_device()

        if self._initialized:
            self._connect_signals()

    def on_button_click(self, widget, button):
        self._show_btnmap_dialog(button)

    def on_btnmap_changed(self, widget, button):
        b = self._builder.get_object("piper-btnmap-btnmap-spinbutton").get_value_as_int()
        button.button = b

    def _custommap_combo_value(self):
        combo = self._builder.get_object("piper-btnmap-custommap-combo")
        tree_iter = combo.get_active_iter()
        if tree_iter != None:
            model = combo.get_model()
            val = model[tree_iter][1]
            return val
        return None

    def on_custommap_changed(self, widget, button):
        radio = self._builder.get_object("piper-btnmap-custommap-radio")
        radio.set_active(True)

        val = self._custommap_combo_value()
        if val:
            button.special = val

    def on_actiontype_changed_button(self, widget, button):
        if not widget.get_active():
            return

        b = self._builder.get_object("piper-btnmap-btnmap-spinbutton").get_value_as_int()
        button.button = b

    def on_actiontype_changed_key(self, widget, button):
        if not widget.get_active():
            return
        print("FIXME: change to key")

    def on_actiontype_changed_macro(self, widget, button):
        if not widget.get_active():
            return
        print("FIXME: change to macro")

    def on_actiontype_changed_special(self, widget, button):
        val = self._custommap_combo_value()
        if val:
            button.special = val

    def _adjust_sensitivity_ranges(self):
        """
        Align the five sensitivity ranges so that the right-most one can
        go to 1200, the left-most one to 200. In between they're bound by
        the previous/next one so the order is always ascending
        """
        nres = self._nres_button.get_value_as_int() - 1

        min, max = 200, 12000

        adj = self._resolution_adjustments
        while nres >= 0:
            a1 = adj[nres]
            a1.set_upper(max)
            v = int(a1.get_value())
            if v != 0:
                max = v

            if nres > 0:
                a2 = adj[nres - 1]
                min = a2.get_value()
            else:
                min = 200

            a1.set_lower(min)
            nres -= 1

    def _update_from_device(self):
        device = self._ratbag_device
        profile = self._current_profile

        for i, b in enumerate(self._profile_buttons):
            if device.profiles[i] == self._current_profile:
                b.set_active(True)
            else:
                b.set_active(False)

        rate = profile.active_resolution.report_rate
        for r, b in self._rate_buttons.items():
            b.set_active(r == rate)

        if not rate in self._rate_buttons.keys():
            print("Ooops, rate is {} and I don't know how to deal with that.".format(rate))
            for b in self._rate_buttons.values():
                b.set_sensitive(False)

        res = profile.resolutions
        nres = len(res)

        for i, b in enumerate(self._resolution_buttons):
            if i >= nres:
                b.set_visible(False)
                continue

            xres = res[i].resolution[0]
            b.set_value(xres)

        self._nres_button.set_value(nres)
        self._adjust_sensitivity_ranges()
        self._set_button_row_function_labels(profile)

class PiperImage(Gtk.EventBox):
    def __init__(self, path):
        Gtk.EventBox.__init__(self)
        self._image = Gtk.Image()
        self._image.set_from_file(path)
        self.add(self._image)
        self.connect("button-press-event", self.on_button_clicked)

    def on_button_clicked(self, widget, event):
        print(event.x)

