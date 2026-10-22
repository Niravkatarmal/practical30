# 💰 Personal Expense Manager

A clean, modern, and robust desktop application developed with **Python Tkinter** and **SQLite3**, designed specifically for **College Practicals, Viva Submissions, and Academic Projects**.

![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=flat&logo=python&logoColor=white)
![Tkinter](https://img.shields.io/badge/GUI-Tkinter-brightgreen?style=flat)
![SQLite](https://img.shields.io/badge/Database-SQLite3-003B57?style=flat&logo=sqlite&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-blue.svg)

---

## 📋 Table of Contents
1. [Key Features](#-key-features)
2. [Database Schema (3 Relational Tables)](#-database-schema-3-relational-tables)
3. [Project Structure](#-project-structure)
4. [Prerequisites & Installation](#-prerequisites--installation)
5. [Running the Application](#-running-the-application)
6. [Application Screens & Operations](#-application-screens--operations)
7. [CSV Export & Import Guide](#-csv-export--import-guide)
8. [Building Windows Executable (.exe)](#-building-windows-executable-exe)
9. [Pushing Source Code to GitHub](#-pushing-source-code-to-github)
10. [College Practical / Viva Questions & Answers](#-college-practical--viva-questions--answers)

---

## 🌟 Key Features

- **Executive Financial Dashboard**:
  - Top KPI cards displaying **Total Income**, **Total Expenses**, and **Net Balance** (live computed).
  - Recent transactions list with color-coded badges (Green for Income, Red for Expense).
  - Top 5 spending categories breakdown with visual progress bars.
- **Complete CRUD Operations**:
  - **Create**: Add new expenses and income with instant validation.
  - **Read**: View records in an interactive, zebra-striped `Treeview` table with column sorting.
  - **Update**: Edit existing transactions or categories through pre-populated modal dialogs.
  - **Delete**: Remove transactions with safety confirmation dialogs (`askyesno`).
- **Relational SQLite Database (3 Tables)**:
  - `categories`, `expenses`, and `income` tables.
  - Foreign key constraints enabled (`PRAGMA foreign_keys = ON;`) ensuring relational integrity.
  - Automatic pre-seeding of realistic sample data on first launch.
- **Category Management**:
  - Add, edit, and delete categories.
  - Foreign key deletion guard: Prevents deleting categories that are currently referenced by transactions.
- **Search & Multi-Filter**:
  - Filter transactions by keyword (description or category), transaction type (`Expense`, `Income`, `All`), payment method (`Cash`, `UPI / Online`, `Debit Card`, `Credit Card`, `Bank Transfer`), and custom date ranges (`From Date` to `To Date`).
- **Reports & Analytics**:
  - Filter by timeframe (`All Time`, `Current Month`, `Last 30 Days`, `Current Year`).
  - Category-wise spending table showing item counts, total amount, and percentage share.
  - Dynamic visual pie chart using `matplotlib` (with automatic fallback to Tkinter Canvas horizontal bars).
- **CSV Data Backup & Restore**:
  - Export records directly into a `.csv` file.
  - Import external or exported `.csv` files back into the SQLite database with category auto-creation and error reporting.
- **Simple, Zero-Configuration Setup**:
  - Runs on standard Python library (`tkinter`, `sqlite3`, `csv`). No mandatory external dependencies!

---

## 🗄️ Database Schema (3 Relational Tables)

The application implements a relational database design with 3 related SQLite tables:

```
+--------------------+               +--------------------------------------+
|    categories      |               |              expenses                |
+--------------------+               +--------------------------------------+
| id (PK, AutoInc)   |<-----+        | id (PK, AutoInc)                     |
| name (TEXT, Unique)|      |        | category_id (FK -> categories.id)    |
| type (TEXT)        |      +--------| amount (REAL, > 0)                   |
+--------------------+      |        | date (TEXT, YYYY-MM-DD)              |
                            |        | payment_method (TEXT)                |
                            |        | description (TEXT)                   |
                            |        | created_at (TIMESTAMP)               |
                            |        +--------------------------------------+
                            |
                            |        +--------------------------------------+
                            |        |               income                 |
                            |        +--------------------------------------+
                            |        | id (PK, AutoInc)                     |
                            +--------| category_id (FK -> categories.id)    |
                                     | amount (REAL, > 0)                   |
                                     | date (TEXT, YYYY-MM-DD)              |
                                     | payment_method (TEXT)                |
                                     | description (TEXT)                   |
                                     | created_at (TIMESTAMP)               |
                                     +--------------------------------------+
```

### Table Definitions

1. **`categories` Table**:
   - `id`: `INTEGER PRIMARY KEY AUTOINCREMENT`
   - `name`: `TEXT UNIQUE NOT NULL`
   - `type`: `TEXT NOT NULL CHECK(type IN ('Expense', 'Income'))`

2. **`expenses` Table**:
   - `id`: `INTEGER PRIMARY KEY AUTOINCREMENT`
   - `category_id`: `INTEGER NOT NULL REFERENCES categories(id) ON DELETE RESTRICT`
   - `amount`: `REAL NOT NULL CHECK(amount > 0)`
   - `date`: `TEXT NOT NULL` (Format: `YYYY-MM-DD`)
   - `payment_method`: `TEXT NOT NULL`
   - `description`: `TEXT`
   - `created_at`: `TIMESTAMP DEFAULT CURRENT_TIMESTAMP`

3. **`income` Table**:
   - `id`: `INTEGER PRIMARY KEY AUTOINCREMENT`
   - `category_id`: `INTEGER NOT NULL REFERENCES categories(id) ON DELETE RESTRICT`
   - `amount`: `REAL NOT NULL CHECK(amount > 0)`
   - `date`: `TEXT NOT NULL` (Format: `YYYY-MM-DD`)
   - `payment_method`: `TEXT NOT NULL`
   - `description`: `TEXT`
   - `created_at`: `TIMESTAMP DEFAULT CURRENT_TIMESTAMP`

---

## 📁 Project Structure

```
pr30/
├── app.py                      # Application launcher / alternate entry point
├── main.py                     # Main Tkinter GUI application (Dashboard, Menubar, Views)
├── database.py                 # SQLite database layer, schema, CRUD, CSV import/export
├── sample_expenses_import.csv  # Ready-to-use sample CSV file for viva/practical testing
├── build_exe.bat               # One-click Windows batch script to compile .exe via PyInstaller
├── run_app.bat                 # One-click launcher to run the Python application
├── requirements.txt            # Optional dependencies (matplotlib, pyinstaller)
├── .gitignore                  # Git ignore rules for Python, DB, and builds
└── README.md                   # Complete documentation and viva guide
```

---

## ⚙️ Prerequisites & Installation

### 1. Requirements
- **Python 3.8 or newer** (tested on Python 3.11).
- `tkinter` and `sqlite3` are bundled with standard Python on Windows.

### 2. Optional Dependencies (For Visual Charts & Executable)
To enable the graphical Matplotlib pie chart in the Reports view:
```bash
pip install -r requirements.txt
```
*(If matplotlib is not installed, the application automatically uses its built-in Tkinter Canvas chart.)*

---

## 🚀 Running the Application

### Option A: From Terminal
```bash
python main.py
```
*or:*
```bash
python app.py
```

### Option B: One-Click Launcher (Windows)
Double-click `run_app.bat` in the project folder.

---

## 🖥️ Application Screens & Operations

### 1. 📊 Dashboard
- Overview of current finances: Total Income, Total Expenses, and Net Balance.
- Quick buttons to add expenses/incomes.
- List of recent transactions with double-click view.
- Top expense categories with percentage contribution.

### 2. 💸 Add Expense
- Form fields: **Amount (₹)**, **Category** (dropdown + "+ New Category" button), **Date** (pre-filled with today's date + "Today" button), **Payment Method**, and **Description**.
- Comprehensive validation: Positive number check, valid calendar date format (`YYYY-MM-DD`), and non-empty category.

### 3. 💵 Add Income
- Form fields: **Amount (₹)**, **Source / Category**, **Date**, **Payment Method**, and **Description**.
- Records incoming funds into the `income` table.

### 4. 📋 View Records (Full CRUD)
- Tabbed filters: `All`, `Expense`, or `Income`.
- Real-time search by keyword.
- **Edit Selected**: Opens pre-populated modal dialog to update amount, category, date, payment method, or note.
- **Delete Selected**: Shows warning confirmation dialog (`messagebox.askyesno`).
- Column header click: Sorts rows ascending or descending.

### 5. 🏷️ Category Management
- View all categories with their type (`Expense` / `Income`) and the number of linked transactions.
- Add new categories.
- Edit category name/type.
- Delete category: SQLite foreign key constraint prevents deleting any category currently in use.

### 6. 🔍 Search & Multi-Filter
- Filter transactions simultaneously by:
  - Text keyword in description or category name
  - Transaction type (`All`, `Expense`, `Income`)
  - Payment method (`Cash`, `UPI / Online`, `Debit Card`, `Credit Card`, `Bank Transfer`, `Other`)
  - Date range (`From Date` and `To Date`)
- Live summary: Displays count, filtered income, filtered expense, and net total.

### 7. 📈 Reports & Analytics
- Select timeframe (`All Time`, `Current Month`, `Last 30 Days`, `Current Year`).
- Displays category-wise breakdown table with percentage share.
- Visual pie chart (via Matplotlib) or horizontal bar distribution (via Canvas).
- "Export CSV" button to save report summaries.

### 8. 💾 Import / Export
- **Export Data**: Choose scope (`All`, `Expenses Only`, `Income Only`) and save to `.csv`.
- **Import Data**: Select a CSV file to restore or add records into SQLite. Automatically creates missing categories!
- **Test Sample CSV**: One-click test button using `sample_expenses_import.csv`.

---

## 📥 CSV Export & Import Guide

### CSV Format Specification
When exporting or importing, the CSV uses the following columns:

| Column Header | Format / Example | Notes |
| :--- | :--- | :--- |
| **Type** | `Expense` or `Income` | Mandatory |
| **Date** | `2026-10-23` (YYYY-MM-DD) | Mandatory, validated |
| **Category** | `College & Books` | Mandatory, auto-created if missing |
| **Amount** | `1250.00` | Mandatory, positive float |
| **Payment Method** | `UPI / Online` | Mandatory |
| **Description** | `Reference textbook` | Optional |

A sample file `sample_expenses_import.csv` is provided in the repository for viva testing.

---

## 🔨 Building Windows Executable (.exe)

You can compile the entire application into a standalone Windows `.exe` file that runs on any Windows PC without needing Python installed.

### Option A: Using the Automated Script
Double-click `build_exe.bat`. It will install PyInstaller (if not present) and compile `app.py`.

### Option B: Using Command Line
```bash
# 1. Install PyInstaller
pip install pyinstaller

# 2. Compile standalone windowed executable
python -m PyInstaller --onefile --windowed --name "ExpenseManager" --clean app.py
```

### Result:
The compiled executable will be located in:
```
dist/ExpenseManager.exe
```

---

## 🌐 Pushing Source Code to GitHub

Follow these steps in your PowerShell or Command Prompt inside the `pr30` directory:

### Step 1: Initialize Git Repository
```bash
git init
```

### Step 2: Add Files & Make Initial Commit
```bash
git add .
git commit -m "Initial commit: Personal Expense Manager desktop application"
```

### Step 3: Rename Default Branch to `main`
```bash
git branch -M main
```

### Step 4: Link to Your GitHub Repository
1. Go to [GitHub](https://github.com/new) and create a new repository (e.g., `personal-expense-manager`).
2. Copy the repository URL (e.g., `https://github.com/<your-username>/personal-expense-manager.git`).
3. Link your local repo:
```bash
git remote add origin https://github.com/<your-username>/personal-expense-manager.git
```

### Step 5: Push to GitHub
```bash
git push -u origin main
```

---

## 🎓 College Practical / Viva Questions & Answers

Here are the most common questions examiners ask during practical examinations and viva voce:

### Q1: Why did you use SQLite instead of MySQL or PostgreSQL for this desktop app?
> **Answer**: SQLite is a serverless, self-contained, zero-configuration embedded database engine. It stores the entire database in a single disk file (`expense_manager.db`), which eliminates the need to install and manage a database server. This makes it ideal for standalone desktop applications.

### Q2: How are relationships and Foreign Keys enforced in SQLite?
> **Answer**: By default, SQLite has foreign key support disabled for backwards compatibility. In `database.py`, we explicitly enable it for every connection using `PRAGMA foreign_keys = ON;`. The `expenses` and `income` tables have a `category_id` column defined as `FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE RESTRICT`. If someone tries to delete a category that has linked expense records, SQLite raises an integrity error to protect data consistency.

### Q3: What is the purpose of the 3 separate tables?
> **Answer**: 
> 1. `categories`: Normalized table holding category names and types (`Expense` or `Income`) to prevent data redundancy and spelling inconsistencies.
> 2. `expenses`: Records outgoing expenditures with amount, date, payment method, and description linked to a category ID.
> 3. `income`: Records incoming funds (allowances, salary, scholarships) linked to a category ID. This separation ensures clean normalization and clear accounting calculations.

### Q4: How is input validation handled?
> **Answer**: 
> 1. **Amount**: Validated to ensure it is numeric and strictly greater than zero (`amount > 0`).
> 2. **Date**: Validated using `datetime.strptime(date_str, "%Y-%m-%d")` to ensure valid calendar dates in standard ISO format.
> 3. **Category**: Ensured that a category is selected and exists in the database.
> 4. **User Feedback**: Descriptive error dialogs (`messagebox.showerror`) inform the user of exact mistakes.

### Q5: How does the CSV Import feature work?
> **Answer**: The `import_from_csv()` function in `database.py` reads the CSV with `csv.DictReader`, checks that all mandatory columns exist, validates each row's amount and date format, checks if the category already exists (and creates it if it's new), and executes parameter-bound `INSERT` queries in a single database transaction.

### Q6: How does PyInstaller package the application into an executable?
> **Answer**: PyInstaller analyzes `app.py` and its imported modules (`main.py`, `database.py`, `tkinter`, `sqlite3`), bundles the Python interpreter, standard libraries, and compiled C-extensions into a single executable using the `--onefile` flag, and uses `--windowed` to suppress the command prompt console window.

---

## 📄 License
This project is open-source and created for educational and academic practical purposes.
