# ── ui_helpers.py ─────────────────────────────────────────────────────────────
import tkinter as tk
from tkinter import ttk

# ── Colour palette ────────────────────────────────────────────────────────────
BG_DARK   = "#0F1923"   # page background
BG_CARD   = "#1A2535"   # card / panel surface
BG_PANEL  = "#162031"   # sidebar / sub-panel
ACCENT    = "#E8A838"   # amber highlight
ACCENT_HO = "#F5C060"   # amber hover
DANGER    = "#E05252"   # red for exit / delete
TEXT_MAIN = "#E8EDF2"   # primary text
TEXT_MUTE = "#7A8FA6"   # muted / label text
BORDER    = "#253347"   # subtle border

ENTRY_W  = 28
LABEL_W  = 20


def apply_global_style(root: tk.Tk):
    """Apply dark theme to ttk widgets."""
    style = ttk.Style(root)
    style.theme_use("clam")

    style.configure(".",
        background=BG_DARK, foreground=TEXT_MAIN,
        font=("Segoe UI", 11), relief="flat",
        bordercolor=BORDER, troughcolor=BG_CARD)

    style.configure("Treeview",
        background=BG_CARD, foreground=TEXT_MAIN,
        fieldbackground=BG_CARD, rowheight=28,
        font=("Segoe UI", 10))
    style.configure("Treeview.Heading",
        background=BG_PANEL, foreground=ACCENT,
        font=("Segoe UI", 10, "bold"), relief="flat")
    style.map("Treeview",
        background=[("selected", ACCENT)],
        foreground=[("selected", BG_DARK)])
    style.map("Treeview.Heading",
        background=[("active", BORDER)])

    style.configure("Vertical.TScrollbar",
        background=BG_PANEL, troughcolor=BG_DARK,
        arrowcolor=TEXT_MUTE)


def make_btn(parent, text, cmd, danger=False, small=False):
    """Styled flat button with hover effect."""
    bg  = DANGER if danger else ACCENT
    hov = "#c03a3a" if danger else ACCENT_HO
    fg  = "#fff"    if danger else BG_DARK
    fs  = 10        if small  else 12
    btn = tk.Button(parent, text=text, command=cmd,
                    bg=bg, fg=fg,
                    activebackground=hov, activeforeground=fg,
                    font=("Segoe UI", fs, "bold"),
                    relief="flat", cursor="hand2",
                    padx=18, pady=8, bd=0)
    btn.bind("<Enter>", lambda e: btn.config(bg=hov))
    btn.bind("<Leave>", lambda e: btn.config(bg=bg))
    return btn


def make_label(parent, text, size=11, muted=False, bold=False):
    """Label styled for the dark theme."""
    fg = TEXT_MUTE if muted else TEXT_MAIN
    wt = "bold"     if bold  else "normal"
    return tk.Label(parent, text=text, bg=BG_CARD,
                    fg=fg, font=("Segoe UI", size, wt))


def make_entry(parent, show=None):
    """Single-line entry styled for the dark theme."""
    return tk.Entry(parent, width=ENTRY_W, show=show or "",
                    bg=BG_PANEL, fg=TEXT_MAIN,
                    insertbackground=ACCENT,
                    relief="flat", bd=0,
                    font=("Segoe UI", 11),
                    highlightthickness=1,
                    highlightbackground=BORDER,
                    highlightcolor=ACCENT)


def make_password_field(parent):
    """Password entry + eye-toggle button.

    Returns (wrapper_frame, entry_widget).
    Place the wrapper_frame in the grid/pack; bind / .get() on entry_widget.
    """
    wrapper = tk.Frame(parent, bg=BG_PANEL,
                       highlightbackground=BORDER,
                       highlightthickness=1)

    entry = tk.Entry(wrapper, width=ENTRY_W - 2, show="*",
                     bg=BG_PANEL, fg=TEXT_MAIN,
                     insertbackground=ACCENT,
                     relief="flat", bd=0,
                     font=("Segoe UI", 11),
                     highlightthickness=0)
    entry.pack(side="left", padx=(6, 0), pady=4)

    visible = tk.BooleanVar(value=False)

    def _toggle():
        if visible.get():
            entry.config(show="*")
            visible.set(False)
            eye_btn.config(text="👁")
        else:
            entry.config(show="")
            visible.set(True)
            eye_btn.config(text="🙈")

    eye_btn = tk.Button(wrapper, text="👁", command=_toggle,
                        bg=BG_PANEL, fg=TEXT_MUTE,
                        activebackground=BG_PANEL,
                        activeforeground=ACCENT,
                        relief="flat", bd=0, cursor="hand2",
                        font=("Segoe UI", 11), padx=4)
    eye_btn.pack(side="left", padx=(2, 4))

    return wrapper, entry


def section_title(parent, text):
    """Amber heading + horizontal rule."""
    f = tk.Frame(parent, bg=BG_CARD)
    tk.Label(f, text=text, bg=BG_CARD, fg=ACCENT,
             font=("Segoe UI", 16, "bold")).pack(side="left")
    tk.Frame(f, bg=BORDER, height=2).pack(
        side="left", fill="x", expand=True, padx=(12, 0), pady=7)
    return f


def make_tree(parent, columns, stretch=True):
    """Treeview with vertical + horizontal scrollbars."""
    frame = tk.Frame(parent, bg=BG_CARD)
    tree  = ttk.Treeview(frame, columns=columns,
                          show="headings", selectmode="browse")
    vsb = ttk.Scrollbar(frame, orient="vertical",
                         command=tree.yview,
                         style="Vertical.TScrollbar")
    hsb = ttk.Scrollbar(frame, orient="horizontal",
                         command=tree.xview)
    tree.configure(yscroll=vsb.set, xscroll=hsb.set)
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, anchor="center",
                    stretch=stretch, minwidth=80, width=130)
    tree.grid(row=0, column=0, sticky="nsew")
    vsb.grid(row=0, column=1, sticky="ns")
    hsb.grid(row=1, column=0, sticky="ew")
    frame.rowconfigure(0, weight=1)
    frame.columnconfigure(0, weight=1)
    return frame, tree


def open_modal(root, title, width=640, height=520):
    """Create a centred modal Toplevel and return (win, body_frame)."""
    win = tk.Toplevel(root)
    win.title(title)
    win.geometry(f"{width}x{height}")
    win.configure(bg=BG_CARD)
    win.grab_set()

    hdr = tk.Frame(win, bg=BG_PANEL, pady=14)
    hdr.pack(fill="x")
    tk.Label(hdr, text=title, bg=BG_PANEL, fg=ACCENT,
             font=("Segoe UI", 14, "bold")).pack(padx=20)

    body = tk.Frame(win, bg=BG_CARD, padx=24, pady=16)
    body.pack(fill="both", expand=True)
    return win, body