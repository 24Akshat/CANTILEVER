import tkinter as tk
from tkinter import ttk
from tkinter.simpledialog import Dialog
import sqlite3
import json
import os
from datetime import datetime
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

# Expense categories
CATEGORIES = ["Food", "Transportation", "Utilities", "Entertainment", "Others"]

# SQLite setup
DB_FILE = "expenses.db"
FILE_BACKUP = "expenses_backup.json"

conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        amount REAL,
        category TEXT,
        date TEXT
    )
""")
conn.commit()

# File backup functions
def save_to_file():
    cursor.execute("SELECT * FROM expenses")
    rows = cursor.fetchall()
    with open(FILE_BACKUP, 'w') as f:
        json.dump(rows, f)

def load_from_file():
    if os.path.exists(FILE_BACKUP):
        with open(FILE_BACKUP, 'r') as f:
            rows = json.load(f)
            for row in rows:
                cursor.execute("INSERT OR IGNORE INTO expenses VALUES (?, ?, ?, ?, ?)", row)
            conn.commit()

# Add expense dialog
class AddExpenseDialog(Dialog):
    def body(self, master):
        self.title("Add New Expense")

        tk.Label(master, text="Name:").grid(row=0, column=0)
        self.name_entry = tk.Entry(master)
        self.name_entry.grid(row=0, column=1)

        tk.Label(master, text="Amount:").grid(row=1, column=0)
        self.amount_entry = tk.Entry(master)
        self.amount_entry.grid(row=1, column=1)

        tk.Label(master, text="Category:").grid(row=2, column=0)
        self.category_var = tk.StringVar()
        self.category_dropdown = ttk.Combobox(master, textvariable=self.category_var, values=CATEGORIES)
        self.category_dropdown.grid(row=2, column=1)
        self.category_dropdown.current(0)

        return self.name_entry

    def apply(self):
        self.result = {
            "name": self.name_entry.get(),
            "amount": float(self.amount_entry.get()),
            "category": self.category_var.get(),
            "date": datetime.now().strftime('%Y-%m-%d')
        }

# Main app
class ExpenseTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Expense Tracker")

        self.create_widgets()
        self.refresh_dashboard()

    def create_widgets(self):
        # Top frame with button
        self.top_frame = tk.Frame(self.root)
        self.top_frame.pack(side=tk.TOP, fill=tk.X)

        self.add_button = tk.Button(self.top_frame, text="Add New Expense", command=self.add_expense)
        self.add_button.pack(side=tk.RIGHT, padx=10, pady=10)

        # Frame for pie chart
        self.chart_frame = tk.Frame(self.root, height=250)
        self.chart_frame.pack(side=tk.TOP, fill=tk.X, pady=5)
        self.chart_frame.pack_propagate(False)  # prevent resizing

        # Frame for stats and expense list
        self.bottom_frame = tk.Frame(self.root)
        self.bottom_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.stats_label = tk.Label(self.bottom_frame, text="", font=("Arial", 12))
        self.stats_label.pack(pady=5)

        self.expense_list = ttk.Treeview(
            self.bottom_frame,
            columns=("Name", "Amount", "Category", "Date"),
            show="headings"
        )
        for col in ("Name", "Amount", "Category", "Date"):
            self.expense_list.heading(col, text=col)
        self.expense_list.pack(fill=tk.BOTH, expand=True)

    def refresh_dashboard(self):
        # Clear the list
        for i in self.expense_list.get_children():
            self.expense_list.delete(i)

        cursor.execute("SELECT name, amount, category, date FROM expenses")
        rows = cursor.fetchall()

        totals = {cat: 0 for cat in CATEGORIES}
        total_expense = 0

        for row in rows:
            self.expense_list.insert("", tk.END, values=row)
            totals[row[2]] += row[1]
            total_expense += row[1]

        self.stats_label.config(
            text=f"Total Expenses: ₹{total_expense:.2f} | "
                 + ", ".join([f"{cat}: ₹{totals[cat]:.2f}" for cat in CATEGORIES])
        )

        self.draw_pie_chart(totals)

    def draw_pie_chart(self, data):
        for widget in self.chart_frame.winfo_children():
            widget.destroy()

        fig, ax = plt.subplots(figsize=(3, 3))  # smaller figure
        categories = [cat for cat, amt in data.items() if amt > 0]
        amounts = [amt for amt in data.values() if amt > 0]

        if amounts:
            ax.pie(amounts, labels=categories, autopct='%1.1f%%')
        else:
            ax.text(0.5, 0.5, "No expenses to show.", ha='center')

        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP)  # no fill, no expand

    def add_expense(self):
        dialog = AddExpenseDialog(self.root)
        if dialog.result:
            cursor.execute(
                "INSERT INTO expenses (name, amount, category, date) VALUES (?, ?, ?, ?)",
                (
                    dialog.result["name"],
                    dialog.result["amount"],
                    dialog.result["category"],
                    dialog.result["date"],
                ),
            )
            conn.commit()
            save_to_file()
            self.refresh_dashboard()

if __name__ == "__main__":
    load_from_file()
    root = tk.Tk()
    app = ExpenseTrackerApp(root)
    root.mainloop()
    conn.close()
