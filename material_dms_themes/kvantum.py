"""The Kvantum theme: SVG elements and kvconfig drawn like DankMaterialShell, in the palette's colors.

Kvantum draws a widget from nine SVG objects per state (an interior and eight frame pieces, NAME-STATE[-top|-bottom|
-left|-right|-topleft|...]), each scaled to its place, so every piece is its own object with exact bounds. Element
names and config keys follow Kvantum's documentation. Shapes and numbers follow DMS: pill buttons, 4 px filled text
fields with a 2 px primary ring on focus, 12 px items, 16 px popups, state layers of 8% (hover) and 10% (pressed).
"""
from .palette import Palette, mix

STATES = ["normal", "focused", "pressed", "toggled", "disabled"]
EDGE = 10


class Svg:
    def __init__(self):
        self.parts, self.x, self.y, self.row, self.ids = [], 0, 0, 0, set()

    def place(self, w, h):
        if self.x + w > 1600:
            self.x, self.y, self.row = 0, self.y + self.row + 8, 0
        x, y = self.x, self.y
        self.x += w + 8
        self.row = max(self.row, h)
        return x, y

    def obj(self, name, x, y, w, h, shapes):
        assert name not in self.ids, name
        self.ids.add(name)
        self.parts.append(f'<g id="{name}"><rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#000000" '
                          f'fill-opacity="0"/>{"".join(shapes)}</g>')

    def text(self):
        return ('<?xml version="1.0" encoding="UTF-8"?>\n<!-- Material DMS: generated, do not edit. -->\n'
                f'<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="{self.y + self.row + 8}">\n'
                + "\n".join(self.parts) + "\n</svg>\n")


def fill(color, opacity):
    return f'fill="{color}" fill-opacity="{opacity:g}"'


def rect(x, y, w, h, color, opacity):
    return f'<rect x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" {fill(color, opacity)}/>' if opacity > 0 else ""


def stroke(d, color, opacity, width):
    return (f'<path d="{d}" fill="none" stroke="{color}" stroke-opacity="{opacity:g}" stroke-width="{width:g}" '
            'stroke-linecap="round" stroke-linejoin="round"/>')


def corner(x, y, f, rad, where, bg, border):
    """The corner piece `where`: an f x f square at (x, y) rounded with rad at its outer corner."""
    def at(px, py):
        mx = f - px if "right" in where else px
        my = f - py if "bottom" in where else py
        return f"{x + mx:g},{y + my:g}"
    sweep = 1 if (("right" in where) == ("bottom" in where)) else 0
    out = []
    if bg and bg[1] > 0:
        if rad > 0:
            d = f"M{at(0, f)} L{at(0, rad)} A{rad:g},{rad:g} 0 0 {sweep} {at(rad, 0)} L{at(f, 0)} L{at(f, f)} Z"
        else:
            d = f"M{at(0, 0)} L{at(f, 0)} L{at(f, f)} L{at(0, f)} Z"
        out.append(f'<path d="{d}" {fill(*bg)}/>')
    if border and border[1] > 0:
        color, opacity, w = border
        h = w / 2
        r = max(rad - h, 0)
        if rad > 0:
            d = f"M{at(h, f)} L{at(h, rad)} A{r:g},{r:g} 0 0 {sweep} {at(rad, h)} L{at(f, h)}"
        else:
            d = f"M{at(h, f)} L{at(h, h)} L{at(f, h)}"
        out.append(f'<path d="{d}" fill="none" stroke="{color}" stroke-opacity="{opacity:g}" stroke-width="{w:g}"/>')
    return out


def box(svg, name, f, rad, bg=None, border=None, interior=True):
    """The nine objects of one state of a framed element."""
    x, y = svg.place(2 * f + EDGE, 2 * f + EDGE)
    L = EDGE
    edge_bg = (lambda *a: rect(*a, *bg)) if bg else (lambda *a: "")
    if interior:
        svg.obj(name, x + f, y + f, L, L, [edge_bg(x + f, y + f, L, L)])
    for where, (px, py) in {"topleft": (x, y), "topright": (x + f + L, y), "bottomleft": (x, y + f + L),
                            "bottomright": (x + f + L, y + f + L)}.items():
        svg.obj(f"{name}-{where}", px, py, f, f, corner(px, py, f, rad, where, bg, border))
    bw = border[2] if border else 0
    bline = (lambda *a: rect(*a, border[0], border[1])) if border else (lambda *a: "")
    svg.obj(f"{name}-top", x + f, y, L, f, [edge_bg(x + f, y, L, f), bline(x + f, y, L, bw)])
    svg.obj(f"{name}-bottom", x + f, y + f + L, L, f,
            [edge_bg(x + f, y + f + L, L, f), bline(x + f, y + f + L + f - bw, L, bw)])
    svg.obj(f"{name}-left", x, y + f, f, L, [edge_bg(x, y + f, f, L), bline(x, y + f, bw, L)])
    svg.obj(f"{name}-right", x + f + L, y + f, f, L,
            [edge_bg(x + f + L, y + f, f, L), bline(x + f + L + f - bw, y + f, bw, L)])


def element(svg, name, f, rad, looks, interior=True):
    for state, (bg, border) in looks.items():
        box(svg, f"{name}-{state}", f, rad, bg, border, interior)


def glyph(svg, name, size, shapes_at):
    x, y = svg.place(size, size)
    svg.obj(name, x, y, size, size, shapes_at(x, y))


STATE_ALPHA = {"normal": 1.0, "focused": 1.0, "pressed": 1.0, "toggled": 1.0, "disabled": 0.38}


def chevrons(svg, base, color):
    paths = {"down": "M4,6 L8,10 L12,6", "up": "M4,10 L8,6 L12,10", "right": "M6,4 L10,8 L6,12",
             "left": "M10,4 L6,8 L10,12"}
    for direction, d in paths.items():
        for state in STATES:
            glyph(svg, f"{base}-{direction}-{state}", 16, lambda x, y, d=d, s=state: [
                f'<g transform="translate({x},{y})">' + stroke(d, color, STATE_ALPHA[s], 1.75) + "</g>"])


def build(p: Palette):
    svg = Svg()
    FG, PRI, ON_PRI = p["on_surface"], p["primary"], p["on_primary"]
    SEC, ON_SEC = p["secondary_container"], p["on_secondary_container"]
    VAR, OUTV = p["on_surface_variant"], p["outline_variant"]
    HIGH, CONT = p["surface_container_high"], p["surface_container"]
    solid = lambda c: (c, 1)  # noqa: E731
    tint = lambda c, a: (c, a)  # noqa: E731
    hov = lambda base, on: solid(mix(base, on, .08))  # noqa: E731   DMS's hover state layer, pre-mixed
    prs = lambda base, on: solid(mix(base, on, .10))  # noqa: E731

    # buttons: tonal and pill-shaped (DMS's default); the default button is filled
    B = 14
    element(svg, "button", B, B, {"normal": (solid(SEC), None), "focused": (hov(SEC, ON_SEC), None),
                                  "pressed": (prs(SEC, ON_SEC), None), "toggled": (solid(PRI), None),
                                  "disabled": (tint(FG, .10), None)})
    element(svg, "tbutton", 12, 12, {"normal": (None, None), "focused": (tint(FG, .08), None),
                                     "pressed": (tint(FG, .10), None), "toggled": (solid(SEC), None),
                                     "disabled": (None, None)})
    flat8 = {"normal": (None, None), "focused": (tint(FG, .08), None), "pressed": (tint(FG, .10), None),
             "toggled": (None, None), "disabled": (None, None)}
    element(svg, "spin", 8, 8, flat8)
    element(svg, "header", 2, 0, flat8)
    element(svg, "tab", 12, 12, {**flat8, "focused": (tint(PRI, .08), None), "pressed": (tint(PRI, .10), None)})
    element(svg, "itemview", 8, 8, {**flat8, "toggled": (solid(SEC), None)})
    element(svg, "menuitem", 12, 12, {**flat8, "toggled": (tint(FG, .08), None)})
    element(svg, "menubaritem", 12, 12, {**flat8, "toggled": (tint(FG, .10), None)})
    # text fields: filled (container high), 4 px corners, 1 px outline-variant, a 2 px primary ring when focused
    ring = (PRI, 1, 2)
    element(svg, "lineedit", 6, 4, {"normal": (solid(HIGH), (OUTV, 1, 1)), "focused": (solid(HIGH), ring),
                                    "pressed": (solid(HIGH), ring), "toggled": (solid(HIGH), ring),
                                    "disabled": (tint(FG, .04), (FG, .12, 1))})
    element(svg, "common", 12, 12, {"normal": (None, (OUTV, 1, 1)), "disabled": (None, (OUTV, .5, 1))})
    element(svg, "group", 12, 12, {"normal": (solid(CONT), None)})
    element(svg, "tabframe", 12, 12, {"normal": (None, (OUTV, 1, 1))})
    element(svg, "menu", 16, 16, {"normal": (solid(CONT), (OUTV, .6, 1))})
    element(svg, "tooltip", 8, 8, {"normal": (solid(p["inverse_surface"]), None)})
    element(svg, "progress", 4, 4, {"normal": (solid(SEC), None), "disabled": (tint(FG, .12), None)})
    element(svg, "progress-pattern", 4, 4, {"normal": (solid(PRI), None), "focused": (solid(PRI), None),
                                            "disabled": (tint(FG, .38), None)})
    element(svg, "slider", 8, 8, {"normal": (tint(SEC, .6), None), "focused": (tint(SEC, .6), None),
                                  "pressed": (tint(SEC, .6), None), "toggled": (solid(PRI), None),
                                  "disabled": (tint(FG, .12), None)})
    element(svg, "scrollbarslider", 4, 4, {"normal": (tint(FG, .30), None), "focused": (tint(FG, .50), None),
                                           "pressed": (tint(FG, .70), None), "disabled": (tint(FG, .12), None)},
            interior=False)
    element(svg, "scrollgroove", 1, 0, {"normal": (None, None)})
    element(svg, "toolbar", 1, 0, {"normal": (None, None)})
    element(svg, "dock", 1, 0, {"normal": (solid(CONT), None)})
    element(svg, "titlebar", 1, 0, {"normal": (solid(p["surface"]), None), "focused": (solid(p["surface"]), None)})
    element(svg, "splitter", 1, 0, {"normal": (None, None), "focused": (tint(PRI, .3), None),
                                    "pressed": (tint(PRI, .5), None)})
    box(svg, "focus", 8, 8, None, (PRI, 1, 2), interior=False)

    # check boxes (18 px, 2 px corners, 2 px outline) and radios
    for kind in ("checkbox", "radio"):
        rad = 2 if kind == "checkbox" else 9
        for state in ("normal", "focused", "pressed", "disabled"):
            col = VAR if state == "normal" else FG
            a = .38 if state == "disabled" else 1
            glyph(svg, f"{kind}-{state}", 18, lambda x, y, col=col, a=a, rad=rad: [
                f'<rect x="{x + 1}" y="{y + 1}" width="16" height="16" rx="{max(rad - 1, 0)}" fill="none" '
                f'stroke="{col}" stroke-opacity="{a:g}" stroke-width="2"/>'])
            fillc = FG if state == "disabled" else (mix(PRI, ON_PRI, .08) if state == "focused" else PRI)
            fa = .38 if state == "disabled" else 1
            if kind == "checkbox":
                mark = lambda x, y: stroke(f"M{x + 4.5},{y + 9} L{x + 7.5},{y + 12} L{x + 13.5},{y + 6}", ON_PRI, 1, 2)  # noqa: E731
                dash = lambda x, y: stroke(f"M{x + 5},{y + 9} L{x + 13},{y + 9}", ON_PRI, 1, 2)  # noqa: E731
            else:
                mark = lambda x, y: f'<circle cx="{x + 9}" cy="{y + 9}" r="4" fill="{ON_PRI}"/>'  # noqa: E731
                dash = mark
            for suffix, m in (("checked", mark), ("tristate", dash)):
                glyph(svg, f"{kind}-{suffix}-{state}", 18, lambda x, y, m=m, fillc=fillc, fa=fa, rad=rad: [
                    f'<rect x="{x}" y="{y}" width="18" height="18" rx="{rad}" fill="{fillc}" fill-opacity="{fa:g}"/>',
                    m(x, y)])
    # slider handle: DMS's is a thin primary bar; Kvantum scales this box to length x width, so it fills it
    for state in ("normal", "focused", "pressed", "disabled"):
        col, o = (PRI, 1) if state != "disabled" else (FG, .38)
        glyph(svg, f"slidercursor-{state}", 20, lambda x, y, col=col, o=o: [
            f'<rect x="{x}" y="{y}" width="20" height="20" rx="3" fill="{col}" fill-opacity="{o:g}"/>'])
    glyph(svg, "slider-tick", 5, lambda x, y: [rect(x, y + 2, 5, 1, VAR, .6)])

    chevrons(svg, "arrow", FG)
    for state in STATES:
        glyph(svg, f"arrow-plus-{state}", 16, lambda x, y, s=state: [
            f'<g transform="translate({x},{y})">' + stroke("M6,4 L10,8 L6,12", FG, STATE_ALPHA[s], 1.75) + "</g>"])
        glyph(svg, f"arrow-minus-{state}", 16, lambda x, y, s=state: [
            f'<g transform="translate({x},{y})">' + stroke("M4,6 L8,10 L12,6", FG, STATE_ALPHA[s], 1.75) + "</g>"])
    for direction, d in {"right": "M6,4 L10,8 L6,12", "left": "M10,4 L6,8 L10,12"}.items():
        for state in ("normal", "focused", "pressed", "disabled"):
            glyph(svg, f"menuitem-{direction}-{state}", 16, lambda x, y, d=d, s=state: [
                f'<g transform="translate({x},{y})">' + stroke(d, FG, STATE_ALPHA[s], 1.75) + "</g>"])
    glyph(svg, "menuitem-separator", 10, lambda x, y: [rect(x, y + 4.5, 10, 1, OUTV, 1)])
    for state in ("normal", "focused"):
        glyph(svg, f"menuitem-tearoff-{state}", 10, lambda x, y: [rect(x, y + 4.5, 5, 1, OUTV, 1)])
    for state in STATES:
        bg = {"focused": .08, "pressed": .10}.get(state, 0)
        a = .38 if state == "disabled" else 1
        glyph(svg, f"tab-close-{state}", 16, lambda x, y, bg=bg, a=a: [
            f'<circle cx="{x + 8}" cy="{y + 8}" r="8" fill="{FG}" fill-opacity="{bg:g}"/>' if bg else "",
            stroke(f"M{x + 5},{y + 5} L{x + 11},{y + 11} M{x + 11},{y + 5} L{x + 5},{y + 11}", FG, a, 1.5)])
    glyph(svg, "tab-tear", 2, lambda x, y: [rect(x, y, 2, 2, FG, .2)])
    glyph(svg, "header-separator", 2, lambda x, y: [rect(x, y, 1, 2, OUTV, 1)])
    glyph(svg, "toolbar-separator", 4, lambda x, y: [rect(x + 1.5, y, 1, 4, OUTV, 1)])
    glyph(svg, "toolbar-handle", 8, lambda x, y: [])
    for state in ("normal", "focused", "pressed"):
        glyph(svg, f"splitter-grip-{state}", 16, lambda x, y: [])
        glyph(svg, f"grip-{state}", 13, lambda x, y: [])
    for state in ("normal", "focused"):
        glyph(svg, f"sizegrip-{state}", 13, lambda x, y: [
            f'<circle cx="{x + px}" cy="{y + py}" r="1" fill="{VAR}"/>'
            for px, py in ((11, 5), (8, 8), (11, 8), (5, 11), (8, 11), (11, 11))])
    glyph(svg, "button-default-indicator", 9, lambda x, y: [])
    marks = {"close": "M5,5 L11,11 M11,5 L5,11", "maximize": "M5,5 L11,5 L11,11 L5,11 Z",
             "restore": "M6,7 L11,7 L11,11 L6,11 Z M7,5 L12,5 L12,9", "minimize": "M5,11 L11,11",
             "shade": "M4,10 L8,6 L12,10"}
    for name, d in marks.items():
        for state in ("normal", "focused", "pressed", "disabled"):
            bg = {"normal": 0, "focused": .08, "pressed": .10, "disabled": 0}[state]
            glyph(svg, f"mdi-{name}-{state}", 16, lambda x, y, d=d, bg=bg: [
                f'<circle cx="{x + 8}" cy="{y + 8}" r="8" fill="{FG}" fill-opacity="{bg:g}"/>',
                f'<g transform="translate({x},{y})">' + stroke(d, FG, 1, 1.4) + "</g>"])
    glyph(svg, "mdi-menu-normal", 16, lambda x, y: [])
    glyph(svg, "dial", 32, lambda x, y: [f'<circle cx="{x + 16}" cy="{y + 16}" r="15" fill="{SEC}"/>'])
    glyph(svg, "dial-handle", 8, lambda x, y: [f'<circle cx="{x + 4}" cy="{y + 4}" r="3" fill="{PRI}"/>'])
    glyph(svg, "dial-notches", 32, lambda x, y: [])
    return svg


def config(p: Palette):
    """The kvconfig: geometry and behavior, the palette, and each widget's elements and text colors."""
    FG, PRI, ON_PRI = p["on_surface"], p["primary"], p["on_primary"]
    ON_SEC, VAR = p["on_secondary_container"], p["on_surface_variant"]
    text = lambda color=FG, **extra: {"text.normal.color": color, "text.focus.color": color,  # noqa: E731
                                      "text.press.color": color, "text.toggle.color": color, **extra}
    frame = lambda n, el=None, it=None: {"frame.top": n, "frame.bottom": n, "frame.left": n,  # noqa: E731
                                         "frame.right": n, **({"frame.element": el} if el else {}),
                                         **({"interior.element": it} if it else {})}
    sections = {
        "%General": {
            "author": "material-dms-themes", "comment": "Material 3 as DankMaterialShell draws it",
            "x11drag": "none", "alt_mnemonic": "true", "left_tabs": "true", "attach_active_tab": "false",
            "mirror_doc_tabs": "false", "group_toolbar_buttons": "false", "toolbar_item_spacing": "2",
            "toolbar_interior_spacing": "4", "spread_progressbar": "true", "progressbar_thickness": "8",
            "composite": "true", "menu_shadow_depth": "6", "tooltip_shadow_depth": "4", "spread_menuitems": "false",
            "menu_separator_height": "10", "splitter_width": "1", "scroll_width": "10", "scroll_min_extent": "40",
            "scroll_arrows": "false", "transient_scrollbar": "true", "transient_groove": "true",
            "combo_as_lineedit": "true", "combo_menu": "true", "combo_focus_rect": "false",
            "inline_spin_indicators": "true", "inline_spin_separator": "false", "vertical_spin_indicators": "false",
            "spin_button_width": "28", "slider_width": "16", "slider_handle_width": "24", "slider_handle_length": "6",
            "tickless_slider_handle_size": "24", "check_size": "18", "button_contents_shift": "false",
            "animate_states": "true", "no_inactiveness": "true", "no_window_pattern": "true",
            "translucent_windows": "false", "reduce_window_opacity": "0", "reduce_menu_opacity": "0",
            "popup_blurring": "false", "menu_blur_radius": "0", "tooltip_blur_radius": "0",
            "small_icon_size": "16", "large_icon_size": "32", "button_icon_size": "20", "toolbar_icon_size": "20",
            "layout_spacing": "8", "layout_margin": "12", "submenu_overlap": "0", "submenu_delay": "250",
            "tooltip_delay": "-1", "click_behavior": "0", "respect_DE": "true", "fill_rubberband": "false",
            "dialog_button_layout": "0", "drag_from_buttons": "false", "scrollbar_in_view": "true",
            "center_toolbar_handle": "true", "slim_toolbars": "false", "toolbutton_style": "0",
            "menubar_mouse_tracking": "true", "merge_menubar_with_toolbar": "false", "hide_combo_checkboxes": "true",
            "joined_inactive_tabs": "false",
        },
        "GeneralColors": {
            "window.color": p["surface"], "base.color": p["surface_container_low"],
            "alt.base.color": p["surface_container"], "button.color": p["secondary_container"],
            "light.color": p["surface_container_highest"], "mid.light.color": p["surface_container_high"],
            "dark.color": p["surface_dim"], "mid.color": p["outline_variant"], "shadow.color": "#00000060",
            "highlight.color": PRI, "inactive.highlight.color": PRI, "text.color": FG, "window.text.color": FG,
            "button.text.color": ON_SEC, "disabled.text.color": FG + "61",
            "tooltip.base.color": p["inverse_surface"], "tooltip.text.color": p["inverse_on_surface"],
            "highlight.text.color": ON_PRI, "link.color": PRI, "link.visited.color": p["tertiary"],
            "progress.indicator.text.color": FG, "progress.inactive.indicator.text.color": FG,
        },
        "Hacks": {
            "respect_darkness": "true", "transparent_ktitle_label": "true", "transparent_dolphin_view": "true",
            "transparent_pcmanfm_sidepane": "true", "transparent_pcmanfm_view": "false", "lxqtmainmenu_iconsize": "16",
            "blur_translucent": "false", "normal_default_pushbutton": "true", "iconless_pushbutton": "false",
            "iconless_menu": "false", "tint_on_mouseover": "0", "no_selection_tint": "true",
            "transparent_arrow_button": "true", "middle_click_scroll": "false", "kcapacitybar_as_progressbar": "true",
            "force_size_grip": "false", "centered_forms": "false", "kinetic_scrolling": "false",
            "noninteger_translucency": "false", "style_vertical_toolbars": "false", "single_top_toolbar": "true",
        },
        "PanelButtonCommand": {**frame(14, "button", "button"), "frame": "true", "interior": "true", "text.default.color": ON_PRI,
                               "indicator.element": "arrow", "indicator.size": "16", **text(ON_SEC, **{"text.toggle.color": ON_PRI}),
                               "text.shadow": "0", "text.margin": "1", "text.iconspacing": "8",
                               "text.margin.top": "3", "text.margin.bottom": "3", "text.margin.left": "6",
                               "text.margin.right": "6", "min_width": "+8", "min_height": "+4"},
        "PanelButtonTool": {"inherits": "PanelButtonCommand", **frame(12, "tbutton", "tbutton"), **text()},
        "ToolbarButton": {**text(), "frame.element": "tbutton", "interior.element": "tbutton"},
        "Dock": {"inherits": "PanelButtonCommand", "frame": "false", "interior": "false", **text()},
        "DockTitle": {"inherits": "PanelButtonCommand", "frame": "false", "interior": "true",
                      "interior.element": "dock", "text.bold": "true", **text()},
        "IndicatorSpinBox": {"inherits": "PanelButtonCommand", **frame(8, "spin", "spin"),
                             "indicator.element": "arrow", "indicator.size": "16", **text()},
        "RadioButton": {"inherits": "PanelButtonCommand", "frame": "false", "interior.element": "radio",
                        "text.margin.left": "4", "text.margin.right": "4", **text()},
        "CheckBox": {"inherits": "PanelButtonCommand", "frame": "false", "interior.element": "checkbox",
                     "text.margin.left": "4", "text.margin.right": "4", **text()},
        "Focus": {"inherits": "PanelButtonCommand", "interior": "false", "frame": "true", **frame(8, "focus")},
        "GenericFrame": {"inherits": "PanelButtonCommand", "frame": "true", "interior": "false",
                         **frame(12, "common", "common"), **text()},
        "LineEdit": {"inherits": "PanelButtonCommand", **frame(6, "lineedit", "lineedit"), **text(),
                     "text.margin.left": "6", "text.margin.right": "6", "min_height": "+8"},
        "ToolbarLineEdit": {"inherits": "LineEdit"},
        "DropDownButton": {"inherits": "PanelButtonCommand", "indicator.element": "arrow-down"},
        "IndicatorArrow": {"indicator.element": "arrow", "indicator.size": "16"},
        "ToolboxTab": {"inherits": "PanelButtonCommand", **frame(12, "tbutton", "tbutton"), **text()},
        "Tab": {"inherits": "PanelButtonCommand", **frame(12, "tab", "tab"), **text(VAR),
                "text.toggle.color": PRI, "text.bold": "false", "indicator.element": "tab", "indicator.size": "16",
                "text.margin.left": "12", "text.margin.right": "12", "text.margin.top": "6",
                "text.margin.bottom": "6", "min_width": "+10", "min_height": "+8"},
        "TabFrame": {"inherits": "PanelButtonCommand", "frame": "true", "interior": "false",
                     **frame(12, "tabframe", "common")},
        "TabBarFrame": {"inherits": "GenericFrame", "frame": "false", "interior": "false"},
        "TreeExpander": {"inherits": "PanelButtonCommand", "frame": "false", "interior": "false",
                         "indicator.element": "arrow", "indicator.size": "16"},
        "HeaderSection": {"inherits": "PanelButtonCommand", **frame(2, "header", "header"),
                          "indicator.element": "arrow", "indicator.size": "12", "text.margin.left": "8",
                          "text.margin.right": "8", **text(VAR), "text.bold": "true"},
        "SizeGrip": {"indicator.element": "sizegrip"},
        "Toolbar": {"inherits": "PanelButtonCommand", "frame": "false", "interior": "false",
                    "indicator.element": "toolbar", "indicator.size": "8", **frame(1, "toolbar", "toolbar"), **text()},
        "Slider": {"inherits": "PanelButtonCommand", **frame(8, "slider", "slider"), "focusFrame": "false"},
        "SliderCursor": {"inherits": "PanelButtonCommand", "frame": "false", "interior": "true",
                         "interior.element": "slidercursor"},
        "Progressbar": {"inherits": "PanelButtonCommand", **frame(4, "progress", "progress"), **text(),
                        "text.bold": "false"},
        "ProgressbarContents": {"inherits": "PanelButtonCommand", "frame": "true", "interior": "true",
                                **frame(4, "progress-pattern", "progress-pattern")},
        "ItemView": {"inherits": "PanelButtonCommand", **frame(8, "itemview", "itemview"),
                     **text(FG, **{"text.toggle.color": ON_SEC}), "text.margin": "0", "text.margin.left": "6",
                     "text.margin.right": "6"},
        "Splitter": {"inherits": "PanelButtonCommand", **frame(0, "splitter", "splitter"),
                     "indicator.element": "splitter-grip", "indicator.size": "16"},
        "Scrollbar": {"inherits": "PanelButtonCommand", "indicator.element": "arrow", "indicator.size": "8"},
        "ScrollbarSlider": {"inherits": "PanelButtonCommand", "interior": "false",
                            **frame(4, "scrollbarslider", "scrollbarslider"), "indicator.element": "grip",
                            "indicator.size": "13"},
        "ScrollbarGroove": {"inherits": "PanelButtonCommand", "frame": "false", "interior": "false",
                            **frame(1, "scrollgroove", "scrollgroove")},
        "MenuItem": {"inherits": "PanelButtonCommand", "frame": "true", **frame(12, "menuitem", "menuitem"),
                     "indicator.element": "menuitem", **text(), "text.margin.top": "4", "text.margin.bottom": "4",
                     "text.margin.left": "8", "text.margin.right": "8", "min_height": "+8"},
        "MenuBarItem": {"inherits": "PanelButtonCommand", "frame": "true",
                        **frame(12, "menubaritem", "menubaritem"), **text(), "text.margin.top": "3",
                        "text.margin.bottom": "3", "text.margin.left": "6", "text.margin.right": "6"},
        "MenuBar": {"inherits": "PanelButtonCommand", "frame": "false", "interior": "false", **text()},
        "TitleBar": {"inherits": "PanelButtonCommand", "frame": "false", "interior": "true",
                     "interior.element": "titlebar", "indicator.element": "mdi", "indicator.size": "16", **text(),
                     "text.bold": "true"},
        "ComboBox": {"inherits": "PanelButtonCommand", "indicator.element": "arrow", **text()},
        "ToolbarComboBox": {"inherits": "ComboBox"},
        "Menu": {"inherits": "PanelButtonCommand", **frame(16, "menu", "menu"), "frame": "true",
                 "interior": "true", **text()},
        "GroupBox": {"inherits": "GenericFrame", "frame": "true", "interior": "true",
                     **frame(12, "group", "group"), "text.margin": "0", "text.bold": "true"},
        "ToolTip": {"inherits": "GenericFrame", **frame(8, "tooltip", "tooltip"), "frame": "true",
                    "interior": "true", **text(p["inverse_on_surface"]), "text.margin": "4"},
        "StatusBar": {"inherits": "GenericFrame", "frame": "false", "interior": "false"},
        "Window": {"interior": "false", "frame": "false"},
    }
    out = ["# Material DMS: generated from DMS's palette. Do not edit."]
    for name, keys in sections.items():
        out.append(f"\n[{name}]")
        out += [f"{k}={v}" for k, v in keys.items() if v != ""]
    return "\n".join(out) + "\n"
