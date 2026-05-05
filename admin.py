# ── admin.py ──────────────────────────────────────────────────────────────────
import tkinter as tk
from tkinter import messagebox
from datetime import datetime

from database   import cursor, conn
from ui_helpers import (
    BG_DARK, BG_CARD, BG_PANEL, ACCENT, ACCENT_HO, DANGER,
    TEXT_MAIN, TEXT_MUTE, BORDER,
    make_btn, make_label, make_entry, make_password_field,
    section_title, make_tree, open_modal
)

NAV_ICONS = {
    "Dashboard":    "⊞",
    "Books":        "📖",
    "Students":     "🎓",
    "Issued Books": "📋",
    "Search":       "🔍",
}


class AdminMixin:
    """All admin-facing screens."""

    # ── Admin Login ───────────────────────────────────────────────────────────
    def login_screen(self):
        self._clear()
        self.root.title("LMS — Admin Login")
        self._header("Admin Portal")

        card = self._center_card(400)
        section_title(card, "Admin Login").pack(
            fill="x", padx=24, pady=(28, 16))

        form = tk.Frame(card, bg=BG_CARD)
        form.pack(padx=36, fill="x")
        form.grid_columnconfigure(1, weight=1)

        make_label(form, "Username", muted=True).grid(
            row=0, column=0, sticky="e", padx=(0, 12), pady=10)
        self.username_entry = make_entry(form)
        self.username_entry.grid(row=0, column=1, pady=10, sticky="ew", ipady=4)
        self.username_entry.bind(
            "<Return>", lambda e: self.password_entry.focus_set())

        make_label(form, "Password", muted=True).grid(
            row=1, column=0, sticky="e", padx=(0, 12), pady=10)
        pass_wrap, self.password_entry = make_password_field(form)
        pass_wrap.grid(row=1, column=1, pady=10, sticky="ew")
        self.password_entry.bind("<Return>", lambda e: self.admin_login())

        btn_row = tk.Frame(card, bg=BG_CARD)
        btn_row.pack(pady=20, padx=24)
        make_btn(btn_row, "Login", self.admin_login).pack(
            side="left", padx=(0, 8))
        make_btn(btn_row, "Back", self.init_login_screen).pack(side="left")

    def admin_login(self):
        user = self.username_entry.get().strip()
        pwd  = self.password_entry.get()
        cursor.execute(
            "SELECT * FROM admin WHERE username=? AND password=?",
            (user, pwd))
        if cursor.fetchone():
            self.main_menu()
        else:
            messagebox.showerror("Login Failed", "Incorrect credentials.")

    # ── Main Layout ───────────────────────────────────────────────────────────
    def main_menu(self):
        self._clear()
        self.root.title("LMS — Admin Panel")
        self.root.geometry("1300x820")
        self._header("Admin Panel")

        outer = tk.Frame(self.root, bg=BG_DARK)
        outer.pack(fill="both", expand=True)

        # ── Left Sidebar ──────────────────────────────────────────────────────
        self._sidebar = tk.Frame(outer, bg=BG_CARD, width=240,
                                 highlightbackground=BORDER,
                                 highlightthickness=1)
        self._sidebar.pack(side="left", fill="y")
        self._sidebar.pack_propagate(False)

        tk.Label(self._sidebar, text="📚 LMS", bg=BG_CARD, fg=ACCENT,
                 font=("Segoe UI", 17, "bold")).pack(pady=(26, 4))
        tk.Label(self._sidebar, text="Admin Panel", bg=BG_CARD, fg=TEXT_MUTE,
                 font=("Segoe UI", 10)).pack()
        tk.Frame(self._sidebar, bg=BORDER, height=1).pack(
            fill="x", padx=20, pady=16)

        self._nav_buttons = {}
        for name in ["Dashboard", "Books", "Students", "Issued Books", "Search"]:
            icon = NAV_ICONS.get(name, "•")
            b = tk.Button(self._sidebar,
                          text=f"  {icon}  {name}",
                          command=lambda n=name: self._load_section(n),
                          bg=BG_CARD, fg=TEXT_MAIN,
                          activebackground=BG_PANEL, activeforeground=ACCENT,
                          font=("Segoe UI", 11),
                          relief="flat", cursor="hand2",
                          anchor="w", padx=14, pady=13, bd=0)
            b.pack(fill="x")
            b.bind("<Enter>",
                   lambda e, btn=b: btn.config(bg=BG_PANEL, fg=ACCENT)
                   if btn.cget("bg") != ACCENT else None)
            b.bind("<Leave>",
                   lambda e, btn=b: btn.config(bg=BG_CARD, fg=TEXT_MAIN)
                   if btn.cget("bg") != ACCENT else None)
            self._nav_buttons[name] = b

        tk.Frame(self._sidebar, bg=BORDER, height=1).pack(
            fill="x", padx=20, pady=12)

        def confirm_exit():
            if messagebox.askyesno("Exit", "Are you sure you want to exit?"):
                self.root.quit()

        make_btn(self._sidebar, "← Back", self.init_login_screen,
                 small=True).pack(fill="x", padx=16, pady=4)
        make_btn(self._sidebar, "Exit", confirm_exit,
                 danger=True, small=True).pack(fill="x", padx=16, pady=(4, 24))

        # ── Right Content Area ────────────────────────────────────────────────
        self._content = tk.Frame(outer, bg=BG_CARD,
                                 highlightbackground=BORDER,
                                 highlightthickness=1)
        self._content.pack(side="left", fill="both", expand=True, padx=1)

        self._load_section("Dashboard")

    # ── Navigation helpers ────────────────────────────────────────────────────
    def _set_active_nav(self, name):
        for n, btn in self._nav_buttons.items():
            if n == name:
                btn.config(bg=ACCENT, fg=BG_DARK)
                btn.unbind("<Enter>")
                btn.unbind("<Leave>")
            else:
                btn.config(bg=BG_CARD, fg=TEXT_MAIN)
                btn.bind("<Enter>",
                         lambda e, b=btn: b.config(bg=BG_PANEL, fg=ACCENT))
                btn.bind("<Leave>",
                         lambda e, b=btn: b.config(bg=BG_CARD, fg=TEXT_MAIN))

    def _clear_content(self):
        for w in self._content.winfo_children():
            w.destroy()

    def _load_section(self, name):
        self._set_active_nav(name)
        self._clear_content()
        {
            "Dashboard":    self._section_dashboard,
            "Books":        self._section_books,
            "Students":     self._section_students,
            "Issued Books": self._section_issued,
            "Search":       self._section_search,
        }[name]()

    def _section_header(self, title):
        """Renders a section title + divider inside content area."""
        tk.Label(self._content, text=title,
                 bg=BG_CARD, fg=TEXT_MAIN,
                 font=("Segoe UI", 22, "bold")).pack(
                     anchor="w", padx=36, pady=(32, 0))
        tk.Frame(self._content, bg=BORDER, height=1).pack(
            fill="x", padx=36, pady=(12, 0))

    # ── Section: Dashboard ────────────────────────────────────────────────────
    def _section_dashboard(self):
        self._section_header("Dashboard")
        tk.Label(self._content, text="Overview of the library system.",
                 bg=BG_CARD, fg=TEXT_MUTE,
                 font=("Segoe UI", 10)).pack(anchor="w", padx=28, pady=(4, 0))
        self._load_stats(self._content)

    def _load_stats(self, parent):
        self._stat_labels = {}
        stat_defs = [
            ("total_books",  "Total Books",      "#3EBD8A"),
            ("available",    "Available Copies", "#E8A838"),
            ("students",     "Students",         "#5B9BD5"),
            ("issued",       "Books Issued",     "#E05252"),
        ]
        grid = tk.Frame(parent, bg=BG_CARD)
        grid.pack(pady=36, padx=36, anchor="w")
        for i, (key, label, color) in enumerate(stat_defs):
            tile = tk.Frame(grid, bg=BG_PANEL, width=200, height=120,
                            highlightbackground=BORDER, highlightthickness=1)
            tile.grid(row=0, column=i, padx=10)
            tile.pack_propagate(False)
            num = tk.Label(tile, text="—", bg=BG_PANEL, fg=color,
                           font=("Segoe UI", 34, "bold"))
            num.pack(pady=(20, 2))
            tk.Label(tile, text=label, bg=BG_PANEL, fg=TEXT_MUTE,
                     font=("Segoe UI", 10)).pack()
            self._stat_labels[key] = num
        self._refresh_stats()

    def _refresh_stats(self):
        if not hasattr(self, "_stat_labels"):
            return
        cursor.execute("SELECT COUNT(*) FROM book")
        total_books = cursor.fetchone()[0]
        cursor.execute("SELECT SUM(available_copies) FROM book")
        avail = cursor.fetchone()[0] or 0
        cursor.execute("SELECT COUNT(*) FROM students")
        total_stu = cursor.fetchone()[0]
        cursor.execute(
            "SELECT COUNT(*) FROM issued WHERE return_date IS NULL")
        issued_ct = cursor.fetchone()[0]
        self._stat_labels["total_books"].config(text=str(total_books))
        self._stat_labels["available"].config(text=str(avail))
        self._stat_labels["students"].config(text=str(total_stu))
        self._stat_labels["issued"].config(text=str(issued_ct))

    # ── Section: Books ────────────────────────────────────────────────────────
    def _section_books(self):
        self._section_header("Books")

        # Contextual toolbar
        bar = tk.Frame(self._content, bg=BG_CARD)
        bar.pack(fill="x", padx=36, pady=14)
        make_btn(bar, "+ Add Book",
                 lambda: self._modal_add_book(self._refresh_books_table),
                 small=True).pack(side="left", padx=(0, 8))
        make_btn(bar, "＋ Add Copies",
                 lambda: self._modal_add_copies(self._refresh_books_table),
                 small=True).pack(side="left", padx=(0, 8))
        make_btn(bar, "－ Remove Copies",
                 lambda: self._modal_remove_copies(self._refresh_books_table),
                 small=True).pack(side="left")

        # Table
        cols = ("ID", "Title", "Author", "Total",
                "Available", "Publication", "Price")
        tbl_frame, self._books_tree = make_tree(self._content, cols)
        tbl_frame.pack(fill="both", expand=True, padx=36, pady=(4, 20))
        self._refresh_books_table()

    def _refresh_books_table(self):
        if not hasattr(self, "_books_tree"):
            return
        for row in self._books_tree.get_children():
            self._books_tree.delete(row)
        cursor.execute("SELECT * FROM book")
        for row in cursor.fetchall():
            self._books_tree.insert("", "end", values=row)
        self._refresh_stats()

    # ── Section: Students ─────────────────────────────────────────────────────
    def _section_students(self):
        self._section_header("Students")

        cols = ("ID", "Name", "Email", "Class", "Year", "Phone")
        tbl_frame, tree = make_tree(self._content, cols)
        tbl_frame.pack(fill="both", expand=True, padx=36, pady=(16, 20))
        cursor.execute(
            "SELECT student_id, name, email, class, year, phone FROM students")
        for row in cursor.fetchall():
            tree.insert("", "end", values=row)

    # ── Section: Issued Books ─────────────────────────────────────────────────
    def _section_issued(self):
        self._section_header("Issued Books")

        # Contextual toolbar
        bar = tk.Frame(self._content, bg=BG_CARD)
        bar.pack(fill="x", padx=36, pady=14)
        make_btn(bar, "📤 Issue Book",
                 lambda: self._modal_issue(self._refresh_issued_table),
                 small=True).pack(side="left", padx=(0, 8))
        make_btn(bar, "📥 Return Book",
                 lambda: self._modal_return(self._refresh_issued_table),
                 small=True).pack(side="left")

        # Table
        cols = ("Issue ID", "Student Name", "Student ID",
                "Book ID", "Issue Date", "Due Date", "Return Date", "Fine (₹)")
        tbl_frame, self._issued_tree = make_tree(self._content, cols)
        tbl_frame.pack(fill="both", expand=True, padx=36, pady=(4, 20))
        self._refresh_issued_table()

    def _refresh_issued_table(self):
        if not hasattr(self, "_issued_tree"):
            return
        for row in self._issued_tree.get_children():
            self._issued_tree.delete(row)
        cursor.execute(
            "SELECT issue_id, student_name, student_id, book_id, "
            "issue_date, due_date, return_date, fine FROM issued")
        for row in cursor.fetchall():
            self._issued_tree.insert("", "end", values=row)
        self._refresh_stats()

    # ── Section: Search ───────────────────────────────────────────────────────
    def _section_search(self):
        self._section_header("Search Books")

        bar = tk.Frame(self._content, bg=BG_CARD)
        bar.pack(fill="x", padx=36, pady=16)

        search_entry = make_entry(bar)
        search_entry.config(width=44)
        search_entry.pack(side="left", padx=(0, 10))

        cols = ("ID", "Title", "Author", "Total",
                "Available", "Publication", "Price")
        tbl_frame, tree = make_tree(self._content, cols)
        tbl_frame.pack(fill="both", expand=True, padx=36, pady=(0, 20))

        def perform():
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

        make_btn(bar, "Search", perform, small=True).pack(side="left")
        search_entry.bind("<Return>", lambda e: perform())
        search_entry.focus_set()
        perform()

    # ── Modal: Add Book ───────────────────────────────────────────────────────
    def _modal_add_book(self, on_done=None):
        win, body = open_modal(self.root, "Add Book", 580, 460)
        form = tk.Frame(body, bg=BG_CARD)
        form.pack(fill="x")

        labels  = ["Title", "Author", "Total Copies", "Publication", "Price"]
        entries = {}
        for i, lbl in enumerate(labels):
            make_label(form, lbl, muted=True).grid(
                row=i, column=0, sticky="e", padx=(0, 10), pady=6)
            e = make_entry(form)
            e.grid(row=i, column=1, pady=6, sticky="w")
            entries[lbl] = e

        def save():
            vals = {k: v.get().strip() for k, v in entries.items()}
            if not all(vals.values()):
                messagebox.showerror("Input Error",
                                     "All fields are required.", parent=win)
                return
            try:
                copies = int(vals["Total Copies"])
                price  = int(vals["Price"])
            except ValueError:
                messagebox.showerror("Input Error",
                                     "Copies and Price must be numbers.",
                                     parent=win)
                return
            cursor.execute(
                "INSERT INTO book (title, author, total_copies, "
                "available_copies, publication, price) VALUES (?,?,?,?,?,?)",
                (vals["Title"], vals["Author"], copies, copies,
                 vals["Publication"], price))
            conn.commit()
            messagebox.showinfo("Success", "Book added.", parent=win)
            win.destroy()
            if on_done:
                on_done()

        make_btn(body, "Add Book", save).pack(pady=(16, 0))

    # ── Modal: Add Copies ─────────────────────────────────────────────────────
    def _modal_add_copies(self, on_done=None):
        win, body = open_modal(self.root, "Add Book Copies", 540, 300)
        form = tk.Frame(body, bg=BG_CARD)
        form.pack(fill="x")

        make_label(form, "Book ID", muted=True).grid(
            row=0, column=0, sticky="e", padx=(0, 10), pady=8)
        book_id_e = make_entry(form)
        book_id_e.grid(row=0, column=1, pady=8)

        make_label(form, "Copies to Add", muted=True).grid(
            row=1, column=0, sticky="e", padx=(0, 10), pady=8)
        copies_e = make_entry(form)
        copies_e.grid(row=1, column=1, pady=8)
        book_id_e.bind("<Return>", lambda e: copies_e.focus_set())

        def save():
            try:
                bid = int(book_id_e.get().strip())
                cnt = int(copies_e.get().strip())
            except ValueError:
                messagebox.showerror("Error", "Enter valid numbers.", parent=win)
                return
            if cnt <= 0:
                messagebox.showerror("Error", "Enter a positive number.",
                                     parent=win)
                return
            cursor.execute(
                "SELECT total_copies, available_copies FROM book WHERE book_id=?",
                (bid,))
            row = cursor.fetchone()
            if not row:
                messagebox.showerror("Error", "Book ID not found.", parent=win)
                return
            cursor.execute(
                "UPDATE book SET total_copies=?, available_copies=? "
                "WHERE book_id=?",
                (row[0] + cnt, row[1] + cnt, bid))
            conn.commit()
            messagebox.showinfo("Success", f"{cnt} copies added.", parent=win)
            win.destroy()
            if on_done:
                on_done()

        copies_e.bind("<Return>", lambda e: save())
        make_btn(body, "Add Copies", save).pack(pady=(20, 0))

    # ── Modal: Remove Copies ──────────────────────────────────────────────────
    def _modal_remove_copies(self, on_done=None):
        win, body = open_modal(self.root, "Remove Book Copies", 540, 300)
        form = tk.Frame(body, bg=BG_CARD)
        form.pack(fill="x")

        make_label(form, "Book ID", muted=True).grid(
            row=0, column=0, sticky="e", padx=(0, 10), pady=8)
        book_id_e = make_entry(form)
        book_id_e.grid(row=0, column=1, pady=8)

        make_label(form, "Copies to Remove", muted=True).grid(
            row=1, column=0, sticky="e", padx=(0, 10), pady=8)
        copies_e = make_entry(form)
        copies_e.grid(row=1, column=1, pady=8)
        book_id_e.bind("<Return>", lambda e: copies_e.focus_set())

        def save():
            try:
                bid = int(book_id_e.get().strip())
                cnt = int(copies_e.get().strip())
            except ValueError:
                messagebox.showerror("Error", "Enter valid numbers.", parent=win)
                return
            if cnt <= 0:
                messagebox.showerror("Error", "Enter a positive number.",
                                     parent=win)
                return
            cursor.execute(
                "SELECT total_copies, available_copies FROM book WHERE book_id=?",
                (bid,))
            row = cursor.fetchone()
            if not row:
                messagebox.showerror("Error", "Book ID not found.", parent=win)
                return
            total, available = row
            if cnt > available:
                messagebox.showwarning(
                    "Warning", "Cannot remove more than available copies.",
                    parent=win)
                return
            if (total - cnt) <= 0:
                messagebox.showerror("Error", "Must keep at least 1 copy.",
                                     parent=win)
                return
            cursor.execute(
                "UPDATE book SET total_copies=?, available_copies=? "
                "WHERE book_id=?",
                (total - cnt, available - cnt, bid))
            conn.commit()
            messagebox.showinfo("Success", f"{cnt} copies removed.", parent=win)
            win.destroy()
            if on_done:
                on_done()

        copies_e.bind("<Return>", lambda e: save())
        make_btn(body, "Remove Copies", save).pack(pady=(20, 0))

    # ── Modal: Issue Book ─────────────────────────────────────────────────────
    def _modal_issue(self, on_done=None):
        win, body = open_modal(self.root, "Issue Book", 600, 500)
        form = tk.Frame(body, bg=BG_CARD)
        form.pack(fill="x")

        fields = [
            "Student Name", "Student ID", "Book ID",
            "Issue Date (YYYY-MM-DD)", "Due Date (YYYY-MM-DD)"
        ]
        entries = {}
        field_widgets = []
        for i, lbl in enumerate(fields):
            make_label(form, lbl, muted=True).grid(
                row=i, column=0, sticky="e", padx=(0, 10), pady=6)
            e = make_entry(form)
            e.grid(row=i, column=1, pady=6, sticky="w")
            entries[lbl] = e
            field_widgets.append(e)

        # Enter moves through fields
        for i, e in enumerate(field_widgets[:-1]):
            next_e = field_widgets[i + 1]
            e.bind("<Return>", lambda ev, n=next_e: n.focus_set())

        def issue():
            try:
                bid = int(entries["Book ID"].get().strip())
            except ValueError:
                messagebox.showerror("Error", "Book ID must be a number.",
                                     parent=win)
                return
            cursor.execute(
                "SELECT available_copies FROM book WHERE book_id=?", (bid,))
            data = cursor.fetchone()
            if not data or data[0] <= 0:
                messagebox.showerror("Error", "Book not available.", parent=win)
                return
            try:
                datetime.strptime(
                    entries["Issue Date (YYYY-MM-DD)"].get(), "%Y-%m-%d")
                datetime.strptime(
                    entries["Due Date (YYYY-MM-DD)"].get(), "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Error",
                                     "Invalid date. Use YYYY-MM-DD.",
                                     parent=win)
                return
            cursor.execute(
                "INSERT INTO issued (student_name, student_id, book_id, "
                "issue_date, due_date) VALUES (?,?,?,?,?)",
                (entries["Student Name"].get().strip(),
                 entries["Student ID"].get().strip(),
                 bid,
                 entries["Issue Date (YYYY-MM-DD)"].get().strip(),
                 entries["Due Date (YYYY-MM-DD)"].get().strip()))
            cursor.execute(
                "UPDATE book SET available_copies = available_copies - 1 "
                "WHERE book_id=?", (bid,))
            conn.commit()
            messagebox.showinfo("Success", "Book issued.", parent=win)
            win.destroy()
            if on_done:
                on_done()

        field_widgets[-1].bind("<Return>", lambda e: issue())
        make_btn(body, "Issue", issue).pack(pady=(16, 0))

    # ── Modal: Return Book ────────────────────────────────────────────────────
    def _modal_return(self, on_done=None):
        win, body = open_modal(self.root, "Return Book", 560, 340)
        form = tk.Frame(body, bg=BG_CARD)
        form.pack(fill="x")

        make_label(form, "Issue ID", muted=True).grid(
            row=0, column=0, sticky="e", padx=(0, 10), pady=8)
        issue_id_e = make_entry(form)
        issue_id_e.grid(row=0, column=1, pady=8, sticky="w")

        make_label(form, "Return Date (YYYY-MM-DD)", muted=True).grid(
            row=1, column=0, sticky="e", padx=(0, 10), pady=8)
        return_date_e = make_entry(form)
        return_date_e.grid(row=1, column=1, pady=8, sticky="w")
        issue_id_e.bind("<Return>", lambda e: return_date_e.focus_set())

        def process():
            try:
                iid = int(issue_id_e.get().strip())
                rdt = datetime.strptime(
                    return_date_e.get().strip(), "%Y-%m-%d")
            except ValueError:
                messagebox.showerror(
                    "Error", "Invalid input. Check ID and date.", parent=win)
                return
            cursor.execute(
                "SELECT book_id, due_date FROM issued "
                "WHERE issue_id=? AND (return_date IS NULL OR return_date='')",
                (iid,))
            data = cursor.fetchone()
            if not data:
                messagebox.showerror(
                    "Error", "Invalid Issue ID or already returned.",
                    parent=win)
                return
            book_id, due_str = data
            due_dt = datetime.strptime(due_str, "%Y-%m-%d")
            fine   = max(0, (rdt - due_dt).days * 5)
            cursor.execute(
                "UPDATE issued SET return_date=?, fine=? WHERE issue_id=?",
                (return_date_e.get().strip(), fine, iid))
            cursor.execute(
                "UPDATE book SET available_copies = available_copies + 1 "
                "WHERE book_id=?", (book_id,))
            conn.commit()
            msg = f"Book returned.\nFine: ₹{fine}"
            if fine == 0:
                msg += "\n✓ On time — no fine!"
            messagebox.showinfo("Returned", msg, parent=win)
            win.destroy()
            if on_done:
                on_done()

        return_date_e.bind("<Return>", lambda e: process())
        make_btn(body, "Return", process).pack(pady=(20, 0))

    # ── Aliases so any leftover direct calls still work ───────────────────────
    def add_book(self):            self._modal_add_book(None)
    def add_book_copies(self):     self._modal_add_copies(None)
    def remove_book_copies(self):  self._modal_remove_copies(None)
    def issue_book(self):          self._modal_issue(None)
    def return_book(self):         self._modal_return(None)