# ── student.py ────────────────────────────────────────────────────────────────
import tkinter as tk
from tkinter import messagebox
from datetime import datetime

from database   import cursor, conn
from ui_helpers import (
    BG_DARK, BG_CARD, BG_PANEL, ACCENT, TEXT_MAIN, TEXT_MUTE, BORDER,
    make_btn, make_label, make_entry, make_password_field,
    section_title, make_tree, open_modal
)


class StudentMixin:
    """All student-facing screens.

    Expects the host class to provide:
        self.root               – the root Tk window
        self._clear()           – destroys all children of root
        self._header(subtitle)  – draws the top header bar
        self._center_card(w)    – returns a centred card Frame
        self.init_login_screen()
        self.search_book()      – shared search (defined in main.py)
        self.current_student    – set to student_id after login
    """

    # ── Student Login ─────────────────────────────────────────────────────────
    def student_login(self):
        self._clear()
        self.root.title("LMS — Student Login")
        self._header("Student Portal")

        card = self._center_card(420)
        section_title(card, "Student Login").pack(
            fill="x", padx=24, pady=(28, 16))

        form = tk.Frame(card, bg=BG_CARD)
        form.pack(padx=24)

        make_label(form, "Student ID", muted=True).grid(
            row=0, column=0, sticky="e", padx=(0, 12), pady=12)
        id_entry = make_entry(form)
        id_entry.grid(row=0, column=1, pady=12, sticky="w")

        make_label(form, "Password", muted=True).grid(
            row=1, column=0, sticky="e", padx=(0, 12), pady=12)
        pass_wrap, pass_entry = make_password_field(form)
        pass_wrap.grid(row=1, column=1, pady=12, sticky="w")

        # Enter on Student ID → jump to password
        id_entry.bind("<Return>", lambda e: pass_entry.focus_set())

        def login():
            sid = id_entry.get().strip()
            pwd = pass_entry.get()
            cursor.execute(
                "SELECT * FROM students WHERE student_id=? AND password=?",
                (sid, pwd))
            result = cursor.fetchone()
            if result:
                self.current_student = sid
                self.student_dashboard()
            else:
                messagebox.showerror("Login Failed", "Invalid ID or Password.")

        # Enter on password → submit
        pass_entry.bind("<Return>", lambda e: login())

        btn_row = tk.Frame(card, bg=BG_CARD)
        btn_row.pack(pady=16, padx=24)
        make_btn(btn_row, "Login",    login).pack(side="left", padx=(0, 6))
        make_btn(btn_row, "Register", self.student_register).pack(
            side="left", padx=(0, 6))
        make_btn(btn_row, "Back",     self.init_login_screen).pack(side="left")

    # ── Student Register ──────────────────────────────────────────────────────
    def student_register(self):
        self._clear()
        self.root.title("SafeShelf — Student Registration")
        self._header("Student Registration")

        card = self._center_card(500)
        section_title(card, "Create Account").pack(
            fill="x", padx=24, pady=(20, 10))

        form = tk.Frame(card, bg=BG_CARD)
        form.pack(padx=24, fill="x")

        fields_cfg = [
            ("Student ID", False),
            ("Name",       False),
            ("Email",      False),
            ("Password",   True),
            ("Class",      False),
            ("Year",       False),
            ("Phone",      False),
        ]
        entries = {}
        for i, (lbl, secret) in enumerate(fields_cfg):
            make_label(form, lbl, muted=True).grid(
                row=i, column=0, sticky="e", padx=(0, 10), pady=4)
            if secret:
                wrap, e = make_password_field(form)
                wrap.grid(row=i, column=1, pady=4, sticky="w")
            else:
                e = make_entry(form)
                e.grid(row=i, column=1, pady=4, sticky="w")
            entries[lbl] = e

        def register():
            vals = {k: v.get().strip() for k, v in entries.items()}
            try:
                sid = int(vals["Student ID"])
            except ValueError:
                messagebox.showerror("Error", "Student ID must be a number.")
                return
            if not all(vals.values()):
                messagebox.showwarning("Input Error", "All fields are required.")
                return
            email = vals["Email"]
            if "@" not in email or "." not in email:
                messagebox.showwarning("Input Error", "Invalid email format.")
                return
            phone = vals["Phone"]
            if not phone.isdigit():
                messagebox.showerror("Error",
                                     "Phone number must contain only digits.")
                return
            if len(phone) != 10:
                messagebox.showerror("Error",
                                     "Phone number must be exactly 10 digits.")
                return
            cursor.execute(
                "SELECT * FROM students WHERE student_id=?", (sid,))
            if cursor.fetchone():
                messagebox.showerror("Error", "Student ID already registered.")
                return
            cursor.execute(
                "INSERT INTO students "
                "(student_id, name, email, password, class, year, phone) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)",
                (sid, vals["Name"], email, vals["Password"],
                 vals["Class"], vals["Year"], phone))
            conn.commit()
            messagebox.showinfo("Success", "Account created! Please login.")
            self.student_login()

        btn_row = tk.Frame(card, bg=BG_CARD)
        btn_row.pack(pady=14, padx=24)
        make_btn(btn_row, "Register",      register).pack(
            side="left", padx=(0, 8))
        make_btn(btn_row, "Back to Login", self.student_login).pack(side="left")

    # ── Student Dashboard ─────────────────────────────────────────────────────
    def student_dashboard(self):
        self._clear()
        self.root.title("SafeShelf — Student Dashboard")
        self._header(f"Student Portal  ·  ID {self.current_student}")

        card = self._center_card(400)
        tk.Label(card, text="Student Dashboard",
                 bg=BG_CARD, fg=TEXT_MAIN,
                 font=("Segoe UI", 18, "bold")).pack(pady=(32, 4))
        tk.Label(card,
                 text=f"Logged in as student {self.current_student}",
                 bg=BG_CARD, fg=TEXT_MUTE,
                 font=("Segoe UI", 10)).pack(pady=(0, 24))

        actions = [
            ("View Available Books", self.view_books),
            ("Search Book",          self.search_book),
            ("My Issued Books",      self.my_issued_books),
            ("Back",                 self.init_login_screen),
        ]
        for label, cmd in actions:
            make_btn(card, label, cmd).pack(fill="x", padx=48, pady=5)

        def confirm_exit():
            if messagebox.askyesno("Exit", "Are you sure you want to exit?"):
                self.root.quit()

        make_btn(card, "Exit", confirm_exit, danger=True).pack(
            fill="x", padx=48, pady=(10, 24))

    # ── My Issued Books ───────────────────────────────────────────────────────
    def my_issued_books(self):
        win, body = open_modal(
            self.root, "My Issued Books", 980, 560)

        # ── Fine rule banner ──────────────────────────────────────────────────
        info = tk.Frame(body, bg=BG_PANEL,
                        highlightbackground=BORDER, highlightthickness=1)
        info.pack(fill="x", pady=(0, 12))
        tk.Label(info,
                 text="📌  Fine Policy:  ₹5 charged per day after the due date.",
                 bg=BG_PANEL, fg=ACCENT,
                 font=("Segoe UI", 11, "bold")).pack(
                     side="left", padx=14, pady=10)
        tk.Label(info,
                 text="Pending fine is estimated from today's date for unreturned books.",
                 bg=BG_PANEL, fg=TEXT_MUTE,
                 font=("Segoe UI", 10)).pack(side="left", padx=(0, 14))

        # ── Table ─────────────────────────────────────────────────────────────
        cols = ("Book ID", "Title", "Issue Date",
                "Due Date", "Status", "Fine / Pending Fine (₹)")
        frame, tree = make_tree(body, cols)
        tree.column("Book ID",              width=80,  minwidth=60)
        tree.column("Title",                width=200, minwidth=120)
        tree.column("Issue Date",           width=120, minwidth=100)
        tree.column("Due Date",             width=120, minwidth=100)
        tree.column("Status",               width=100, minwidth=80)
        tree.column("Fine / Pending Fine (₹)", width=180, minwidth=140)
        frame.pack(fill="both", expand=True)

        today = datetime.now().date()

        cursor.execute("""
            SELECT issued.book_id, book.title,
                   issued.issue_date, issued.due_date,
                   issued.return_date, issued.fine
            FROM issued
            JOIN book ON book.book_id = issued.book_id
            WHERE issued.student_id=?
        """, (self.current_student,))

        for row in cursor.fetchall():
            book_id, title, issue_date, due_date, return_date, fine = row

            if return_date:
                status       = "✅ Returned"
                fine_display = f"₹{fine}" if fine else "₹0 (on time)"
            else:
                status = "📖 Issued"
                try:
                    due_dt      = datetime.strptime(due_date, "%Y-%m-%d").date()
                    days_late   = (today - due_dt).days
                    pending     = max(0, days_late * 5)
                    if days_late > 0:
                        fine_display = f"₹{pending}  ({days_late}d overdue)"
                    else:
                        days_left    = (due_dt - today).days
                        fine_display = f"₹0  ({days_left}d remaining)"
                except ValueError:
                    fine_display = "—"

            tree.insert("", "end",
                        values=(book_id, title, issue_date,
                                due_date, status, fine_display))

    # ── View All Books (read-only, shared with admin) ─────────────────────────
    def view_books(self):
        win, body = open_modal(self.root, "All Books", 860, 520)
        cols = ("ID", "Title", "Author", "Total",
                "Available", "Publication", "Price")
        frame, tree = make_tree(body, cols)
        frame.pack(fill="both", expand=True)
        cursor.execute("SELECT * FROM book")
        for row in cursor.fetchall():
            tree.insert("", "end", values=row)