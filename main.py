"""
main.py - Personal Expense Manager Desktop Application
Built with Python Tkinter and SQLite for College Practical / Viva Submission.
Features:
- Main Dashboard with KPI cards & recent transactions
- Menu Bar with full shortcuts
- Separate screens for Add Expense, Add Income, View Records, Categories, Search/Filter, Reports, CSV Import/Export
- Relational SQLite database with 3 tables (categories, expenses, income)
- Full CRUD operations with input validation and confirmation dialogs
- Interactive reports with category breakdown and dynamic chart
- CSV Export and Import
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, date
import os
import sys

# Import database module
import database

# Optional Matplotlib integration for visual reports
MATPLOTLIB_AVAILABLE = False
try:
    import matplotlib
    matplotlib.use("TkAgg")
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    MATPLOTLIB_AVAILABLE = True
except Exception:
    MATPLOTLIB_AVAILABLE = False


class ExpenseManagerApp(tk.Tk):
    """Main Application Window for Personal Expense Manager."""

    # Color Palette - Professional Slate & Indigo Theme
    COLOR_PRIMARY = "#1e293b"       # Dark Slate (Sidebar & Headers)
    COLOR_PRIMARY_HOVER = "#334155" # Lighter Slate
    COLOR_ACCENT = "#4f46e5"        # Indigo
    COLOR_ACCENT_HOVER = "#4338ca"
    COLOR_BG = "#f8fafc"            # Soft White / Slate 50
    COLOR_CARD = "#ffffff"          # Pure White
    COLOR_BORDER = "#e2e8f0"        # Light Gray Border
    COLOR_TEXT = "#0f172a"          # Dark Text
    COLOR_TEXT_MUTED = "#64748b"    # Slate Gray Text
    COLOR_SUCCESS = "#10b981"       # Emerald Green (Income)
    COLOR_DANGER = "#ef4444"        # Crimson Red (Expense)
    COLOR_INFO = "#0284c7"          # Sky Blue (Balance)
    COLOR_WARNING = "#f59e0b"       # Amber

    PAYMENT_METHODS = ["Cash", "UPI / Online", "Debit Card", "Credit Card", "Bank Transfer", "Other"]

    def __init__(self):
        super().__init__()

        # Window Configuration
        self.title("Personal Expense Manager - College Practical Project")
        self.geometry("1100x720")
        self.minsize(980, 640)
        self.configure(bg=self.COLOR_BG)

        # Center Window on Screen
        self.center_window(1100, 720)

        # Initialize SQLite Database
        database.init_db()

        # Active Screen State
        self.current_screen = None
        self.sidebar_buttons = {}

        # Configure TTK Styles
        self.setup_styles()

        # Build UI Structure
        self.create_menu_bar()
        self.create_layout()

        # Show Default Screen
        self.show_screen("dashboard")
        self.update_status("Application ready. Database connected successfully.")

    def center_window(self, width, height):
        """Centers the Tkinter window on the primary screen."""
        self.update_idletasks()
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        x = max(0, int((screen_w - width) / 2))
        y = max(0, int((screen_h - height) / 2))
        self.geometry(f"{width}x{height}+{x}+{y}")

    def setup_styles(self):
        """Configures modern styling for TTK widgets."""
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except Exception:
            pass

        # General TTK Styles
        style.configure("TLabel", background=self.COLOR_BG, foreground=self.COLOR_TEXT, font=("Segoe UI", 10))
        style.configure("Card.TFrame", background=self.COLOR_CARD, relief="flat")
        
        # Treeview Styling
        style.configure(
            "Treeview.Heading",
            font=("Segoe UI", 10, "bold"),
            background="#0f172a",
            foreground="#ffffff",
            relief="flat",
            padding=6
        )
        style.map("Treeview.Heading", background=[("active", "#1e293b")])
        style.configure(
            "Treeview",
            font=("Segoe UI", 9),
            rowheight=26,
            background="#ffffff",
            fieldbackground="#ffffff",
            foreground=self.COLOR_TEXT,
            borderwidth=1
        )
        style.map("Treeview", background=[("selected", "#e0e7ff")], foreground=[("selected", "#1e1b4b")])

        # Modern Button Styles
        style.configure(
            "Primary.TButton",
            font=("Segoe UI", 10, "bold"),
            background=self.COLOR_ACCENT,
            foreground="#ffffff",
            borderwidth=0,
            padding=6
        )
        style.map("Primary.TButton", background=[("active", self.COLOR_ACCENT_HOVER)])

        style.configure(
            "Success.TButton",
            font=("Segoe UI", 10, "bold"),
            background=self.COLOR_SUCCESS,
            foreground="#ffffff",
            borderwidth=0,
            padding=6
        )
        style.map("Success.TButton", background=[("active", "#059669")])

        style.configure(
            "Danger.TButton",
            font=("Segoe UI", 10, "bold"),
            background=self.COLOR_DANGER,
            foreground="#ffffff",
            borderwidth=0,
            padding=6
        )
        style.map("Danger.TButton", background=[("active", "#dc2626")])

    def create_menu_bar(self):
        """Creates the native application menu bar."""
        menubar = tk.Menu(self)

        # File Menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Export to CSV...", command=lambda: self.show_screen("import_export"))
        file_menu.add_command(label="Import from CSV...", command=lambda: self.show_screen("import_export"))
        file_menu.add_separator()
        file_menu.add_command(label="Exit", accelerator="Alt+F4", command=self.quit)
        menubar.add_cascade(label="File", menu=file_menu)

        # Navigation Menu
        nav_menu = tk.Menu(menubar, tearoff=0)
        nav_menu.add_command(label="Dashboard", command=lambda: self.show_screen("dashboard"))
        nav_menu.add_command(label="Add Expense", command=lambda: self.show_screen("add_expense"))
        nav_menu.add_command(label="Add Income", command=lambda: self.show_screen("add_income"))
        nav_menu.add_command(label="View Records", command=lambda: self.show_screen("records"))
        nav_menu.add_command(label="Manage Categories", command=lambda: self.show_screen("categories"))
        nav_menu.add_command(label="Search & Filter", command=lambda: self.show_screen("search"))
        nav_menu.add_command(label="Reports & Analytics", command=lambda: self.show_screen("reports"))
        menubar.add_cascade(label="Screens", menu=nav_menu)

        # Tools Menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        tools_menu.add_command(label="Refresh Active Screen", accelerator="F5", command=self.refresh_current_screen)
        tools_menu.add_command(label="Seed / Reset Sample Data", command=self.confirm_reset_sample_data)
        menubar.add_cascade(label="Data", menu=tools_menu)

        # Help Menu
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="Database Schema Info", command=self.show_schema_dialog)
        help_menu.add_command(label="About Project", command=self.show_about_dialog)
        menubar.add_cascade(label="Help", menu=help_menu)

        self.config(menu=menubar)
        self.bind("<F5>", lambda event: self.refresh_current_screen())

    def create_layout(self):
        """Constructs the sidebar, top header, main content body, and bottom status bar."""
        # Top Header Bar
        self.header_frame = tk.Frame(self, bg=self.COLOR_PRIMARY, height=54)
        self.header_frame.pack(side=tk.TOP, fill=tk.X)
        self.header_frame.pack_propagate(False)

        title_lbl = tk.Label(
            self.header_frame,
            text="💰 Personal Expense Manager",
            bg=self.COLOR_PRIMARY,
            fg="#ffffff",
            font=("Segoe UI", 14, "bold")
        )
        title_lbl.pack(side=tk.LEFT, padx=16, pady=10)

        badge_lbl = tk.Label(
            self.header_frame,
            text="Python Tkinter + SQLite Practical",
            bg="#334155",
            fg="#cbd5e1",
            font=("Segoe UI", 8, "bold"),
            padx=8,
            pady=3
        )
        badge_lbl.pack(side=tk.LEFT, padx=8)

        self.date_lbl = tk.Label(
            self.header_frame,
            text=f"📅 {date.today().strftime('%A, %d %B %Y')}",
            bg=self.COLOR_PRIMARY,
            fg="#94a3b8",
            font=("Segoe UI", 9)
        )
        self.date_lbl.pack(side=tk.RIGHT, padx=16)

        # Bottom Status Bar
        self.status_bar = tk.Frame(self, bg="#0f172a", height=24)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        self.status_bar.pack_propagate(False)

        self.status_lbl = tk.Label(
            self.status_bar,
            text="Ready",
            bg="#0f172a",
            fg="#94a3b8",
            font=("Segoe UI", 8),
            anchor=tk.W
        )
        self.status_lbl.pack(side=tk.LEFT, padx=12)

        self.db_status_lbl = tk.Label(
            self.status_bar,
            text=f"DB: {os.path.basename(database.DB_FILE)} (Connected)",
            bg="#0f172a",
            fg="#38bdf8",
            font=("Segoe UI", 8),
            anchor=tk.E
        )
        self.db_status_lbl.pack(side=tk.RIGHT, padx=12)

        # Center Container (Sidebar + Content View)
        self.center_container = tk.Frame(self, bg=self.COLOR_BG)
        self.center_container.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Left Sidebar Navigation
        self.sidebar_frame = tk.Frame(self.center_container, bg=self.COLOR_PRIMARY, width=200)
        self.sidebar_frame.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar_frame.pack_propagate(False)

        nav_title = tk.Label(
            self.sidebar_frame,
            text="NAVIGATION",
            bg=self.COLOR_PRIMARY,
            fg="#64748b",
            font=("Segoe UI", 8, "bold"),
            anchor=tk.W
        )
        nav_title.pack(fill=tk.X, padx=16, pady=(16, 8))

        # Sidebar Navigation Buttons Configuration
        nav_items = [
            ("dashboard", "📊 Dashboard"),
            ("add_expense", "💸 Add Expense"),
            ("add_income", "💵 Add Income"),
            ("records", "📋 View Records"),
            ("categories", "🏷️ Categories"),
            ("search", "🔍 Search & Filter"),
            ("reports", "📈 Reports & Stats"),
            ("import_export", "💾 Import / Export"),
        ]

        for screen_key, label_text in nav_items:
            btn = tk.Button(
                self.sidebar_frame,
                text=f"  {label_text}",
                anchor="w",
                font=("Segoe UI", 10),
                bg=self.COLOR_PRIMARY,
                fg="#cbd5e1",
                activebackground=self.COLOR_PRIMARY_HOVER,
                activeforeground="#ffffff",
                relief="flat",
                bd=0,
                padx=12,
                pady=9,
                cursor="hand2",
                command=lambda k=screen_key: self.show_screen(k)
            )
            btn.pack(fill=tk.X, padx=8, pady=2)
            self.sidebar_buttons[screen_key] = btn

        # Main Content Frame where screens are rendered
        self.content_frame = tk.Frame(self.center_container, bg=self.COLOR_BG)
        self.content_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=16, pady=16)

    def update_status(self, message):
        """Updates the status bar label."""
        self.status_lbl.config(text=message)

    def show_screen(self, screen_name):
        """Switches the active view in the content area."""
        self.current_screen = screen_name

        # Update sidebar active highlights
        for key, btn in self.sidebar_buttons.items():
            if key == screen_name:
                btn.config(bg=self.COLOR_ACCENT, fg="#ffffff", font=("Segoe UI", 10, "bold"))
            else:
                btn.config(bg=self.COLOR_PRIMARY, fg="#cbd5e1", font=("Segoe UI", 10))

        # Clear existing screen widgets
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        # Build requested screen
        if screen_name == "dashboard":
            self.build_dashboard_screen()
        elif screen_name == "add_expense":
            self.build_add_expense_screen()
        elif screen_name == "add_income":
            self.build_add_income_screen()
        elif screen_name == "records":
            self.build_records_screen()
        elif screen_name == "categories":
            self.build_categories_screen()
        elif screen_name == "search":
            self.build_search_screen()
        elif screen_name == "reports":
            self.build_reports_screen()
        elif screen_name == "import_export":
            self.build_import_export_screen()

        self.update_status(f"View changed to: {screen_name.replace('_', ' ').title()}")

    def refresh_current_screen(self):
        """Refreshes the currently displayed screen."""
        if self.current_screen:
            self.show_screen(self.current_screen)

    # =========================================================================
    # SCREEN 1: DASHBOARD
    # =========================================================================

    def build_dashboard_screen(self):
        """Constructs the dashboard overview with KPI cards, quick actions, and recent activity."""
        summary = database.get_financial_summary()

        # Dashboard Header
        top_bar = tk.Frame(self.content_frame, bg=self.COLOR_BG)
        top_bar.pack(fill=tk.X, pady=(0, 14))

        dash_title = tk.Label(
            top_bar,
            text="Financial Dashboard",
            font=("Segoe UI", 16, "bold"),
            bg=self.COLOR_BG,
            fg=self.COLOR_TEXT
        )
        dash_title.pack(side=tk.LEFT)

        btn_box = tk.Frame(top_bar, bg=self.COLOR_BG)
        btn_box.pack(side=tk.RIGHT)

        ttk.Button(
            btn_box,
            text="+ Add Expense",
            style="Danger.TButton",
            command=lambda: self.show_screen("add_expense")
        ).pack(side=tk.LEFT, padx=4)

        ttk.Button(
            btn_box,
            text="+ Add Income",
            style="Success.TButton",
            command=lambda: self.show_screen("add_income")
        ).pack(side=tk.LEFT, padx=4)

        # 3 KPI Cards Frame (Income, Expense, Net Balance)
        kpi_frame = tk.Frame(self.content_frame, bg=self.COLOR_BG)
        kpi_frame.pack(fill=tk.X, pady=(0, 16))
        kpi_frame.columnconfigure(0, weight=1)
        kpi_frame.columnconfigure(1, weight=1)
        kpi_frame.columnconfigure(2, weight=1)

        # Card 1: Total Income
        self.create_kpi_card(
            parent=kpi_frame,
            col=0,
            title="TOTAL INCOME",
            amount=f"₹ {summary['total_income']:,.2f}",
            subtitle=f"{summary['income_count']} credited entries",
            banner_color=self.COLOR_SUCCESS,
            icon="💵"
        )

        # Card 2: Total Expenses
        self.create_kpi_card(
            parent=kpi_frame,
            col=1,
            title="TOTAL EXPENSES",
            amount=f"₹ {summary['total_expenses']:,.2f}",
            subtitle=f"{summary['expense_count']} spent entries",
            banner_color=self.COLOR_DANGER,
            icon="💸"
        )

        # Card 3: Net Balance
        balance_val = summary['balance']
        bal_color = self.COLOR_SUCCESS if balance_val >= 0 else self.COLOR_DANGER
        self.create_kpi_card(
            parent=kpi_frame,
            col=2,
            title="NET BALANCE",
            amount=f"₹ {balance_val:,.2f}",
            subtitle="Available balance" if balance_val >= 0 else "Deficit / Overspent",
            banner_color=bal_color,
            icon="⚖️"
        )

        # Two-Column Body: Recent Transactions (Left) & Category Breakdown (Right)
        body_frame = tk.Frame(self.content_frame, bg=self.COLOR_BG)
        body_frame.pack(fill=tk.BOTH, expand=True)
        body_frame.columnconfigure(0, weight=3)
        body_frame.columnconfigure(1, weight=2)

        # Left Card: Recent Transactions Table
        recent_card = tk.Frame(body_frame, bg=self.COLOR_CARD, highlightthickness=1, highlightbackground=self.COLOR_BORDER)
        recent_card.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        recent_header = tk.Frame(recent_card, bg=self.COLOR_CARD)
        recent_header.pack(fill=tk.X, padx=12, pady=10)
        tk.Label(
            recent_header,
            text="Recent Transactions",
            font=("Segoe UI", 11, "bold"),
            bg=self.COLOR_CARD,
            fg=self.COLOR_TEXT
        ).pack(side=tk.LEFT)

        tk.Button(
            recent_header,
            text="View All →",
            font=("Segoe UI", 9, "bold"),
            bg=self.COLOR_CARD,
            fg=self.COLOR_ACCENT,
            bd=0,
            cursor="hand2",
            command=lambda: self.show_screen("records")
        ).pack(side=tk.RIGHT)

        # Recent Treeview
        columns = ("type", "date", "category", "amount")
        recent_tree = ttk.Treeview(recent_card, columns=columns, show="headings", height=8)
        recent_tree.heading("type", text="Type")
        recent_tree.heading("date", text="Date")
        recent_tree.heading("category", text="Category")
        recent_tree.heading("amount", text="Amount")

        recent_tree.column("type", width=70, anchor="center")
        recent_tree.column("date", width=85, anchor="center")
        recent_tree.column("category", width=140, anchor="w")
        recent_tree.column("amount", width=95, anchor="e")

        recent_tree.tag_configure("Expense", foreground="#dc2626")
        recent_tree.tag_configure("Income", foreground="#16a34a")

        # Populate top 8 recent transactions
        recent_records = database.get_combined_transactions(record_type="All")[:8]
        for r in recent_records:
            amt_display = f"+₹{r['amount']:,.2f}" if r["trans_type"] == "Income" else f"-₹{r['amount']:,.2f}"
            recent_tree.insert(
                "",
                tk.END,
                values=(r["trans_type"], r["date"], r["category_name"], amt_display),
                tags=(r["trans_type"],)
            )

        recent_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        # Right Card: Expense Category Breakdown Summary
        cat_card = tk.Frame(body_frame, bg=self.COLOR_CARD, highlightthickness=1, highlightbackground=self.COLOR_BORDER)
        cat_card.grid(row=0, column=1, sticky="nsew", padx=(8, 0))

        cat_header = tk.Frame(cat_card, bg=self.COLOR_CARD)
        cat_header.pack(fill=tk.X, padx=12, pady=10)
        tk.Label(
            cat_header,
            text="Top Expense Categories",
            font=("Segoe UI", 11, "bold"),
            bg=self.COLOR_CARD,
            fg=self.COLOR_TEXT
        ).pack(side=tk.LEFT)

        cat_breakdown = database.get_expense_category_breakdown()
        total_exp = summary["total_expenses"] or 1.0  # Avoid division by zero

        cat_content = tk.Frame(cat_card, bg=self.COLOR_CARD)
        cat_content.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 12))

        if not cat_breakdown:
            tk.Label(
                cat_content,
                text="No expense records yet.",
                bg=self.COLOR_CARD,
                fg=self.COLOR_TEXT_MUTED,
                font=("Segoe UI", 10)
            ).pack(pady=40)
        else:
            for cat in cat_breakdown[:5]:
                cat_name = cat["category_name"]
                cat_amt = cat["total_amount"]
                pct = (cat_amt / total_exp) * 100

                row_f = tk.Frame(cat_content, bg=self.COLOR_CARD)
                row_f.pack(fill=tk.X, pady=4)

                tk.Label(
                    row_f,
                    text=cat_name,
                    font=("Segoe UI", 9, "bold"),
                    bg=self.COLOR_CARD,
                    fg=self.COLOR_TEXT
                ).pack(side=tk.LEFT)

                tk.Label(
                    row_f,
                    text=f"₹{cat_amt:,.2f} ({pct:.1f}%)",
                    font=("Segoe UI", 9),
                    bg=self.COLOR_CARD,
                    fg=self.COLOR_TEXT_MUTED
                ).pack(side=tk.RIGHT)

                # Progress bar representation
                bar_bg = tk.Frame(cat_content, bg="#e2e8f0", height=6)
                bar_bg.pack(fill=tk.X, pady=(2, 6))
                bar_bg.pack_propagate(False)

                fill_w = max(4, int(pct * 2.5))
                bar_fill = tk.Frame(bar_bg, bg=self.COLOR_ACCENT, width=fill_w)
                bar_fill.pack(side=tk.LEFT, fill=tk.Y)

    def create_kpi_card(self, parent, col, title, amount, subtitle, banner_color, icon):
        """Reusable KPI summary card."""
        card = tk.Frame(parent, bg=self.COLOR_CARD, highlightthickness=1, highlightbackground=self.COLOR_BORDER)
        card.grid(row=0, column=col, sticky="nsew", padx=6)

        # Top Accent Strip
        strip = tk.Frame(card, bg=banner_color, height=4)
        strip.pack(side=tk.TOP, fill=tk.X)

        inner = tk.Frame(card, bg=self.COLOR_CARD, padx=16, pady=12)
        inner.pack(fill=tk.BOTH, expand=True)

        header_row = tk.Frame(inner, bg=self.COLOR_CARD)
        header_row.pack(fill=tk.X)

        tk.Label(
            header_row,
            text=title,
            font=("Segoe UI", 8, "bold"),
            fg=self.COLOR_TEXT_MUTED,
            bg=self.COLOR_CARD
        ).pack(side=tk.LEFT)

        tk.Label(
            header_row,
            text=icon,
            font=("Segoe UI", 12),
            bg=self.COLOR_CARD
        ).pack(side=tk.RIGHT)

        tk.Label(
            inner,
            text=amount,
            font=("Segoe UI", 17, "bold"),
            fg=self.COLOR_TEXT,
            bg=self.COLOR_CARD
        ).pack(anchor=tk.W, pady=(4, 2))

        tk.Label(
            inner,
            text=subtitle,
            font=("Segoe UI", 8),
            fg=self.COLOR_TEXT_MUTED,
            bg=self.COLOR_CARD
        ).pack(anchor=tk.W)

    # =========================================================================
    # SCREEN 2: ADD EXPENSE
    # =========================================================================

    def build_add_expense_screen(self):
        """Screen for adding a new expense record with comprehensive validation."""
        container = tk.Frame(self.content_frame, bg=self.COLOR_BG)
        container.pack(fill=tk.BOTH, expand=True)

        # Header
        tk.Label(
            container,
            text="Log New Expense",
            font=("Segoe UI", 16, "bold"),
            bg=self.COLOR_BG,
            fg=self.COLOR_TEXT
        ).pack(anchor=tk.W, pady=(0, 4))

        tk.Label(
            container,
            text="Enter details of your expense transaction. Stored in SQLite database.",
            font=("Segoe UI", 9),
            bg=self.COLOR_BG,
            fg=self.COLOR_TEXT_MUTED
        ).pack(anchor=tk.W, pady=(0, 16))

        # Form Card
        form_card = tk.Frame(container, bg=self.COLOR_CARD, padx=24, pady=20, highlightthickness=1, highlightbackground=self.COLOR_BORDER)
        form_card.pack(fill=tk.X)

        # Amount
        tk.Label(form_card, text="Amount (₹) *", font=("Segoe UI", 10, "bold"), bg=self.COLOR_CARD).grid(row=0, column=0, sticky="w", pady=8)
        self.exp_amt_var = tk.StringVar()
        exp_amt_ent = ttk.Entry(form_card, textvariable=self.exp_amt_var, font=("Segoe UI", 11), width=32)
        exp_amt_ent.grid(row=0, column=1, sticky="w", padx=12, pady=8)
        exp_amt_ent.focus_set()

        # Category
        tk.Label(form_card, text="Category *", font=("Segoe UI", 10, "bold"), bg=self.COLOR_CARD).grid(row=1, column=0, sticky="w", pady=8)
        self.exp_cat_var = tk.StringVar()
        self.exp_cat_combo = ttk.Combobox(form_card, textvariable=self.exp_cat_var, state="readonly", font=("Segoe UI", 10), width=30)
        self.exp_cat_combo.grid(row=1, column=1, sticky="w", padx=12, pady=8)

        # Quick Add Category Shortcut Button
        tk.Button(
            form_card,
            text="+ New Category",
            font=("Segoe UI", 8),
            bg="#f1f5f9",
            fg=self.COLOR_ACCENT,
            bd=1,
            cursor="hand2",
            command=lambda: self.quick_add_category_dialog("Expense")
        ).grid(row=1, column=2, sticky="w", padx=4)

        # Date
        tk.Label(form_card, text="Date (YYYY-MM-DD) *", font=("Segoe UI", 10, "bold"), bg=self.COLOR_CARD).grid(row=2, column=0, sticky="w", pady=8)
        date_box = tk.Frame(form_card, bg=self.COLOR_CARD)
        date_box.grid(row=2, column=1, sticky="w", padx=12, pady=8)

        self.exp_date_var = tk.StringVar(value=date.today().strftime("%Y-%m-%d"))
        ttk.Entry(date_box, textvariable=self.exp_date_var, font=("Segoe UI", 10), width=18).pack(side=tk.LEFT)

        tk.Button(
            date_box,
            text="Today",
            font=("Segoe UI", 8),
            bg="#f1f5f9",
            bd=1,
            command=lambda: self.exp_date_var.set(date.today().strftime("%Y-%m-%d"))
        ).pack(side=tk.LEFT, padx=6)

        # Payment Method
        tk.Label(form_card, text="Payment Method *", font=("Segoe UI", 10, "bold"), bg=self.COLOR_CARD).grid(row=3, column=0, sticky="w", pady=8)
        self.exp_pm_var = tk.StringVar(value=self.PAYMENT_METHODS[0])
        pm_combo = ttk.Combobox(form_card, textvariable=self.exp_pm_var, values=self.PAYMENT_METHODS, state="readonly", font=("Segoe UI", 10), width=30)
        pm_combo.grid(row=3, column=1, sticky="w", padx=12, pady=8)

        # Description
        tk.Label(form_card, text="Description / Note", font=("Segoe UI", 10, "bold"), bg=self.COLOR_CARD).grid(row=4, column=0, sticky="w", pady=8)
        self.exp_desc_var = tk.StringVar()
        ttk.Entry(form_card, textvariable=self.exp_desc_var, font=("Segoe UI", 10), width=45).grid(row=4, column=1, columnspan=2, sticky="w", padx=12, pady=8)

        # Button Row
        btn_row = tk.Frame(form_card, bg=self.COLOR_CARD)
        btn_row.grid(row=5, column=1, sticky="w", padx=12, pady=(16, 8))

        ttk.Button(btn_row, text="💾 Save Expense", style="Danger.TButton", command=self.save_expense_action).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(btn_row, text="🔄 Clear Form", command=self.clear_expense_form).pack(side=tk.LEFT)

        self.refresh_expense_categories_dropdown()

    def refresh_expense_categories_dropdown(self):
        """Loads expense categories into the combobox."""
        cats = database.get_categories("Expense")
        names = [c["name"] for c in cats]
        self.exp_cat_combo["values"] = names
        if names:
            self.exp_cat_combo.current(0)

    def clear_expense_form(self):
        """Resets the Add Expense form fields."""
        self.exp_amt_var.set("")
        self.exp_date_var.set(date.today().strftime("%Y-%m-%d"))
        self.exp_pm_var.set(self.PAYMENT_METHODS[0])
        self.exp_desc_var.set("")
        self.refresh_expense_categories_dropdown()

    def save_expense_action(self):
        """Validates and saves the new expense record."""
        amt_str = self.exp_amt_var.get().strip()
        cat_name = self.exp_cat_var.get().strip()
        date_str = self.exp_date_var.get().strip()
        pm = self.exp_pm_var.get().strip()
        desc = self.exp_desc_var.get().strip()

        # Validation
        if not amt_str:
            messagebox.showerror("Validation Error", "Please enter an amount.")
            return

        try:
            amount = float(amt_str)
            if amount <= 0:
                raise ValueError()
        except ValueError:
            messagebox.showerror("Validation Error", "Amount must be a valid positive number.")
            return

        if not cat_name:
            messagebox.showerror("Validation Error", "Please select or create a category.")
            return

        try:
            database.validate_date_format(date_str)
        except ValueError as e:
            messagebox.showerror("Validation Error", str(e))
            return

        # Fetch category ID
        cats = database.get_categories("Expense")
        cat_id = next((c["id"] for c in cats if c["name"] == cat_name), None)

        if not cat_id:
            messagebox.showerror("Error", f"Category '{cat_name}' not found.")
            return

        try:
            database.add_expense(cat_id, amount, date_str, pm, desc)
            messagebox.showinfo("Success", f"Expense of ₹{amount:,.2f} recorded successfully!")
            self.clear_expense_form()
            self.update_status(f"Saved expense: ₹{amount:.2f} under {cat_name}")
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to save expense: {str(e)}")

    # =========================================================================
    # SCREEN 3: ADD INCOME
    # =========================================================================

    def build_add_income_screen(self):
        """Screen for recording income transactions."""
        container = tk.Frame(self.content_frame, bg=self.COLOR_BG)
        container.pack(fill=tk.BOTH, expand=True)

        tk.Label(
            container,
            text="Record New Income",
            font=("Segoe UI", 16, "bold"),
            bg=self.COLOR_BG,
            fg=self.COLOR_TEXT
        ).pack(anchor=tk.W, pady=(0, 4))

        tk.Label(
            container,
            text="Log money received (Salary, Pocket Money, Freelance, Scholarship).",
            font=("Segoe UI", 9),
            bg=self.COLOR_BG,
            fg=self.COLOR_TEXT_MUTED
        ).pack(anchor=tk.W, pady=(0, 16))

        # Form Card
        form_card = tk.Frame(container, bg=self.COLOR_CARD, padx=24, pady=20, highlightthickness=1, highlightbackground=self.COLOR_BORDER)
        form_card.pack(fill=tk.X)

        # Amount
        tk.Label(form_card, text="Amount (₹) *", font=("Segoe UI", 10, "bold"), bg=self.COLOR_CARD).grid(row=0, column=0, sticky="w", pady=8)
        self.inc_amt_var = tk.StringVar()
        inc_amt_ent = ttk.Entry(form_card, textvariable=self.inc_amt_var, font=("Segoe UI", 11), width=32)
        inc_amt_ent.grid(row=0, column=1, sticky="w", padx=12, pady=8)
        inc_amt_ent.focus_set()

        # Category
        tk.Label(form_card, text="Income Source / Category *", font=("Segoe UI", 10, "bold"), bg=self.COLOR_CARD).grid(row=1, column=0, sticky="w", pady=8)
        self.inc_cat_var = tk.StringVar()
        self.inc_cat_combo = ttk.Combobox(form_card, textvariable=self.inc_cat_var, state="readonly", font=("Segoe UI", 10), width=30)
        self.inc_cat_combo.grid(row=1, column=1, sticky="w", padx=12, pady=8)

        tk.Button(
            form_card,
            text="+ New Source",
            font=("Segoe UI", 8),
            bg="#f1f5f9",
            fg=self.COLOR_ACCENT,
            bd=1,
            cursor="hand2",
            command=lambda: self.quick_add_category_dialog("Income")
        ).grid(row=1, column=2, sticky="w", padx=4)

        # Date
        tk.Label(form_card, text="Date (YYYY-MM-DD) *", font=("Segoe UI", 10, "bold"), bg=self.COLOR_CARD).grid(row=2, column=0, sticky="w", pady=8)
        date_box = tk.Frame(form_card, bg=self.COLOR_CARD)
        date_box.grid(row=2, column=1, sticky="w", padx=12, pady=8)

        self.inc_date_var = tk.StringVar(value=date.today().strftime("%Y-%m-%d"))
        ttk.Entry(date_box, textvariable=self.inc_date_var, font=("Segoe UI", 10), width=18).pack(side=tk.LEFT)

        tk.Button(
            date_box,
            text="Today",
            font=("Segoe UI", 8),
            bg="#f1f5f9",
            bd=1,
            command=lambda: self.inc_date_var.set(date.today().strftime("%Y-%m-%d"))
        ).pack(side=tk.LEFT, padx=6)

        # Payment Method
        tk.Label(form_card, text="Payment Method *", font=("Segoe UI", 10, "bold"), bg=self.COLOR_CARD).grid(row=3, column=0, sticky="w", pady=8)
        self.inc_pm_var = tk.StringVar(value="Bank Transfer")
        pm_combo = ttk.Combobox(form_card, textvariable=self.inc_pm_var, values=self.PAYMENT_METHODS, state="readonly", font=("Segoe UI", 10), width=30)
        pm_combo.grid(row=3, column=1, sticky="w", padx=12, pady=8)

        # Description
        tk.Label(form_card, text="Description / Note", font=("Segoe UI", 10, "bold"), bg=self.COLOR_CARD).grid(row=4, column=0, sticky="w", pady=8)
        self.inc_desc_var = tk.StringVar()
        ttk.Entry(form_card, textvariable=self.inc_desc_var, font=("Segoe UI", 10), width=45).grid(row=4, column=1, columnspan=2, sticky="w", padx=12, pady=8)

        # Buttons
        btn_row = tk.Frame(form_card, bg=self.COLOR_CARD)
        btn_row.grid(row=5, column=1, sticky="w", padx=12, pady=(16, 8))

        ttk.Button(btn_row, text="💾 Save Income", style="Success.TButton", command=self.save_income_action).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(btn_row, text="🔄 Clear Form", command=self.clear_income_form).pack(side=tk.LEFT)

        self.refresh_income_categories_dropdown()

    def refresh_income_categories_dropdown(self):
        """Loads income categories into the combobox."""
        cats = database.get_categories("Income")
        names = [c["name"] for c in cats]
        self.inc_cat_combo["values"] = names
        if names:
            self.inc_cat_combo.current(0)

    def clear_income_form(self):
        """Resets the Add Income form fields."""
        self.inc_amt_var.set("")
        self.inc_date_var.set(date.today().strftime("%Y-%m-%d"))
        self.inc_pm_var.set("Bank Transfer")
        self.inc_desc_var.set("")
        self.refresh_income_categories_dropdown()

    def save_income_action(self):
        """Validates and saves the new income record."""
        amt_str = self.inc_amt_var.get().strip()
        cat_name = self.inc_cat_var.get().strip()
        date_str = self.inc_date_var.get().strip()
        pm = self.inc_pm_var.get().strip()
        desc = self.inc_desc_var.get().strip()

        if not amt_str:
            messagebox.showerror("Validation Error", "Please enter an income amount.")
            return

        try:
            amount = float(amt_str)
            if amount <= 0:
                raise ValueError()
        except ValueError:
            messagebox.showerror("Validation Error", "Amount must be a valid positive number.")
            return

        if not cat_name:
            messagebox.showerror("Validation Error", "Please select or create an income category.")
            return

        try:
            database.validate_date_format(date_str)
        except ValueError as e:
            messagebox.showerror("Validation Error", str(e))
            return

        cats = database.get_categories("Income")
        cat_id = next((c["id"] for c in cats if c["name"] == cat_name), None)

        if not cat_id:
            messagebox.showerror("Error", f"Category '{cat_name}' not found.")
            return

        try:
            database.add_income(cat_id, amount, date_str, pm, desc)
            messagebox.showinfo("Success", f"Income of ₹{amount:,.2f} recorded successfully!")
            self.clear_income_form()
            self.update_status(f"Saved income: ₹{amount:.2f} under {cat_name}")
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to save income: {str(e)}")

    def quick_add_category_dialog(self, default_type):
        """Modal dialog to quickly add a new category without leaving the form."""
        dlg = tk.Toplevel(self)
        dlg.title(f"Add New {default_type} Category")
        dlg.geometry("380x220")
        dlg.resizable(False, False)
        dlg.transient(self)
        dlg.grab_set()

        # Center dialog
        self.center_dialog(dlg, 380, 220)

        tk.Label(dlg, text=f"Create New {default_type} Category", font=("Segoe UI", 11, "bold")).pack(pady=(16, 12))

        f = tk.Frame(dlg, padx=20)
        f.pack(fill=tk.BOTH, expand=True)

        tk.Label(f, text="Category Name:", font=("Segoe UI", 9, "bold")).grid(row=0, column=0, sticky="w", pady=6)
        name_ent = ttk.Entry(f, width=24, font=("Segoe UI", 10))
        name_ent.grid(row=0, column=1, sticky="w", pady=6)
        name_ent.focus_set()

        def do_add():
            name = name_ent.get().strip()
            try:
                database.add_category(name, default_type)
                messagebox.showinfo("Success", f"Category '{name}' created successfully!", parent=dlg)
                dlg.destroy()
                if default_type == "Expense" and hasattr(self, "exp_cat_combo"):
                    self.refresh_expense_categories_dropdown()
                    self.exp_cat_var.set(name)
                elif default_type == "Income" and hasattr(self, "inc_cat_combo"):
                    self.refresh_income_categories_dropdown()
                    self.inc_cat_var.set(name)
            except Exception as ex:
                messagebox.showerror("Error", str(ex), parent=dlg)

        btn_box = tk.Frame(dlg, pady=12)
        btn_box.pack()
        ttk.Button(btn_box, text="Save", style="Primary.TButton", command=do_add).pack(side=tk.LEFT, padx=6)
        ttk.Button(btn_box, text="Cancel", command=dlg.destroy).pack(side=tk.LEFT)

    # =========================================================================
    # SCREEN 4: VIEW RECORDS (TREEVIEW WITH COMPLETE CRUD)
    # =========================================================================

    def build_records_screen(self):
        """Displays all transaction records with filtering, editing, and deletion."""
        container = tk.Frame(self.content_frame, bg=self.COLOR_BG)
        container.pack(fill=tk.BOTH, expand=True)

        # Top Bar
        top_bar = tk.Frame(container, bg=self.COLOR_BG)
        top_bar.pack(fill=tk.X, pady=(0, 10))

        tk.Label(
            top_bar,
            text="Transaction Records (CRUD)",
            font=("Segoe UI", 16, "bold"),
            bg=self.COLOR_BG,
            fg=self.COLOR_TEXT
        ).pack(side=tk.LEFT)

        # Filter Tabs (All / Expenses / Income)
        self.records_filter_var = tk.StringVar(value="All")
        filter_box = tk.Frame(top_bar, bg=self.COLOR_BG)
        filter_box.pack(side=tk.RIGHT)

        for label_text in ["All", "Expense", "Income"]:
            rb = tk.Radiobutton(
                filter_box,
                text=label_text,
                value=label_text,
                variable=self.records_filter_var,
                bg=self.COLOR_BG,
                font=("Segoe UI", 9, "bold"),
                command=self.load_records_table
            )
            rb.pack(side=tk.LEFT, padx=6)

        # Quick Search Bar above table
        search_bar = tk.Frame(container, bg=self.COLOR_CARD, padx=12, pady=8, highlightthickness=1, highlightbackground=self.COLOR_BORDER)
        search_bar.pack(fill=tk.X, pady=(0, 10))

        tk.Label(search_bar, text="Quick Search:", font=("Segoe UI", 9, "bold"), bg=self.COLOR_CARD).pack(side=tk.LEFT, padx=(0, 6))
        self.rec_search_var = tk.StringVar()
        rec_search_ent = ttk.Entry(search_bar, textvariable=self.rec_search_var, width=28)
        rec_search_ent.pack(side=tk.LEFT, padx=(0, 8))
        rec_search_ent.bind("<KeyRelease>", lambda event: self.load_records_table())

        ttk.Button(search_bar, text="Clear", command=lambda: [self.rec_search_var.set(""), self.load_records_table()]).pack(side=tk.LEFT)

        self.records_count_lbl = tk.Label(search_bar, text="Showing 0 records", font=("Segoe UI", 9), bg=self.COLOR_CARD, fg=self.COLOR_TEXT_MUTED)
        self.records_count_lbl.pack(side=tk.RIGHT)

        # Treeview Frame with Scrollbars
        table_frame = tk.Frame(container, bg=self.COLOR_CARD, highlightthickness=1, highlightbackground=self.COLOR_BORDER)
        table_frame.pack(fill=tk.BOTH, expand=True)

        cols = ("id", "type", "date", "category", "amount", "payment_method", "description")
        self.records_tree = ttk.Treeview(table_frame, columns=cols, show="headings", selectmode="browse")

        self.records_tree.heading("id", text="ID", command=lambda: self.sort_tree_column(self.records_tree, "id", False))
        self.records_tree.heading("type", text="Type", command=lambda: self.sort_tree_column(self.records_tree, "type", False))
        self.records_tree.heading("date", text="Date", command=lambda: self.sort_tree_column(self.records_tree, "date", False))
        self.records_tree.heading("category", text="Category", command=lambda: self.sort_tree_column(self.records_tree, "category", False))
        self.records_tree.heading("amount", text="Amount (₹)", command=lambda: self.sort_tree_column(self.records_tree, "amount", False))
        self.records_tree.heading("payment_method", text="Payment Method", command=lambda: self.sort_tree_column(self.records_tree, "payment_method", False))
        self.records_tree.heading("description", text="Description")

        self.records_tree.column("id", width=45, anchor="center")
        self.records_tree.column("type", width=75, anchor="center")
        self.records_tree.column("date", width=90, anchor="center")
        self.records_tree.column("category", width=160, anchor="w")
        self.records_tree.column("amount", width=110, anchor="e")
        self.records_tree.column("payment_method", width=120, anchor="w")
        self.records_tree.column("description", width=260, anchor="w")

        self.records_tree.tag_configure("Expense", foreground="#dc2626")
        self.records_tree.tag_configure("Income", foreground="#16a34a")

        v_scroll = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.records_tree.yview)
        h_scroll = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=self.records_tree.xview)
        self.records_tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)

        self.records_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        h_scroll.pack(side=tk.BOTTOM, fill=tk.X)

        self.records_tree.bind("<Double-1>", lambda event: self.edit_selected_record())

        # Action Buttons Row
        action_row = tk.Frame(container, bg=self.COLOR_BG, pady=10)
        action_row.pack(fill=tk.X)

        ttk.Button(action_row, text="✏️ Edit Selected", style="Primary.TButton", command=self.edit_selected_record).pack(side=tk.LEFT, padx=(0, 6))
        ttk.Button(action_row, text="🗑️ Delete Selected", style="Danger.TButton", command=self.delete_selected_record).pack(side=tk.LEFT, padx=6)
        ttk.Button(action_row, text="🔄 Refresh Table", command=self.load_records_table).pack(side=tk.LEFT, padx=6)
        ttk.Button(action_row, text="📤 Export View to CSV", command=lambda: self.export_current_view_to_csv()).pack(side=tk.RIGHT)

        self.load_records_table()

    def load_records_table(self):
        """Fetches and renders filtered records into the treeview."""
        for item in self.records_tree.get_children():
            self.records_tree.delete(item)

        filter_type = self.records_filter_var.get()
        kw = self.rec_search_var.get().strip()

        records = database.get_combined_transactions(record_type=filter_type, keyword=kw)
        for r in records:
            amt_display = f"₹ {r['amount']:,.2f}"
            self.records_tree.insert(
                "",
                tk.END,
                values=(r["id"], r["trans_type"], r["date"], r["category_name"], amt_display, r["payment_method"], r["description"] or ""),
                tags=(r["trans_type"],)
            )

        self.records_count_lbl.config(text=f"Showing {len(records)} records")

    def edit_selected_record(self):
        """Opens modal editor for updating the chosen expense or income transaction."""
        selected = self.records_tree.selection()
        if not selected:
            messagebox.showwarning("Select Record", "Please select a transaction to edit.")
            return

        values = self.records_tree.item(selected[0], "values")
        rec_id = int(values[0])
        rec_type = values[1]

        # Fetch full record from SQLite
        if rec_type == "Expense":
            rec = database.get_expense_by_id(rec_id)
        else:
            rec = database.get_income_by_id(rec_id)

        if not rec:
            messagebox.showerror("Error", "Record could not be found.")
            return

        # Modal Dialog
        dlg = tk.Toplevel(self)
        dlg.title(f"Edit {rec_type} Record #{rec_id}")
        dlg.geometry("440x360")
        dlg.resizable(False, False)
        dlg.transient(self)
        dlg.grab_set()
        self.center_dialog(dlg, 440, 360)

        tk.Label(dlg, text=f"Update {rec_type} Transaction", font=("Segoe UI", 12, "bold")).pack(pady=(16, 12))

        form = tk.Frame(dlg, padx=20)
        form.pack(fill=tk.BOTH, expand=True)

        # Amount
        tk.Label(form, text="Amount (₹) *", font=("Segoe UI", 9, "bold")).grid(row=0, column=0, sticky="w", pady=6)
        amt_var = tk.StringVar(value=str(rec["amount"]))
        ttk.Entry(form, textvariable=amt_var, width=28, font=("Segoe UI", 10)).grid(row=0, column=1, sticky="w", pady=6)

        # Category
        tk.Label(form, text="Category *", font=("Segoe UI", 9, "bold")).grid(row=1, column=0, sticky="w", pady=6)
        cat_var = tk.StringVar(value=rec["category_name"])
        cats = database.get_categories(rec_type)
        cat_names = [c["name"] for c in cats]
        cat_combo = ttk.Combobox(form, textvariable=cat_var, values=cat_names, state="readonly", width=26, font=("Segoe UI", 10))
        cat_combo.grid(row=1, column=1, sticky="w", pady=6)

        # Date
        tk.Label(form, text="Date (YYYY-MM-DD) *", font=("Segoe UI", 9, "bold")).grid(row=2, column=0, sticky="w", pady=6)
        date_var = tk.StringVar(value=rec["date"])
        ttk.Entry(form, textvariable=date_var, width=28, font=("Segoe UI", 10)).grid(row=2, column=1, sticky="w", pady=6)

        # Payment Method
        tk.Label(form, text="Payment Method *", font=("Segoe UI", 9, "bold")).grid(row=3, column=0, sticky="w", pady=6)
        pm_var = tk.StringVar(value=rec["payment_method"])
        ttk.Combobox(form, textvariable=pm_var, values=self.PAYMENT_METHODS, state="readonly", width=26, font=("Segoe UI", 10)).grid(row=3, column=1, sticky="w", pady=6)

        # Description
        tk.Label(form, text="Description", font=("Segoe UI", 9, "bold")).grid(row=4, column=0, sticky="w", pady=6)
        desc_var = tk.StringVar(value=rec["description"] or "")
        ttk.Entry(form, textvariable=desc_var, width=28, font=("Segoe UI", 10)).grid(row=4, column=1, sticky="w", pady=6)

        def do_update():
            try:
                amt = float(amt_var.get().strip())
                if amt <= 0:
                    raise ValueError("Amount must be greater than 0.")
            except ValueError:
                messagebox.showerror("Validation Error", "Please enter a valid positive number for amount.", parent=dlg)
                return

            cat_sel = cat_var.get().strip()
            cat_match = next((c["id"] for c in cats if c["name"] == cat_sel), None)
            if not cat_match:
                messagebox.showerror("Validation Error", "Invalid category selected.", parent=dlg)
                return

            d_str = date_var.get().strip()
            try:
                database.validate_date_format(d_str)
            except ValueError as ex:
                messagebox.showerror("Validation Error", str(ex), parent=dlg)
                return

            pm = pm_var.get().strip()
            ds = desc_var.get().strip()

            try:
                if rec_type == "Expense":
                    database.update_expense(rec_id, cat_match, amt, d_str, pm, ds)
                else:
                    database.update_income(rec_id, cat_match, amt, d_str, pm, ds)

                messagebox.showinfo("Success", f"{rec_type} #{rec_id} updated successfully!", parent=dlg)
                dlg.destroy()
                self.load_records_table()
                self.update_status(f"Updated {rec_type} #{rec_id}")
            except Exception as e:
                messagebox.showerror("Database Error", str(e), parent=dlg)

        btn_box = tk.Frame(dlg, pady=12)
        btn_box.pack()
        ttk.Button(btn_box, text="💾 Save Changes", style="Primary.TButton", command=do_update).pack(side=tk.LEFT, padx=6)
        ttk.Button(btn_box, text="Cancel", command=dlg.destroy).pack(side=tk.LEFT)

    def delete_selected_record(self):
        """Deletes selected transaction after explicit user confirmation."""
        selected = self.records_tree.selection()
        if not selected:
            messagebox.showwarning("Select Record", "Please select a transaction to delete.")
            return

        values = self.records_tree.item(selected[0], "values")
        rec_id = int(values[0])
        rec_type = values[1]
        rec_amt = values[4]
        rec_cat = values[3]

        # Confirmation Dialog
        confirmed = messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to permanently delete this record?\n\n"
            f"• Type: {rec_type}\n"
            f"• Category: {rec_cat}\n"
            f"• Amount: {rec_amt}\n\n"
            f"This operation cannot be undone.",
            icon="warning"
        )

        if not confirmed:
            return

        try:
            if rec_type == "Expense":
                database.delete_expense(rec_id)
            else:
                database.delete_income(rec_id)

            messagebox.showinfo("Deleted", f"{rec_type} record #{rec_id} deleted successfully.")
            self.load_records_table()
            self.update_status(f"Deleted {rec_type} #{rec_id}")
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to delete record: {str(e)}")

    def export_current_view_to_csv(self):
        """Exports currently filtered records from the view table to a CSV file."""
        filter_type = self.records_filter_var.get()
        kw = self.rec_search_var.get().strip()

        default_name = f"expenses_records_{date.today().strftime('%Y%m%d')}.csv"
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile=default_name,
            title="Save Records to CSV"
        )

        if not file_path:
            return

        try:
            records = database.get_combined_transactions(record_type=filter_type, keyword=kw)
            import csv
            with open(file_path, mode="w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["Type", "Date", "Category", "Amount", "Payment Method", "Description"])
                for r in records:
                    writer.writerow([r["trans_type"], r["date"], r["category_name"], f"{r['amount']:.2f}", r["payment_method"], r["description"] or ""])

            messagebox.showinfo("Export Successful", f"Exported {len(records)} records to:\n{file_path}")
            self.update_status(f"Exported {len(records)} records to CSV")
        except Exception as e:
            messagebox.showerror("Export Failed", str(e))

    # =========================================================================
    # SCREEN 5: MANAGE CATEGORIES (CRUD)
    # =========================================================================

    def build_categories_screen(self):
        """Screen for managing categories with CRUD operations and usage integrity check."""
        container = tk.Frame(self.content_frame, bg=self.COLOR_BG)
        container.pack(fill=tk.BOTH, expand=True)

        tk.Label(
            container,
            text="Category Management (Table 1 of 3)",
            font=("Segoe UI", 16, "bold"),
            bg=self.COLOR_BG,
            fg=self.COLOR_TEXT
        ).pack(anchor=tk.W, pady=(0, 4))

        tk.Label(
            container,
            text="Manage categories for Expenses and Income. Categories linked to existing transactions are protected from deletion.",
            font=("Segoe UI", 9),
            bg=self.COLOR_BG,
            fg=self.COLOR_TEXT_MUTED
        ).pack(anchor=tk.W, pady=(0, 12))

        # Add Category Input Bar
        add_bar = tk.Frame(container, bg=self.COLOR_CARD, padx=16, pady=12, highlightthickness=1, highlightbackground=self.COLOR_BORDER)
        add_bar.pack(fill=tk.X, pady=(0, 12))

        tk.Label(add_bar, text="New Category Name:", font=("Segoe UI", 9, "bold"), bg=self.COLOR_CARD).pack(side=tk.LEFT, padx=(0, 6))
        self.new_cat_name_var = tk.StringVar()
        ttk.Entry(add_bar, textvariable=self.new_cat_name_var, width=22, font=("Segoe UI", 10)).pack(side=tk.LEFT, padx=(0, 12))

        tk.Label(add_bar, text="Type:", font=("Segoe UI", 9, "bold"), bg=self.COLOR_CARD).pack(side=tk.LEFT, padx=(0, 6))
        self.new_cat_type_var = tk.StringVar(value="Expense")
        ttk.Combobox(add_bar, textvariable=self.new_cat_type_var, values=["Expense", "Income"], state="readonly", width=10, font=("Segoe UI", 10)).pack(side=tk.LEFT, padx=(0, 12))

        ttk.Button(add_bar, text="➕ Add Category", style="Primary.TButton", command=self.add_category_action).pack(side=tk.LEFT)

        # Categories Table Frame
        table_frame = tk.Frame(container, bg=self.COLOR_CARD, highlightthickness=1, highlightbackground=self.COLOR_BORDER)
        table_frame.pack(fill=tk.BOTH, expand=True)

        cols = ("id", "name", "type", "usage")
        self.cat_tree = ttk.Treeview(table_frame, columns=cols, show="headings", selectmode="browse")

        self.cat_tree.heading("id", text="Category ID")
        self.cat_tree.heading("name", text="Category Name")
        self.cat_tree.heading("type", text="Type")
        self.cat_tree.heading("usage", text="Linked Transactions Count")

        self.cat_tree.column("id", width=90, anchor="center")
        self.cat_tree.column("name", width=260, anchor="w")
        self.cat_tree.column("type", width=120, anchor="center")
        self.cat_tree.column("usage", width=180, anchor="center")

        self.cat_tree.tag_configure("Expense", foreground="#dc2626")
        self.cat_tree.tag_configure("Income", foreground="#16a34a")

        v_scroll = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.cat_tree.yview)
        self.cat_tree.configure(yscrollcommand=v_scroll.set)

        self.cat_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # Action Buttons
        cat_actions = tk.Frame(container, bg=self.COLOR_BG, pady=10)
        cat_actions.pack(fill=tk.X)

        ttk.Button(cat_actions, text="✏️ Edit Category", style="Primary.TButton", command=self.edit_selected_category).pack(side=tk.LEFT, padx=(0, 6))
        ttk.Button(cat_actions, text="🗑️ Delete Category", style="Danger.TButton", command=self.delete_selected_category).pack(side=tk.LEFT, padx=6)
        ttk.Button(cat_actions, text="🔄 Refresh List", command=self.load_categories_table).pack(side=tk.LEFT, padx=6)

        self.load_categories_table()

    def load_categories_table(self):
        """Populates categories table with usage counts."""
        for item in self.cat_tree.get_children():
            self.cat_tree.delete(item)

        categories = database.get_category_usage_counts()
        for c in categories:
            self.cat_tree.insert(
                "",
                tk.END,
                values=(c["id"], c["name"], c["type"], f"{c['usage_count']} records"),
                tags=(c["type"],)
            )

    def add_category_action(self):
        """Adds a new category."""
        name = self.new_cat_name_var.get().strip()
        cat_type = self.new_cat_type_var.get().strip()

        if not name:
            messagebox.showerror("Validation Error", "Please provide a category name.")
            return

        try:
            database.add_category(name, cat_type)
            messagebox.showinfo("Success", f"Category '{name}' ({cat_type}) created!")
            self.new_cat_name_var.set("")
            self.load_categories_table()
            self.update_status(f"Added category '{name}'")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def edit_selected_category(self):
        """Edits selected category name."""
        selected = self.cat_tree.selection()
        if not selected:
            messagebox.showwarning("Select Category", "Please select a category to edit.")
            return

        values = self.cat_tree.item(selected[0], "values")
        cat_id = int(values[0])
        current_name = values[1]
        current_type = values[2]

        dlg = tk.Toplevel(self)
        dlg.title(f"Edit Category #{cat_id}")
        dlg.geometry("380x200")
        dlg.resizable(False, False)
        dlg.transient(self)
        dlg.grab_set()
        self.center_dialog(dlg, 380, 200)

        tk.Label(dlg, text="Edit Category", font=("Segoe UI", 11, "bold")).pack(pady=(16, 10))

        f = tk.Frame(dlg, padx=20)
        f.pack(fill=tk.BOTH, expand=True)

        tk.Label(f, text="Name:", font=("Segoe UI", 9, "bold")).grid(row=0, column=0, sticky="w", pady=6)
        name_var = tk.StringVar(value=current_name)
        ttk.Entry(f, textvariable=name_var, width=22, font=("Segoe UI", 10)).grid(row=0, column=1, sticky="w", pady=6)

        tk.Label(f, text="Type:", font=("Segoe UI", 9, "bold")).grid(row=1, column=0, sticky="w", pady=6)
        type_var = tk.StringVar(value=current_type)
        ttk.Combobox(f, textvariable=type_var, values=["Expense", "Income"], state="readonly", width=12, font=("Segoe UI", 10)).grid(row=1, column=1, sticky="w", pady=6)

        def do_update():
            new_name = name_var.get().strip()
            new_type = type_var.get().strip()
            try:
                database.update_category(cat_id, new_name, new_type)
                messagebox.showinfo("Success", "Category updated!", parent=dlg)
                dlg.destroy()
                self.load_categories_table()
            except Exception as ex:
                messagebox.showerror("Error", str(ex), parent=dlg)

        btn_box = tk.Frame(dlg, pady=10)
        btn_box.pack()
        ttk.Button(btn_box, text="Save", style="Primary.TButton", command=do_update).pack(side=tk.LEFT, padx=6)
        ttk.Button(btn_box, text="Cancel", command=dlg.destroy).pack(side=tk.LEFT)

    def delete_selected_category(self):
        """Deletes category, strictly enforcing foreign key safety."""
        selected = self.cat_tree.selection()
        if not selected:
            messagebox.showwarning("Select Category", "Please select a category to delete.")
            return

        values = self.cat_tree.item(selected[0], "values")
        cat_id = int(values[0])
        cat_name = values[1]

        confirmed = messagebox.askyesno(
            "Confirm Delete Category",
            f"Are you sure you want to delete category '{cat_name}'?\n\n"
            f"Note: If this category is being used by any expense or income record, "
            f"SQLite foreign key constraints will prevent deletion.",
            icon="warning"
        )
        if not confirmed:
            return

        try:
            database.delete_category(cat_id)
            messagebox.showinfo("Deleted", f"Category '{cat_name}' deleted successfully.")
            self.load_categories_table()
            self.update_status(f"Deleted category '{cat_name}'")
        except ValueError as ve:
            messagebox.showerror("Foreign Key Restriction", str(ve))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # =========================================================================
    # SCREEN 6: SEARCH & FILTER
    # =========================================================================

    def build_search_screen(self):
        """Multi-criteria search screen with date range, category, payment method filters."""
        container = tk.Frame(self.content_frame, bg=self.COLOR_BG)
        container.pack(fill=tk.BOTH, expand=True)

        tk.Label(
            container,
            text="Search & Multi-Filter Transactions",
            font=("Segoe UI", 16, "bold"),
            bg=self.COLOR_BG,
            fg=self.COLOR_TEXT
        ).pack(anchor=tk.W, pady=(0, 4))

        tk.Label(
            container,
            text="Filter transactions by date range, payment method, category, and keyword.",
            font=("Segoe UI", 9),
            bg=self.COLOR_BG,
            fg=self.COLOR_TEXT_MUTED
        ).pack(anchor=tk.W, pady=(0, 10))

        # Filter Parameters Card
        filter_panel = tk.Frame(container, bg=self.COLOR_CARD, padx=16, pady=12, highlightthickness=1, highlightbackground=self.COLOR_BORDER)
        filter_panel.pack(fill=tk.X, pady=(0, 10))

        # Row 1: Keyword & Type
        tk.Label(filter_panel, text="Keyword:", font=("Segoe UI", 9, "bold"), bg=self.COLOR_CARD).grid(row=0, column=0, sticky="w", pady=4)
        self.srch_kw_var = tk.StringVar()
        ttk.Entry(filter_panel, textvariable=self.srch_kw_var, width=20).grid(row=0, column=1, sticky="w", padx=6, pady=4)

        tk.Label(filter_panel, text="Type:", font=("Segoe UI", 9, "bold"), bg=self.COLOR_CARD).grid(row=0, column=2, sticky="w", padx=(12, 0), pady=4)
        self.srch_type_var = tk.StringVar(value="All")
        ttk.Combobox(filter_panel, textvariable=self.srch_type_var, values=["All", "Expense", "Income"], state="readonly", width=10).grid(row=0, column=3, sticky="w", padx=6, pady=4)

        tk.Label(filter_panel, text="Payment Method:", font=("Segoe UI", 9, "bold"), bg=self.COLOR_CARD).grid(row=0, column=4, sticky="w", padx=(12, 0), pady=4)
        self.srch_pm_var = tk.StringVar(value="All")
        ttk.Combobox(filter_panel, textvariable=self.srch_pm_var, values=["All"] + self.PAYMENT_METHODS, state="readonly", width=14).grid(row=0, column=5, sticky="w", padx=6, pady=4)

        # Row 2: Date From & Date To
        tk.Label(filter_panel, text="From Date:", font=("Segoe UI", 9, "bold"), bg=self.COLOR_CARD).grid(row=1, column=0, sticky="w", pady=4)
        self.srch_from_var = tk.StringVar()
        ttk.Entry(filter_panel, textvariable=self.srch_from_var, width=20).grid(row=1, column=1, sticky="w", padx=6, pady=4)

        tk.Label(filter_panel, text="To Date:", font=("Segoe UI", 9, "bold"), bg=self.COLOR_CARD).grid(row=1, column=2, sticky="w", padx=(12, 0), pady=4)
        self.srch_to_var = tk.StringVar()
        ttk.Entry(filter_panel, textvariable=self.srch_to_var, width=12).grid(row=1, column=3, sticky="w", padx=6, pady=4)

        # Buttons on filter panel
        btn_box = tk.Frame(filter_panel, bg=self.COLOR_CARD)
        btn_box.grid(row=1, column=4, columnspan=2, sticky="e", pady=4)

        ttk.Button(btn_box, text="🔍 Apply Filter", style="Primary.TButton", command=self.apply_search_filter).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_box, text="🔄 Reset", command=self.reset_search_filter).pack(side=tk.LEFT, padx=4)

        # Results Summary Banner
        self.srch_result_lbl = tk.Label(
            container,
            text="Ready to search.",
            font=("Segoe UI", 9, "bold"),
            bg=self.COLOR_BG,
            fg=self.COLOR_TEXT
        )
        self.srch_result_lbl.pack(anchor=tk.W, pady=(0, 6))

        # Results Table
        table_frame = tk.Frame(container, bg=self.COLOR_CARD, highlightthickness=1, highlightbackground=self.COLOR_BORDER)
        table_frame.pack(fill=tk.BOTH, expand=True)

        cols = ("id", "type", "date", "category", "amount", "pm", "desc")
        self.srch_tree = ttk.Treeview(table_frame, columns=cols, show="headings")

        self.srch_tree.heading("id", text="ID")
        self.srch_tree.heading("type", text="Type")
        self.srch_tree.heading("date", text="Date")
        self.srch_tree.heading("category", text="Category")
        self.srch_tree.heading("amount", text="Amount")
        self.srch_tree.heading("pm", text="Payment Method")
        self.srch_tree.heading("desc", text="Description")

        self.srch_tree.column("id", width=45, anchor="center")
        self.srch_tree.column("type", width=75, anchor="center")
        self.srch_tree.column("date", width=90, anchor="center")
        self.srch_tree.column("category", width=150, anchor="w")
        self.srch_tree.column("amount", width=100, anchor="e")
        self.srch_tree.column("pm", width=120, anchor="w")
        self.srch_tree.column("desc", width=250, anchor="w")

        self.srch_tree.tag_configure("Expense", foreground="#dc2626")
        self.srch_tree.tag_configure("Income", foreground="#16a34a")

        v_scroll = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.srch_tree.yview)
        self.srch_tree.configure(yscrollcommand=v_scroll.set)

        self.srch_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.apply_search_filter()

    def reset_search_filter(self):
        """Clears search filter inputs."""
        self.srch_kw_var.set("")
        self.srch_type_var.set("All")
        self.srch_pm_var.set("All")
        self.srch_from_var.set("")
        self.srch_to_var.set("")
        self.apply_search_filter()

    def apply_search_filter(self):
        """Applies filter criteria and displays matching records."""
        for item in self.srch_tree.get_children():
            self.srch_tree.delete(item)

        kw = self.srch_kw_var.get().strip()
        t_type = self.srch_type_var.get().strip()
        pm = self.srch_pm_var.get().strip()
        f_date = self.srch_from_var.get().strip()
        t_date = self.srch_to_var.get().strip()

        # Date validation if entered
        if f_date:
            try:
                database.validate_date_format(f_date)
            except ValueError as ex:
                messagebox.showerror("Validation Error", f"From Date: {str(ex)}")
                return

        if t_date:
            try:
                database.validate_date_format(t_date)
            except ValueError as ex:
                messagebox.showerror("Validation Error", f"To Date: {str(ex)}")
                return

        records = database.get_combined_transactions(
            record_type=t_type,
            keyword=kw,
            start_date=f_date,
            end_date=t_date,
            payment_method=pm
        )

        total_income = sum(r["amount"] for r in records if r["trans_type"] == "Income")
        total_expense = sum(r["amount"] for r in records if r["trans_type"] == "Expense")

        for r in records:
            amt_display = f"₹ {r['amount']:,.2f}"
            self.srch_tree.insert(
                "",
                tk.END,
                values=(r["id"], r["trans_type"], r["date"], r["category_name"], amt_display, r["payment_method"], r["description"] or ""),
                tags=(r["trans_type"],)
            )

        self.srch_result_lbl.config(
            text=f"Matched {len(records)} transactions  |  Total Income: ₹{total_income:,.2f}  |  Total Expense: ₹{total_expense:,.2f}  |  Net: ₹{(total_income - total_expense):,.2f}"
        )

    # =========================================================================
    # SCREEN 7: REPORTS & ANALYTICS
    # =========================================================================

    def build_reports_screen(self):
        """Generates financial report table, summary totals, and graphical chart."""
        container = tk.Frame(self.content_frame, bg=self.COLOR_BG)
        container.pack(fill=tk.BOTH, expand=True)

        # Header with Period Selector
        top_bar = tk.Frame(container, bg=self.COLOR_BG)
        top_bar.pack(fill=tk.X, pady=(0, 10))

        tk.Label(
            top_bar,
            text="Financial Reports & Analytics",
            font=("Segoe UI", 16, "bold"),
            bg=self.COLOR_BG,
            fg=self.COLOR_TEXT
        ).pack(side=tk.LEFT)

        filter_frame = tk.Frame(top_bar, bg=self.COLOR_BG)
        filter_frame.pack(side=tk.RIGHT)

        tk.Label(filter_frame, text="Timeframe:", font=("Segoe UI", 9, "bold"), bg=self.COLOR_BG).pack(side=tk.LEFT, padx=4)
        self.rep_timeframe_var = tk.StringVar(value="All Time")
        rep_combo = ttk.Combobox(
            filter_frame,
            textvariable=self.rep_timeframe_var,
            values=["All Time", "Current Month", "Last 30 Days", "Current Year"],
            state="readonly",
            width=15
        )
        rep_combo.pack(side=tk.LEFT, padx=4)
        rep_combo.bind("<<ComboboxSelected>>", lambda event: self.render_report_data())

        ttk.Button(filter_frame, text="🔄 Generate", command=self.render_report_data).pack(side=tk.LEFT, padx=4)
        ttk.Button(filter_frame, text="📄 Export CSV", command=self.export_report_csv).pack(side=tk.LEFT, padx=4)

        # Report KPI Bar
        self.rep_kpi_frame = tk.Frame(container, bg=self.COLOR_CARD, padx=16, pady=10, highlightthickness=1, highlightbackground=self.COLOR_BORDER)
        self.rep_kpi_frame.pack(fill=tk.X, pady=(0, 12))

        self.rep_income_lbl = tk.Label(self.rep_kpi_frame, font=("Segoe UI", 11, "bold"), fg=self.COLOR_SUCCESS, bg=self.COLOR_CARD)
        self.rep_income_lbl.pack(side=tk.LEFT, padx=16)

        self.rep_expense_lbl = tk.Label(self.rep_kpi_frame, font=("Segoe UI", 11, "bold"), fg=self.COLOR_DANGER, bg=self.COLOR_CARD)
        self.rep_expense_lbl.pack(side=tk.LEFT, padx=16)

        self.rep_balance_lbl = tk.Label(self.rep_kpi_frame, font=("Segoe UI", 11, "bold"), fg=self.COLOR_INFO, bg=self.COLOR_CARD)
        self.rep_balance_lbl.pack(side=tk.LEFT, padx=16)

        # Split Content Area: Left = Category Breakdown Table; Right = Matplotlib Chart or Canvas
        self.rep_body = tk.Frame(container, bg=self.COLOR_BG)
        self.rep_body.pack(fill=tk.BOTH, expand=True)
        self.rep_body.columnconfigure(0, weight=3)
        self.rep_body.columnconfigure(1, weight=3)

        # Left Table Frame
        self.rep_left_card = tk.Frame(self.rep_body, bg=self.COLOR_CARD, highlightthickness=1, highlightbackground=self.COLOR_BORDER)
        self.rep_left_card.grid(row=0, column=0, sticky="nsew", padx=(0, 6))

        tk.Label(self.rep_left_card, text="Category-wise Spending Breakdown", font=("Segoe UI", 11, "bold"), bg=self.COLOR_CARD).pack(anchor=tk.W, padx=12, pady=8)

        cols = ("cat", "items", "amount", "pct")
        self.rep_tree = ttk.Treeview(self.rep_left_card, columns=cols, show="headings", height=10)
        self.rep_tree.heading("cat", text="Category")
        self.rep_tree.heading("items", text="Count")
        self.rep_tree.heading("amount", text="Total (₹)")
        self.rep_tree.heading("pct", text="Share (%)")

        self.rep_tree.column("cat", width=140, anchor="w")
        self.rep_tree.column("items", width=60, anchor="center")
        self.rep_tree.column("amount", width=95, anchor="e")
        self.rep_tree.column("pct", width=80, anchor="e")

        self.rep_tree.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))

        # Right Chart Card
        self.rep_right_card = tk.Frame(self.rep_body, bg=self.COLOR_CARD, highlightthickness=1, highlightbackground=self.COLOR_BORDER)
        self.rep_right_card.grid(row=0, column=1, sticky="nsew", padx=(6, 0))

        tk.Label(self.rep_right_card, text="Visual Distribution", font=("Segoe UI", 11, "bold"), bg=self.COLOR_CARD).pack(anchor=tk.W, padx=12, pady=8)

        self.chart_container = tk.Frame(self.rep_right_card, bg=self.COLOR_CARD)
        self.chart_container.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))

        self.render_report_data()

    def get_timeframe_dates(self):
        """Calculates start_date and end_date strings based on timeframe dropdown."""
        tf = self.rep_timeframe_var.get()
        today = date.today()
        start_date = ""
        end_date = today.strftime("%Y-%m-%d")

        if tf == "Current Month":
            start_date = date(today.year, today.month, 1).strftime("%Y-%m-%d")
        elif tf == "Last 30 Days":
            from datetime import timedelta
            start_date = (today - timedelta(days=30)).strftime("%Y-%m-%d")
        elif tf == "Current Year":
            start_date = date(today.year, 1, 1).strftime("%Y-%m-%d")

        return start_date, end_date

    def render_report_data(self):
        """Populates report metrics, table, and graphical chart."""
        start_date, end_date = self.get_timeframe_dates()

        summary = database.get_financial_summary(start_date=start_date, end_date=end_date)
        breakdown = database.get_expense_category_breakdown(start_date=start_date, end_date=end_date)

        # Update KPI labels
        self.rep_income_lbl.config(text=f"Total Income: ₹{summary['total_income']:,.2f}")
        self.rep_expense_lbl.config(text=f"Total Expenses: ₹{summary['total_expenses']:,.2f}")
        bal = summary["balance"]
        bal_text = f"Net Balance: ₹{bal:,.2f}"
        self.rep_balance_lbl.config(text=bal_text, fg=self.COLOR_SUCCESS if bal >= 0 else self.COLOR_DANGER)

        # Update Table
        for item in self.rep_tree.get_children():
            self.rep_tree.delete(item)

        total_exp = summary["total_expenses"] or 1.0

        categories = []
        amounts = []

        for row in breakdown:
            cat_name = row["category_name"]
            amt = row["total_amount"]
            count = row["item_count"]
            pct = (amt / total_exp) * 100

            categories.append(cat_name)
            amounts.append(amt)

            self.rep_tree.insert(
                "",
                tk.END,
                values=(cat_name, count, f"₹{amt:,.2f}", f"{pct:.1f}%")
            )

        # Clear old chart
        for w in self.chart_container.winfo_children():
            w.destroy()

        # Render Chart: Matplotlib if available, otherwise native Canvas bars
        if MATPLOTLIB_AVAILABLE and amounts:
            try:
                fig = Figure(figsize=(4.5, 3.2), dpi=90, facecolor="#ffffff")
                ax = fig.add_subplot(111)

                # Up to 6 slices + Other
                if len(categories) > 6:
                    top_cats = categories[:5] + ["Other"]
                    top_amts = amounts[:5] + [sum(amounts[5:])]
                else:
                    top_cats = categories
                    top_amts = amounts

                colors = ["#4f46e5", "#06b6d4", "#10b981", "#f59e0b", "#ec4899", "#8b5cf6", "#64748b"]
                wedges, texts, autotexts = ax.pie(
                    top_amts,
                    labels=top_cats,
                    autopct="%1.1f%%",
                    startangle=140,
                    colors=colors[:len(top_amts)],
                    textprops=dict(fontsize=8)
                )
                for autotext in autotexts:
                    autotext.set_color("white")
                    autotext.set_fontweight("bold")

                fig.tight_layout()
                canvas = FigureCanvasTkAgg(fig, master=self.chart_container)
                canvas.draw()
                canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            except Exception:
                self.render_fallback_canvas_chart(categories, amounts, total_exp)
        else:
            self.render_fallback_canvas_chart(categories, amounts, total_exp)

    def render_fallback_canvas_chart(self, categories, amounts, total_exp):
        """Native Tkinter canvas horizontal bar chart fallback."""
        canvas = tk.Canvas(self.chart_container, bg="#ffffff", highlightthickness=0)
        canvas.pack(fill=tk.BOTH, expand=True)

        if not amounts:
            canvas.create_text(160, 100, text="No expense data for this period", fill=self.COLOR_TEXT_MUTED, font=("Segoe UI", 10))
            return

        y = 20
        colors = ["#4f46e5", "#06b6d4", "#10b981", "#f59e0b", "#ec4899", "#8b5cf6"]

        for i, (cat, amt) in enumerate(zip(categories[:6], amounts[:6])):
            pct = (amt / total_exp) * 100
            canvas.create_text(20, y + 8, text=cat[:16], anchor="w", font=("Segoe UI", 8, "bold"), fill=self.COLOR_TEXT)
            canvas.create_text(280, y + 8, text=f"₹{amt:,.0f} ({pct:.0f}%)", anchor="e", font=("Segoe UI", 8), fill=self.COLOR_TEXT_MUTED)

            # Bar
            canvas.create_rectangle(20, y + 20, 280, y + 28, fill="#f1f5f9", outline="")
            bar_w = int(2.6 * pct)
            if bar_w > 0:
                canvas.create_rectangle(20, y + 20, 20 + bar_w, y + 28, fill=colors[i % len(colors)], outline="")

            y += 42

    def export_report_csv(self):
        """Exports report summary to a CSV file."""
        start_date, end_date = self.get_timeframe_dates()
        default_name = f"expense_report_{date.today().strftime('%Y%m%d')}.csv"
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile=default_name,
            title="Save Financial Report"
        )
        if not file_path:
            return

        try:
            count = database.export_to_csv(file_path, start_date=start_date, end_date=end_date)
            messagebox.showinfo("Export Successful", f"Saved {count} report transactions to:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Export Failed", str(e))

    # =========================================================================
    # SCREEN 8: CSV IMPORT & EXPORT
    # =========================================================================

    def build_import_export_screen(self):
        """Screen dedicated to CSV data backup, export, and import restoration."""
        container = tk.Frame(self.content_frame, bg=self.COLOR_BG)
        container.pack(fill=tk.BOTH, expand=True)

        tk.Label(
            container,
            text="Data Backup & CSV Transfer",
            font=("Segoe UI", 16, "bold"),
            bg=self.COLOR_BG,
            fg=self.COLOR_TEXT
        ).pack(anchor=tk.W, pady=(0, 4))

        tk.Label(
            container,
            text="Export your financial records to CSV format, or import existing CSV datasets back into SQLite.",
            font=("Segoe UI", 9),
            bg=self.COLOR_BG,
            fg=self.COLOR_TEXT_MUTED
        ).pack(anchor=tk.W, pady=(0, 16))

        # Two Main Cards: Export Card (Left) & Import Card (Right)
        panels = tk.Frame(container, bg=self.COLOR_BG)
        panels.pack(fill=tk.BOTH, expand=True)
        panels.columnconfigure(0, weight=1)
        panels.columnconfigure(1, weight=1)

        # Card 1: Export
        exp_card = tk.Frame(panels, bg=self.COLOR_CARD, padx=20, pady=20, highlightthickness=1, highlightbackground=self.COLOR_BORDER)
        exp_card.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        tk.Label(exp_card, text="📤 Export Data to CSV", font=("Segoe UI", 12, "bold"), bg=self.COLOR_CARD, fg=self.COLOR_TEXT).pack(anchor=tk.W, pady=(0, 8))
        tk.Label(
            exp_card,
            text="Saves your transactions into a standard CSV file with Type, Date, Category, Amount, Payment Method, and Description columns.",
            font=("Segoe UI", 9),
            bg=self.COLOR_CARD,
            fg=self.COLOR_TEXT_MUTED,
            wraplength=380,
            justify=tk.LEFT
        ).pack(anchor=tk.W, pady=(0, 14))

        tk.Label(exp_card, text="Choose Records to Export:", font=("Segoe UI", 9, "bold"), bg=self.COLOR_CARD).pack(anchor=tk.W, pady=(0, 4))
        self.exp_scope_var = tk.StringVar(value="All")
        for opt in [("All Transactions (Expenses + Income)", "All"), ("Expenses Only", "Expense"), ("Income Only", "Income")]:
            tk.Radiobutton(exp_card, text=opt[0], value=opt[1], variable=self.exp_scope_var, bg=self.COLOR_CARD, font=("Segoe UI", 9)).pack(anchor=tk.W, pady=2)

        ttk.Button(exp_card, text="💾 Export Now...", style="Primary.TButton", command=self.do_export_dialog).pack(anchor=tk.W, pady=(16, 0))

        # Card 2: Import
        imp_card = tk.Frame(panels, bg=self.COLOR_CARD, padx=20, pady=20, highlightthickness=1, highlightbackground=self.COLOR_BORDER)
        imp_card.grid(row=0, column=1, sticky="nsew", padx=(8, 0))

        tk.Label(imp_card, text="📥 Import Records from CSV", font=("Segoe UI", 12, "bold"), bg=self.COLOR_CARD, fg=self.COLOR_TEXT).pack(anchor=tk.W, pady=(0, 8))
        tk.Label(
            imp_card,
            text="Imports CSV data directly into SQLite. Any new categories found in the CSV will be created automatically.",
            font=("Segoe UI", 9),
            bg=self.COLOR_CARD,
            fg=self.COLOR_TEXT_MUTED,
            wraplength=380,
            justify=tk.LEFT
        ).pack(anchor=tk.W, pady=(0, 14))

        # Instructions / Sample file pointer
        sample_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sample_expenses_import.csv")
        sample_exists = os.path.exists(sample_path)

        info_box = tk.Frame(imp_card, bg="#f1f5f9", padx=10, pady=8)
        info_box.pack(fill=tk.X, pady=(0, 12))
        tk.Label(
            info_box,
            text="Expected CSV headers:\nType, Date, Category, Amount, Payment Method, Description",
            font=("Segoe UI", 8, "bold"),
            bg="#f1f5f9",
            fg=self.COLOR_PRIMARY,
            justify=tk.LEFT
        ).pack(anchor=tk.W)

        btn_row = tk.Frame(imp_card, bg=self.COLOR_CARD)
        btn_row.pack(anchor=tk.W, pady=(6, 0))

        ttk.Button(btn_row, text="📂 Select & Import CSV...", style="Success.TButton", command=self.do_import_dialog).pack(side=tk.LEFT, padx=(0, 8))

        if sample_exists:
            tk.Button(
                btn_row,
                text="Test Sample CSV",
                font=("Segoe UI", 9),
                bg="#f1f5f9",
                fg=self.COLOR_ACCENT,
                bd=1,
                cursor="hand2",
                command=lambda: self.execute_csv_import(sample_path)
            ).pack(side=tk.LEFT)

    def do_export_dialog(self):
        """Prompts user for save destination and exports transactions."""
        scope = self.exp_scope_var.get()
        default_file = f"expense_manager_export_{scope.lower()}_{date.today().strftime('%Y%m%d')}.csv"
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile=default_file,
            title="Export Records to CSV"
        )
        if not file_path:
            return

        try:
            count = database.export_to_csv(file_path, record_type=scope)
            messagebox.showinfo("Export Complete", f"Successfully exported {count} records to:\n{file_path}")
            self.update_status(f"Exported {count} records to {os.path.basename(file_path)}")
        except Exception as e:
            messagebox.showerror("Export Failed", str(e))

    def do_import_dialog(self):
        """Prompts user to select a CSV file and imports records."""
        file_path = filedialog.askopenfilename(
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Select CSV File to Import"
        )
        if not file_path:
            return
        self.execute_csv_import(file_path)

    def execute_csv_import(self, file_path):
        """Executes the import process with progress and result confirmation."""
        try:
            imported, skipped, errors = database.import_from_csv(file_path)

            msg = f"CSV Import Summary:\n\n• Successfully imported: {imported} records\n• Skipped rows: {skipped}"
            if errors:
                err_details = "\n".join(errors[:5])
                if len(errors) > 5:
                    err_details += f"\n... and {len(errors) - 5} more."
                msg += f"\n\nRow Warnings / Errors:\n{err_details}"

            messagebox.showinfo("Import Results", msg)
            self.update_status(f"Imported {imported} records from {os.path.basename(file_path)}")
        except Exception as e:
            messagebox.showerror("Import Error", f"Failed to import file:\n{str(e)}")

    # =========================================================================
    # DIALOGS & UTILITY METHODS
    # =========================================================================

    def center_dialog(self, dlg, width, height):
        """Centers a modal dialog relative to the parent application window."""
        self.update_idletasks()
        parent_x = self.winfo_x()
        parent_y = self.winfo_y()
        parent_w = self.winfo_width()
        parent_h = self.winfo_height()

        x = parent_x + max(0, int((parent_w - width) / 2))
        y = parent_y + max(0, int((parent_h - height) / 2))
        dlg.geometry(f"{width}x{height}+{x}+{y}")

    def sort_tree_column(self, tree, col, reverse):
        """Sorts Treeview rows when clicking a column header."""
        l = [(tree.set(k, col), k) for k in tree.get_children("")]
        
        # Try numeric sort if possible
        try:
            l.sort(key=lambda t: float(t[0].replace("₹", "").replace(",", "").strip()), reverse=reverse)
        except ValueError:
            l.sort(reverse=reverse)

        for index, (val, k) in enumerate(l):
            tree.move(k, "", index)

        tree.heading(col, command=lambda: self.sort_tree_column(tree, col, not reverse))

    def confirm_reset_sample_data(self):
        """Resets the SQLite database with default sample records."""
        confirmed = messagebox.askyesno(
            "Confirm Reset Sample Data",
            "This will clear current database records and re-seed clean default categories & sample transactions.\n\nContinue?",
            icon="warning"
        )
        if confirmed:
            try:
                conn = database.get_connection()
                cursor = conn.cursor()
                cursor.execute("DELETE FROM expenses;")
                cursor.execute("DELETE FROM income;")
                cursor.execute("DELETE FROM categories;")
                cursor.execute("DELETE FROM sqlite_sequence;")
                conn.commit()
                database.seed_default_data(conn)
                conn.close()

                messagebox.showinfo("Reset Complete", "Database reset and seeded with initial sample practical data!")
                self.refresh_current_screen()
                self.update_status("Database reset to sample state.")
            except Exception as e:
                messagebox.showerror("Reset Error", str(e))

    def show_schema_dialog(self):
        """Displays database relational schema info for college viva."""
        dlg = tk.Toplevel(self)
        dlg.title("SQLite Relational Database Schema")
        dlg.geometry("540x460")
        dlg.transient(self)
        self.center_dialog(dlg, 540, 460)

        schema_text = (
            "====================================================\n"
            "   PERSONAL EXPENSE MANAGER - 3 SQLite TABLES\n"
            "====================================================\n\n"
            "1. TABLE: categories\n"
            "   - id: INTEGER PRIMARY KEY AUTOINCREMENT\n"
            "   - name: TEXT UNIQUE NOT NULL\n"
            "   - type: TEXT ('Expense' or 'Income')\n\n"
            "2. TABLE: expenses\n"
            "   - id: INTEGER PRIMARY KEY AUTOINCREMENT\n"
            "   - category_id: INTEGER NOT NULL (FOREIGN KEY -> categories.id)\n"
            "   - amount: REAL NOT NULL (> 0)\n"
            "   - date: TEXT NOT NULL (YYYY-MM-DD)\n"
            "   - payment_method: TEXT NOT NULL\n"
            "   - description: TEXT\n"
            "   - created_at: TIMESTAMP DEFAULT CURRENT_TIMESTAMP\n\n"
            "3. TABLE: income\n"
            "   - id: INTEGER PRIMARY KEY AUTOINCREMENT\n"
            "   - category_id: INTEGER NOT NULL (FOREIGN KEY -> categories.id)\n"
            "   - amount: REAL NOT NULL (> 0)\n"
            "   - date: TEXT NOT NULL (YYYY-MM-DD)\n"
            "   - payment_method: TEXT NOT NULL\n"
            "   - description: TEXT\n"
            "   - created_at: TIMESTAMP DEFAULT CURRENT_TIMESTAMP\n\n"
            "RELATIONSHIPS:\n"
            "• categories 1 --- N expenses (ON DELETE RESTRICT)\n"
            "• categories 1 --- N income   (ON DELETE RESTRICT)\n"
            "Foreign keys are enforced via: PRAGMA foreign_keys = ON;\n"
        )

        txt = tk.Text(dlg, font=("Consolas", 9), padx=10, pady=10, bg="#f8fafc", wrap=tk.WORD)
        txt.insert("1.0", schema_text)
        txt.config(state="disabled")
        txt.pack(fill=tk.BOTH, expand=True)

        ttk.Button(dlg, text="Close", command=dlg.destroy).pack(pady=8)

    def show_about_dialog(self):
        """Displays college practical project metadata."""
        messagebox.showinfo(
            "About Project",
            "Personal Expense Manager\n"
            "Desktop Application built with Python Tkinter & SQLite.\n\n"
            "Features:\n"
            "• Full CRUD operations with input validation\n"
            "• 3 Relational SQLite tables with Foreign Key constraints\n"
            "• Search, date & category filtering\n"
            "• Visual financial analytics and category breakdown\n"
            "• CSV Data Export and Import\n"
            "• College Practical / Viva Ready"
        )


def main():
    """Application Entry Point."""
    app = ExpenseManagerApp()
    app.mainloop()


if __name__ == "__main__":
    main()
