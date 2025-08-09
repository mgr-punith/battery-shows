#!/usr/bin/env python3
import gi, psutil
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GLib, Notify

Notify.init("Battery Alert")

class BatteryWidget(Gtk.Window):
    def __init__(self):
        super().__init__()
        self.set_decorated(False)
        self.set_app_paintable(True)
        self.set_keep_above(True)
        self.set_resizable(False)
        self.set_type_hint(Gdk.WindowTypeHint.DOCK)

        # Transparent window
        screen = self.get_screen()
        visual = screen.get_rgba_visual()
        if visual and self.is_composited():
            self.set_visual(visual)

        # CSS style
        css = b"""
        #battery-box {
            background-color: rgba(30, 30, 30, 0.8);
            border-radius: 12px;
            padding: 6px 10px;
        }
        label {
            color: white;
            font-weight: bold;
            font-size: 14px;
        }
        """
        style_provider = Gtk.CssProvider()
        style_provider.load_from_data(css)
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            style_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        # Widget
        box = Gtk.Box()
        box.set_name("battery-box")
        self.label = Gtk.Label()
        box.pack_start(self.label, True, True, 0)
        self.add(box)

        # Position bottom-right
        monitor_geo = screen.get_monitor_geometry(screen.get_primary_monitor())
        self.move(monitor_geo.width - 120, monitor_geo.height - 50)

        # Update every second
        GLib.timeout_add_seconds(1, self.update_battery)
        self.update_battery()

    def update_battery(self):
        battery = psutil.sensors_battery()
        if battery:
            percent = round(battery.percent, 1)  # One decimal place

            if battery.power_plugged:
                icon = "⚡︎"
            elif percent <= 20:
                icon = "🪫"
            else:
                icon = ""

            self.label.set_text(f"{icon} {percent:.1f}%")

            if percent <= 20 and not battery.power_plugged:
                Notify.Notification.new(
                    "Low Battery",
                    f"Battery is at {percent:.1f}%! Plug in your charger.",
                    None
                ).show()
        return True

win = BatteryWidget()
win.show_all()
Gtk.main()
