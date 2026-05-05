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

ENTRY_W  = 32
LABEL_W  = 22


def apply_global_style(root: tk.Tk):
    """Apply dark theme to ttk widgets."""
    style = ttk.Style(root)
    style.theme_use("clam")

    style.configure(".",
        background=BG_DARK, foreground=TEXT_MAIN,
        font=("Segoe UI", 12), relief="flat",
        bordercolor=BORDER, troughcolor=BG_CARD)

    style.configure("Treeview",
        background=BG_CARD, foreground=TEXT_MAIN,
        fieldbackground=BG_CARD, rowheight=38,
        font=("Segoe UI", 11))
    style.configure("Treeview.Heading",
        background=BG_PANEL, foreground=ACCENT,
        font=("Segoe UI", 11, "bold"), relief="flat")
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
    fs  = 11        if small  else 13
    btn = tk.Button(parent, text=text, command=cmd,
                    bg=bg, fg=fg,
                    activebackground=hov, activeforeground=fg,
                    font=("Segoe UI", fs, "bold"),
                    relief="flat", cursor="hand2",
                    padx=22, pady=10, bd=0)
    btn.bind("<Enter>", lambda e: btn.config(bg=hov))
    btn.bind("<Leave>", lambda e: btn.config(bg=bg))
    return btn


def make_label(parent, text, size=12, muted=False, bold=False):
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
                    font=("Segoe UI", 12),
                    highlightthickness=1,
                    highlightbackground=BORDER,
                    highlightcolor=ACCENT)


def make_password_field(parent):
    """Password entry with Show/Hide button placed inside on the right edge."""
    wrap = tk.Frame(parent, bg=BG_CARD)

    field = tk.Frame(wrap, bg=BG_PANEL,
                     highlightbackground=BORDER,
                     highlightthickness=1)
    field.pack(fill="x")

    entry = tk.Entry(field, show="*",
                     bg=BG_PANEL, fg=TEXT_MAIN,
                     relief="flat", bd=0,
                     font=("Segoe UI", 12),
                     insertbackground=ACCENT)
    entry.pack(fill="x", ipady=8, padx=(10, 52))

    def toggle():
        if entry.cget("show") == "":
            entry.config(show="*")
            eye_btn.config(text="👁")
        else:
            entry.config(show="")
            eye_btn.config(text="🔒")

    eye_btn = tk.Button(field, text="👁", command=toggle,
                        bg=BG_PANEL, fg=TEXT_MUTE,
                        activebackground=BG_PANEL,
                        activeforeground=ACCENT,
                        relief="flat", bd=0, cursor="hand2",
                        font=("Segoe UI Emoji", 11))

    eye_btn.place(relx=1.0, rely=0.5, anchor="e", x=-10)

    return wrap, entry


def section_title(parent, text):
    """Amber heading + horizontal rule."""
    f = tk.Frame(parent, bg=BG_CARD)
    tk.Label(f, text=text, bg=BG_CARD, fg=ACCENT,
             font=("Segoe UI", 18, "bold")).pack(side="left")
    tk.Frame(f, bg=BORDER, height=2).pack(
        side="left", fill="x", expand=True, padx=(14, 0), pady=8)
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
                    stretch=stretch, minwidth=100, width=150)
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

    hdr = tk.Frame(win, bg=BG_PANEL, pady=18)
    hdr.pack(fill="x")
    tk.Label(hdr, text=title, bg=BG_PANEL, fg=ACCENT,
             font=("Segoe UI", 15, "bold")).pack(padx=24)

    body = tk.Frame(win, bg=BG_CARD, padx=32, pady=22)
    body.pack(fill="both", expand=True)
    return win, body