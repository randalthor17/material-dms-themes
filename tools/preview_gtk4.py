#!/usr/bin/env python3
"""A libadwaita window with the widgets the theme styles, for tools/render.sh and for looking at by hand."""
import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw, Gtk  # noqa: E402


def on_activate(app):
    win = Adw.ApplicationWindow(application=app, default_width=1000, default_height=760)
    view = Adw.ToolbarView()
    header = Adw.HeaderBar()
    view.add_top_bar(header)
    box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=24, margin_top=16, margin_bottom=16,
                  margin_start=16, margin_end=16)

    col = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
    row = Gtk.Box(spacing=8)
    suggested = Gtk.Button(label="Filled")
    suggested.add_css_class("suggested-action")
    danger = Gtk.Button(label="Delete")
    danger.add_css_class("destructive-action")
    flat = Gtk.Button(label="Text")
    flat.add_css_class("flat")
    for b in (Gtk.Button(label="Tonal"), suggested, danger, flat):
        row.append(b)
    col.append(row)
    entry = Gtk.Entry(placeholder_text="Filled text field")
    col.append(entry)
    focused = Gtk.Entry(text="Focused field")
    col.append(focused)
    focused.grab_focus()
    col.append(Gtk.SearchEntry(placeholder_text="Search"))
    for state in (False, True):
        r = Gtk.Box(spacing=12)
        r.append(Gtk.Switch(active=state))
        r.append(Gtk.CheckButton(label="Check", active=state))
        radio = Gtk.CheckButton(label="Radio", active=state, group=Gtk.CheckButton())
        r.append(radio)
        col.append(r)
    col.append(Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 100, 1))
    col.get_last_child().set_value(40)
    pb = Gtk.ProgressBar(fraction=.6)
    col.append(pb)
    col.append(Gtk.DropDown.new_from_strings(["One", "Two", "Three"]))
    col.append(Gtk.SpinButton.new_with_range(0, 10, 1))
    box.append(col)

    lst = Gtk.ListBox(selection_mode=Gtk.SelectionMode.SINGLE)
    lst.add_css_class("boxed-list")
    for i in range(5):
        lst.append(Adw.ActionRow(title=f"Row {i + 1}", subtitle="A description"))
    lst.select_row(lst.get_row_at_index(1))
    scroller = Gtk.ScrolledWindow(hexpand=True, vexpand=True)
    right = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
    right.append(lst)
    nb = Gtk.Notebook()
    for t in ("Tab one", "Tab two"):
        nb.append_page(Gtk.Label(label=t, margin_top=24, margin_bottom=24), Gtk.Label(label=t))
    right.append(nb)
    toggle = Gtk.ToggleButton(label="Toggled", active=True)
    right.append(toggle)
    scroller.set_child(right)
    box.append(scroller)
    view.set_content(box)
    win.set_content(view)
    win.present()


app = Adw.Application(application_id="dev.material_dms_themes.Preview")
app.connect("activate", on_activate)
app.run()
