# ── main.py ───────────────────────────────────────────────────────────────────
import tkinter as tk
from tkinter import messagebox

from database   import cursor, conn
from ui_helpers import (
    BG_DARK, BG_CARD, BG_PANEL, ACCENT, TEXT_MAIN, TEXT_MUTE, BORDER,
    apply_global_style, make_btn, make_entry, make_label,
    section_title, make_tree, open_modal
)
from student import StudentMixin
from admin   import AdminMixin


class LibraryApp(AdminMixin, StudentMixin):
    """Root application — owns the Tk window and all shared helpers."""

    def __init__(self, root: tk.Tk):
        self.root            = root
        self.current_student = None
        apply_global_style(root)
        self.root.configure(bg=BG_DARK)
        self.init_login_screen()

    # ── shared layout helpers ─────────────────────────────────────────────────
    def _clear(self):
        for w in self.root.winfo_children():
            w.destroy()

    def _header(self, subtitle=""):
        hdr = tk.Frame(self.root, bg=BG_PANEL, pady=18)
        hdr.pack(fill="x")
        tk.Label(hdr, text="📚  LMS", bg=BG_PANEL, fg=ACCENT,
                 font=("Segoe UI", 20, "bold")).pack()
        if subtitle:
            tk.Label(hdr, text=subtitle, bg=BG_PANEL, fg=TEXT_MUTE,
                     font=("Segoe UI", 10)).pack()
        tk.Frame(hdr, bg=BORDER, height=1).pack(fill="x", pady=(10, 0))

    def _center_card(self, width=420):
        outer = tk.Frame(self.root, bg=BG_DARK)
        outer.pack(fill="both", expand=True)
        card  = tk.Frame(outer, bg=BG_CARD, bd=0,
                         highlightbackground=BORDER,
                         highlightthickness=1)
        card.place(relx=0.5, rely=0.5, anchor="center",
                   width=width, relheight=0.85)
        return card

    # ── Welcome screen ────────────────────────────────────────────────────────
    def init_login_screen(self):
        self._clear()
        self.root.title("LMS — Library Management System")
        self.root.geometry("900x620")
        self._header("Library Management System")

        card = self._center_card(380)

        tk.Label(card, text="Welcome", bg=BG_CARD, fg=TEXT_MAIN,
                 font=("Segoe UI", 22, "bold")).pack(pady=(36, 4))
        tk.Label(card, text="Select your login type to continue",
                 bg=BG_CARD, fg=TEXT_MUTE,
                 font=("Segoe UI", 10)).pack(pady=(0, 32))

        make_btn(card, "Admin Login",   self.login_screen).pack(
            fill="x", padx=48, pady=6)
        make_btn(card, "Student Login", self.student_login).pack(
            fill="x", padx=48, pady=6)

    # ── Shared: Search Book ───────────────────────────────────────────────────
    def search_book(self):
        win, body = open_modal(self.root, "Search Book", 900, 560)

        top = tk.Frame(body, bg=BG_CARD)
        top.pack(fill="x", pady=(0, 10))
        tk.Label(top, text="Search by Title / Author / ID",
                 bg=BG_CARD, fg=TEXT_MUTE,
                 font=("Segoe UI", 10)).pack(side="left", padx=(0, 8))
        search_entry = make_entry(top)
        search_entry.pack(side="left", padx=(0, 8))

        cols  = ("ID", "Title", "Author", "Total",
                 "Available", "Publication", "Price")
        frame, tree = make_tree(body, cols)
        frame.pack(fill="both", expand=True, pady=(8, 0))

        def perform_search():
            for row in tree.get_children():
                tree.delete(row)
            q = search_entry.get().strip()
            if not q:
                cursor.execute("SELECT * FROM book")
            elif q.isdigit():
                cursor.execute("SELECT * FROM book WHERE book_id=?", (q,))
            else:
                cursor.execute(
                    "SELECT * FROM book WHERE title LIKE ? OR author LIKE ?",
                    (f"%{q}%", f"%{q}%"))
            for row in cursor.fetchall():
                tree.insert("", "end", values=row)

        make_btn(top, "Search", perform_search, small=True).pack(side="left")
        search_entry.bind("<Return>", lambda e: perform_search())
        perform_search()


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    root.resizable(True, True)
    LibraryApp(root)
    root.mainloop()