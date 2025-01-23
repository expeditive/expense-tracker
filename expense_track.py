import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import matplotlib.pyplot as plt

DB_NAME = "expense_tracker_gui.db"

# Initialize the database (check if table exists, do not drop data)
def initialize_database():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            category TEXT NOT NULL,
            description TEXT,
            amount REAL NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Add an expense
def add_expense(date, category, description, amount):
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO expenses (date, category, description, amount)
            VALUES (?, ?, ?, ?)
        ''', (date, category, description, amount))
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Expense added successfully!")
        update_expense_table()
        update_total_expense_label()
    except Exception as e:
        messagebox.showerror("Error", str(e))

# Fetch expenses from the database
def fetch_expenses():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM expenses", conn)
    conn.close()
    return df

# Fetch the total expenses
def fetch_total_expense():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(amount) FROM expenses")
    result = cursor.fetchone()[0]
    conn.close()
    return result if result else 0

# Update the expense table
def update_expense_table():
    for row in expense_table.get_children():
        expense_table.delete(row)
    df = fetch_expenses()
    for _, row in df.iterrows():
        expense_table.insert("", tk.END, values=row.values)

# Update the total expense label
def update_total_expense_label():
    total_expense = fetch_total_expense()
    total_expense_label.config(text=f"Total Expense: ₹{total_expense:.2f}")

# Visualize expenses with a pie chart
def visualize_expenses():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT category, SUM(amount) as total FROM expenses GROUP BY category", conn)
    conn.close()
    if not df.empty:
        plt.figure(figsize=(8, 6), facecolor="black")
        colors = plt.cm.Paired.colors
        plt.pie(df["total"], labels=df["category"], autopct="%1.1f%%", colors=colors, textprops={"color": "white"})
        plt.title("Expense Distribution by Category", color="white", fontsize=14)
        plt.axis("equal")
        plt.tight_layout()
        plt.show()
    else:
        messagebox.showinfo("No Data", "No expenses to visualize.")

# Create the GUI
def create_gui():
    global expense_table, total_expense_label
    root = tk.Tk()
    root.title("Expense Tracker")
    root.geometry("800x600")
    root.configure(bg="#1b3a2b")  # Dark greenish-black background

    # Style configuration
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("TLabel", background="#1b3a2b", foreground="white", font=("Arial", 10))
    style.configure("TButton", background="#20B2AA", foreground="black", font=("Arial", 12, "bold"), width=20, padding=10)
    style.map("TButton", background=[("active", "#5F9EA0")])  # Hover effect
    style.configure("Treeview", background="gray20", foreground="white", fieldbackground="gray20", font=("Arial", 10))
    style.configure("Treeview.Heading", background="gray30", foreground="white", font=("Arial", 11, "bold"))
    style.map("Treeview.Heading", background=[("active", "#0078D7")])

    # Add the title "EXPENSE TRACKER" in large cool font to the top-right corner
    title_label = tk.Label(root, text="EXPENSE TRACKER", font=("Papyrus", 30, "bold"), fg="white", bg="#1b3a2b")
    title_label.place(relx=1.0, rely=0.05, anchor="ne")  # Position at the top-right corner

    # Input Frame
    input_frame = ttk.Frame(root, padding="10")
    input_frame.pack(fill="x", pady=10)

    ttk.Label(input_frame, text="Date:").grid(row=0, column=0, padx=5, pady=5)
    date_entry = ttk.Entry(input_frame)
    date_entry.grid(row=0, column=1, padx=5, pady=5)

    ttk.Label(input_frame, text="Category:").grid(row=0, column=2, padx=5, pady=5)
    category_entry = ttk.Entry(input_frame)
    category_entry.grid(row=0, column=3, padx=5, pady=5)

    ttk.Label(input_frame, text="Description:").grid(row=1, column=0, padx=5, pady=5)
    description_entry = ttk.Entry(input_frame)
    description_entry.grid(row=1, column=1, padx=5, pady=5)

    ttk.Label(input_frame, text="Amount:").grid(row=1, column=2, padx=5, pady=5)
    amount_entry = ttk.Entry(input_frame)
    amount_entry.grid(row=1, column=3, padx=5, pady=5)

    def on_add():
        date = date_entry.get()
        category = category_entry.get()
        description = description_entry.get()
        try:
            amount = float(amount_entry.get())
        except ValueError:
            messagebox.showerror("Invalid Input", "Amount must be a number.")
            return
        add_expense(date, category, description, amount)
        date_entry.delete(0, tk.END)
        category_entry.delete(0, tk.END)
        description_entry.delete(0, tk.END)
        amount_entry.delete(0, tk.END)

    ttk.Button(input_frame, text="Add Expense", command=on_add).grid(row=2, column=0, columnspan=4, pady=10)

    # Table Frame
    table_frame = ttk.Frame(root, padding="10")
    table_frame.pack(fill="both", expand=True)

    columns = ("ID", "Date", "Category", "Description", "Amount")
    expense_table = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
    for col in columns:
        expense_table.heading(col, text=col)
        expense_table.column(col, anchor="center")
    expense_table.pack(fill="both", expand=True, side="left")

    scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=expense_table.yview)
    expense_table.configure(yscroll=scrollbar.set)
    scrollbar.pack(side="right", fill="y")

    # Total Expense Label
    total_expense_label = ttk.Label(root, text="Total Expense: ₹0.00", font=("Arial", 12, "bold"))
    total_expense_label.pack(pady=10)

    # Button Frame
    button_frame = ttk.Frame(root, padding="10")
    button_frame.pack(fill="x", pady=10)

    # Updated Button size and padding
    visualize_button = ttk.Button(button_frame, text="Visualize Expenses", command=visualize_expenses)
    visualize_button.pack(side="left", padx=5, pady=5)
    
    exit_button = ttk.Button(button_frame, text="Exit", command=root.quit)
    exit_button.pack(side="right", padx=5, pady=5)

    update_expense_table()
    update_total_expense_label()
    root.mainloop()

# Main
if __name__ == "__main__":
    initialize_database()
    create_gui()
