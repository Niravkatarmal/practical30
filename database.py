"""
database.py - Database Manager for Personal Expense Manager
Handles SQLite database connection, schema creation, migrations, CRUD operations,
and CSV export/import functionality.
"""

import sqlite3
import os
import csv
from datetime import datetime

DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "expense_manager.db")


def get_connection():
    """Create and return a SQLite database connection with foreign key support enabled."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db():
    """
    Initializes the database tables:
    1. categories (Stores categories for both expenses and income)
    2. expenses   (Stores expense transactions linked to category_id)
    3. income     (Stores income transactions linked to category_id)
    Also seeds default categories and sample transactions if the database is newly created.
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Table 1: Categories
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            type TEXT NOT NULL CHECK(type IN ('Expense', 'Income'))
        );
    """)

    # Table 2: Expenses
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_id INTEGER NOT NULL,
            amount REAL NOT NULL CHECK(amount > 0),
            date TEXT NOT NULL,
            payment_method TEXT NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (category_id) REFERENCES categories (id) ON DELETE RESTRICT
        );
    """)

    # Table 3: Income
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS income (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_id INTEGER NOT NULL,
            amount REAL NOT NULL CHECK(amount > 0),
            date TEXT NOT NULL,
            payment_method TEXT NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (category_id) REFERENCES categories (id) ON DELETE RESTRICT
        );
    """)

    conn.commit()

    # Seed initial categories if none exist
    cursor.execute("SELECT COUNT(*) FROM categories")
    if cursor.fetchone()[0] == 0:
        seed_default_data(conn)

    conn.close()


def seed_default_data(conn):
    """Seeds default categories and realistic sample expenses/income for demonstration."""
    cursor = conn.cursor()

    default_categories = [
        # Expense categories
        ("Food & Dining", "Expense"),
        ("College & Books", "Expense"),
        ("Transportation", "Expense"),
        ("Hostel & Rent", "Expense"),
        ("Utilities & Internet", "Expense"),
        ("Entertainment & Leisure", "Expense"),
        ("Groceries", "Expense"),
        ("Healthcare & Meds", "Expense"),
        ("Shopping & Gadgets", "Expense"),
        # Income categories
        ("Monthly Allowance / Pocket Money", "Income"),
        ("College Scholarship", "Income"),
        ("Freelance Project", "Income"),
        ("Part-time Tutoring", "Income"),
        ("Gifts & Rewards", "Income"),
    ]

    for name, cat_type in default_categories:
        cursor.execute(
            "INSERT OR IGNORE INTO categories (name, type) VALUES (?, ?)",
            (name, cat_type)
        )
    conn.commit()

    # Retrieve category IDs
    cat_map = {}
    cursor.execute("SELECT id, name FROM categories")
    for row in cursor.fetchall():
        cat_map[row["name"]] = row["id"]

    # Sample income records
    sample_income = [
        (cat_map.get("Monthly Allowance / Pocket Money"), 15000.0, "2026-10-01", "Bank Transfer", "Monthly allowance from parents"),
        (cat_map.get("Freelance Project"), 8500.0, "2026-10-08", "UPI / Online", "Web development mini-project payment"),
        (cat_map.get("Part-time Tutoring"), 3000.0, "2026-10-15", "Cash", "High school math tutoring fee"),
    ]

    for item in sample_income:
        if item[0]:
            cursor.execute(
                "INSERT INTO income (category_id, amount, date, payment_method, description) VALUES (?, ?, ?, ?, ?)",
                item
            )

    # Sample expense records
    sample_expenses = [
        (cat_map.get("Hostel & Rent"), 6000.0, "2026-10-02", "Bank Transfer", "Hostel room accommodation fee"),
        (cat_map.get("College & Books"), 1450.0, "2026-10-05", "UPI / Online", "Python programming reference books and lab manual"),
        (cat_map.get("Food & Dining"), 320.0, "2026-10-06", "Cash", "Lunch at college canteen with friends"),
        (cat_map.get("Transportation"), 450.0, "2026-10-09", "UPI / Online", "Monthly metro travel smart card recharge"),
        (cat_map.get("Utilities & Internet"), 799.0, "2026-10-11", "Debit Card", "High-speed broadband Wi-Fi bill"),
        (cat_map.get("Groceries"), 1200.0, "2026-10-14", "UPI / Online", "Weekly snacks, fruits, and milk"),
        (cat_map.get("Entertainment & Leisure"), 480.0, "2026-10-18", "Credit Card", "Cinema movie ticket & popcorn"),
        (cat_map.get("Healthcare & Meds"), 250.0, "2026-10-20", "Cash", "Vitamins and first aid supplies"),
    ]

    for item in sample_expenses:
        if item[0]:
            cursor.execute(
                "INSERT INTO expenses (category_id, amount, date, payment_method, description) VALUES (?, ?, ?, ?, ?)",
                item
            )

    conn.commit()


# ==========================================
# CATEGORIES CRUD
# ==========================================

def get_categories(cat_type=None):
    """Retrieve categories. Filter by 'Expense' or 'Income' if cat_type is given."""
    conn = get_connection()
    cursor = conn.cursor()
    if cat_type:
        cursor.execute("SELECT * FROM categories WHERE type = ? ORDER BY name ASC", (cat_type,))
    else:
        cursor.execute("SELECT * FROM categories ORDER BY type DESC, name ASC")
    rows = cursor.fetchall()
    conn.close()
    return rows


def add_category(name, cat_type):
    """Add a new category."""
    name = name.strip()
    if not name:
        raise ValueError("Category name cannot be empty.")
    if cat_type not in ('Expense', 'Income'):
        raise ValueError("Category type must be 'Expense' or 'Income'.")

    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO categories (name, type) VALUES (?, ?)", (name, cat_type))
        conn.commit()
        cat_id = cursor.lastrowid
        return cat_id
    except sqlite3.IntegrityError:
        raise ValueError(f"Category '{name}' already exists.")
    finally:
        conn.close()


def update_category(cat_id, name, cat_type):
    """Update an existing category's name and type."""
    name = name.strip()
    if not name:
        raise ValueError("Category name cannot be empty.")
    if cat_type not in ('Expense', 'Income'):
        raise ValueError("Category type must be 'Expense' or 'Income'.")

    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE categories SET name = ?, type = ? WHERE id = ?", (name, cat_type, cat_id))
        conn.commit()
    except sqlite3.IntegrityError:
        raise ValueError(f"A category named '{name}' already exists.")
    finally:
        conn.close()


def delete_category(cat_id):
    """
    Delete a category.
    Raises ValueError if category is currently referenced by any expense or income record.
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Check expenses reference
    cursor.execute("SELECT COUNT(*) FROM expenses WHERE category_id = ?", (cat_id,))
    if cursor.fetchone()[0] > 0:
        conn.close()
        raise ValueError("Cannot delete category: It is currently used in expense records.")

    # Check income reference
    cursor.execute("SELECT COUNT(*) FROM income WHERE category_id = ?", (cat_id,))
    if cursor.fetchone()[0] > 0:
        conn.close()
        raise ValueError("Cannot delete category: It is currently used in income records.")

    cursor.execute("DELETE FROM categories WHERE id = ?", (cat_id,))
    conn.commit()
    conn.close()


def get_category_by_id(cat_id):
    """Fetch single category record by ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM categories WHERE id = ?", (cat_id,))
    row = cursor.fetchone()
    conn.close()
    return row


def get_category_usage_counts():
    """Returns list of categories with usage count in expenses/income."""
    conn = get_connection()
    cursor = conn.cursor()
    query = """
        SELECT c.id, c.name, c.type,
               (CASE 
                  WHEN c.type = 'Expense' THEN (SELECT COUNT(*) FROM expenses e WHERE e.category_id = c.id)
                  ELSE (SELECT COUNT(*) FROM income i WHERE i.category_id = c.id)
                END) AS usage_count
        FROM categories c
        ORDER BY c.type DESC, c.name ASC
    """
    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()
    return rows


# ==========================================
# EXPENSES CRUD
# ==========================================

def add_expense(category_id, amount, date_str, payment_method, description=""):
    """Insert a new expense record."""
    if amount <= 0:
        raise ValueError("Expense amount must be greater than 0.")
    validate_date_format(date_str)

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO expenses (category_id, amount, date, payment_method, description) VALUES (?, ?, ?, ?, ?)",
        (category_id, amount, date_str, payment_method, description.strip())
    )
    conn.commit()
    exp_id = cursor.lastrowid
    conn.close()
    return exp_id


def update_expense(expense_id, category_id, amount, date_str, payment_method, description=""):
    """Update an existing expense record."""
    if amount <= 0:
        raise ValueError("Expense amount must be greater than 0.")
    validate_date_format(date_str)

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE expenses SET category_id = ?, amount = ?, date = ?, payment_method = ?, description = ? WHERE id = ?",
        (category_id, amount, date_str, payment_method, description.strip(), expense_id)
    )
    conn.commit()
    conn.close()


def delete_expense(expense_id):
    """Delete an expense record by ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
    conn.commit()
    conn.close()


def get_expense_by_id(expense_id):
    """Retrieve a single expense record with category details."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT e.*, c.name AS category_name
        FROM expenses e
        JOIN categories c ON e.category_id = c.id
        WHERE e.id = ?
    """, (expense_id,))
    row = cursor.fetchone()
    conn.close()
    return row


def get_all_expenses(limit=None):
    """Retrieve expenses joined with category names ordered by date descending."""
    conn = get_connection()
    cursor = conn.cursor()
    query = """
        SELECT e.id, e.category_id, c.name AS category_name, e.amount, e.date, e.payment_method, e.description, e.created_at
        FROM expenses e
        JOIN categories c ON e.category_id = c.id
        ORDER BY e.date DESC, e.id DESC
    """
    if limit:
        query += f" LIMIT {int(limit)}"
    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()
    return rows


# ==========================================
# INCOME CRUD
# ==========================================

def add_income(category_id, amount, date_str, payment_method, description=""):
    """Insert a new income record."""
    if amount <= 0:
        raise ValueError("Income amount must be greater than 0.")
    validate_date_format(date_str)

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO income (category_id, amount, date, payment_method, description) VALUES (?, ?, ?, ?, ?)",
        (category_id, amount, date_str, payment_method, description.strip())
    )
    conn.commit()
    inc_id = cursor.lastrowid
    conn.close()
    return inc_id


def update_income(income_id, category_id, amount, date_str, payment_method, description=""):
    """Update an existing income record."""
    if amount <= 0:
        raise ValueError("Income amount must be greater than 0.")
    validate_date_format(date_str)

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE income SET category_id = ?, amount = ?, date = ?, payment_method = ?, description = ? WHERE id = ?",
        (category_id, amount, date_str, payment_method, description.strip(), income_id)
    )
    conn.commit()
    conn.close()


def delete_income(income_id):
    """Delete an income record by ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM income WHERE id = ?", (income_id,))
    conn.commit()
    conn.close()


def get_income_by_id(income_id):
    """Retrieve a single income record with category details."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT i.*, c.name AS category_name
        FROM income i
        JOIN categories c ON i.category_id = c.id
        WHERE i.id = ?
    """, (income_id,))
    row = cursor.fetchone()
    conn.close()
    return row


def get_all_income(limit=None):
    """Retrieve income joined with category names ordered by date descending."""
    conn = get_connection()
    cursor = conn.cursor()
    query = """
        SELECT i.id, i.category_id, c.name AS category_name, i.amount, i.date, i.payment_method, i.description, i.created_at
        FROM income i
        JOIN categories c ON i.category_id = c.id
        ORDER BY i.date DESC, i.id DESC
    """
    if limit:
        query += f" LIMIT {int(limit)}"
    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()
    return rows


# ==========================================
# SEARCH, FILTER & REPORTS
# ==========================================

def get_combined_transactions(record_type="All", keyword="", category_id=None,
                              start_date="", end_date="", payment_method="All"):
    """
    Unified query combining Expenses and Income, with flexible filtering:
    - record_type: 'All', 'Expense', or 'Income'
    - keyword: matches in description or category name
    - category_id: specific category ID
    - start_date / end_date: date range (YYYY-MM-DD)
    - payment_method: specific payment method or 'All'
    """
    conn = get_connection()
    cursor = conn.cursor()

    queries = []
    params = []

    # Expense query part
    if record_type in ("All", "Expense"):
        e_query = """
            SELECT 'Expense' AS trans_type, e.id, e.date, c.name AS category_name,
                   e.amount, e.payment_method, e.description, e.category_id
            FROM expenses e
            JOIN categories c ON e.category_id = c.id
            WHERE 1=1
        """
        e_params = []
        if keyword:
            e_query += " AND (e.description LIKE ? OR c.name LIKE ?)"
            e_params.extend([f"%{keyword}%", f"%{keyword}%"])
        if category_id:
            e_query += " AND e.category_id = ?"
            e_params.append(category_id)
        if start_date:
            e_query += " AND e.date >= ?"
            e_params.append(start_date)
        if end_date:
            e_query += " AND e.date <= ?"
            e_params.append(end_date)
        if payment_method and payment_method != "All":
            e_query += " AND e.payment_method = ?"
            e_params.append(payment_method)

        queries.append((e_query, e_params))

    # Income query part
    if record_type in ("All", "Income"):
        i_query = """
            SELECT 'Income' AS trans_type, i.id, i.date, c.name AS category_name,
                   i.amount, i.payment_method, i.description, i.category_id
            FROM income i
            JOIN categories c ON i.category_id = c.id
            WHERE 1=1
        """
        i_params = []
        if keyword:
            i_query += " AND (i.description LIKE ? OR c.name LIKE ?)"
            i_params.extend([f"%{keyword}%", f"%{keyword}%"])
        if category_id:
            i_query += " AND i.category_id = ?"
            i_params.append(category_id)
        if start_date:
            i_query += " AND i.date >= ?"
            i_params.append(start_date)
        if end_date:
            i_query += " AND i.date <= ?"
            i_params.append(end_date)
        if payment_method and payment_method != "All":
            i_query += " AND i.payment_method = ?"
            i_params.append(payment_method)

        queries.append((i_query, i_params))

    if not queries:
        conn.close()
        return []

    if len(queries) == 1:
        full_query = queries[0][0] + " ORDER BY date DESC, id DESC"
        full_params = queries[0][1]
    else:
        full_query = f"SELECT * FROM ({queries[0][0]} UNION ALL {queries[1][0]}) ORDER BY date DESC, id DESC"
        full_params = queries[0][1] + queries[1][1]

    cursor.execute(full_query, full_params)
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_financial_summary(start_date="", end_date="", category_id=None, payment_method="All"):
    """
    Computes total income, total expenses, net balance, and counts for a given filter.
    """
    records = get_combined_transactions(
        record_type="All",
        start_date=start_date,
        end_date=end_date,
        category_id=category_id,
        payment_method=payment_method
    )

    total_income = sum(r["amount"] for r in records if r["trans_type"] == "Income")
    total_expenses = sum(r["amount"] for r in records if r["trans_type"] == "Expense")
    balance = total_income - total_expenses
    income_count = sum(1 for r in records if r["trans_type"] == "Income")
    expense_count = sum(1 for r in records if r["trans_type"] == "Expense")

    return {
        "total_income": total_income,
        "total_expenses": total_expenses,
        "balance": balance,
        "income_count": income_count,
        "expense_count": expense_count,
        "total_count": len(records),
        "records": records
    }


def get_expense_category_breakdown(start_date="", end_date=""):
    """
    Computes aggregated expense amounts by category for reporting and charts.
    """
    conn = get_connection()
    cursor = conn.cursor()
    query = """
        SELECT c.name AS category_name, SUM(e.amount) AS total_amount, COUNT(e.id) AS item_count
        FROM expenses e
        JOIN categories c ON e.category_id = c.id
        WHERE 1=1
    """
    params = []
    if start_date:
        query += " AND e.date >= ?"
        params.append(start_date)
    if end_date:
        query += " AND e.date <= ?"
        params.append(end_date)
    query += " GROUP BY c.id, c.name ORDER BY total_amount DESC"

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return rows


# ==========================================
# CSV EXPORT AND IMPORT
# ==========================================

def export_to_csv(filepath, record_type="All", start_date="", end_date="", category_id=None, payment_method="All"):
    """
    Exports filtered transactions into a formatted CSV file.
    Columns: Type, ID, Date, Category, Amount, Payment Method, Description
    """
    records = get_combined_transactions(
        record_type=record_type,
        start_date=start_date,
        end_date=end_date,
        category_id=category_id,
        payment_method=payment_method
    )

    with open(filepath, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Type", "Date", "Category", "Amount", "Payment Method", "Description"])
        for r in records:
            writer.writerow([
                r["trans_type"],
                r["date"],
                r["category_name"],
                f"{r['amount']:.2f}",
                r["payment_method"],
                r["description"] or ""
            ])

    return len(records)


def import_from_csv(filepath):
    """
    Imports transactions from a CSV file into SQLite.
    Expected headers (case-insensitive):
    - Type ('Expense' or 'Income')
    - Date (YYYY-MM-DD)
    - Category (string)
    - Amount (positive number)
    - Payment Method (string)
    - Description (optional string)

    If a category in the CSV does not exist in the database, it is automatically created!
    Returns (imported_count, skipped_count, error_messages_list).
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")

    imported = 0
    skipped = 0
    errors = []

    conn = get_connection()
    cursor = conn.cursor()

    # Preload existing categories cache: (name.lower(), type.lower()) -> id
    cursor.execute("SELECT id, name, type FROM categories")
    cat_cache = {(row["name"].strip().lower(), row["type"].strip().lower()): row["id"] for row in cursor.fetchall()}

    with open(filepath, mode="r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        # Normalize column header names
        normalized_fieldnames = {col.strip().lower(): col for col in (reader.fieldnames or [])}

        required_cols = ["type", "date", "category", "amount", "payment method"]
        missing_cols = [c for c in required_cols if c not in normalized_fieldnames]
        if missing_cols:
            conn.close()
            raise ValueError(f"CSV missing mandatory columns: {', '.join(missing_cols)}")

        for row_idx, raw_row in enumerate(reader, start=2):
            try:
                row = {k.strip().lower(): v.strip() for k, v in raw_row.items() if k}

                t_type = row.get("type", "").capitalize()
                if t_type not in ("Expense", "Income"):
                    raise ValueError(f"Invalid transaction type '{t_type}'. Must be 'Expense' or 'Income'.")

                date_val = row.get("date", "")
                validate_date_format(date_val)

                cat_name = row.get("category", "")
                if not cat_name:
                    raise ValueError("Category name is required.")

                amt_str = row.get("amount", "").replace(",", "")
                try:
                    amount = float(amt_str)
                    if amount <= 0:
                        raise ValueError()
                except ValueError:
                    raise ValueError(f"Invalid amount '{amt_str}'. Must be a positive number.")

                payment_method = row.get("payment method", "Cash")
                desc = row.get("description", "")

                # Lookup or insert category
                cache_key = (cat_name.lower(), t_type.lower())
                cat_id = cat_cache.get(cache_key)

                if not cat_id:
                    cursor.execute("INSERT OR IGNORE INTO categories (name, type) VALUES (?, ?)", (cat_name, t_type))
                    conn.commit()
                    cursor.execute("SELECT id FROM categories WHERE name = ? AND type = ?", (cat_name, t_type))
                    found = cursor.fetchone()
                    if found:
                        cat_id = found["id"]
                        cat_cache[cache_key] = cat_id
                    else:
                        raise ValueError(f"Could not link or create category '{cat_name}'.")

                # Insert into appropriate table
                if t_type == "Expense":
                    cursor.execute(
                        "INSERT INTO expenses (category_id, amount, date, payment_method, description) VALUES (?, ?, ?, ?, ?)",
                        (cat_id, amount, date_val, payment_method, desc)
                    )
                else:
                    cursor.execute(
                        "INSERT INTO income (category_id, amount, date, payment_method, description) VALUES (?, ?, ?, ?, ?)",
                        (cat_id, amount, date_val, payment_method, desc)
                    )

                imported += 1

            except Exception as e:
                skipped += 1
                errors.append(f"Row {row_idx}: {str(e)}")

    conn.commit()
    conn.close()
    return imported, skipped, errors


# ==========================================
# VALIDATION HELPERS
# ==========================================

def validate_date_format(date_str):
    """Validates that a string is in YYYY-MM-DD format and represents a real calendar date."""
    date_str = str(date_str).strip()
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        raise ValueError(f"Invalid date format: '{date_str}'. Expected YYYY-MM-DD format (e.g., 2026-10-23).")
