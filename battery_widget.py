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
        self.set_type_hint(Gdk.WindowTypeHint.UTILITY)
        self.set_accept_focus(False)

        self.low_battery_count = 0

        # Transparent background
        screen = self.get_screen()
        visual = screen.get_rgba_visual()
        if visual and self.is_composited():
            self.set_visual(visual)

        # CSS styling
        css = b"""
        #battery-box {
            background-color: rgba(30, 30, 30, 0.8);
            border-radius: 12px;
            padding: 4px 8px;
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

        # Layout
        box = Gtk.Box(spacing=6)
        box.set_name("battery-box")
        self.label = Gtk.Label()
        box.pack_start(self.label, True, True, 0)
        self.add(box)

        # Position bottom-right initially
        monitor_geo = screen.get_monitor_geometry(screen.get_primary_monitor())
        self.move(monitor_geo.width - 120, monitor_geo.height - 50)

        # Allow dragging
        self.connect("button-press-event", self.on_mouse_press)

        GLib.timeout_add_seconds(1, self.update_battery)
        self.update_battery()

    def on_mouse_press(self, widget, event):
        if event.type == Gdk.EventType.BUTTON_PRESS and event.button == 1:
            self.begin_move_drag(event.button, int(event.x_root), int(event.y_root), event.time)

    def update_battery(self):
        battery = psutil.sensors_battery()
        if battery:
            percent = min(round(battery.percent, 1), 100.0)

            if battery.power_plugged:
                icon = "⚡"
                self.low_battery_count = 0
            elif percent <= 20:
                icon = "🪫"
                if self.low_battery_count < 3:
                    Notify.Notification.new(
                        "Low Battery",
                        f"Battery is at {percent:.1f}%! Plug in your charger.",
                        None
                    ).show()
                    self.low_battery_count += 1
            else:
                icon = "🔋"
                self.low_battery_count = 0

            self.label.set_text(f"{icon} {percent:.1f}%")

        return True

win = BatteryWidget()
win.show_all()
Gtk.main()
