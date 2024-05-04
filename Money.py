import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkcalendar import DateEntry
import sqlite3
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import datetime as dt


# Database setup
DB_NAME = "expense_tracker.db"

# Initialize the SQLite database and create tables if they don't exist
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY,
            date TEXT,
            category TEXT,
            description TEXT,
            amount REAL
        )
        """
    )
    conn.commit()
    conn.close()

# Expense Tracker GUI
class ExpenseTracker(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Expense Tracker")
        
        # Initialize the database
        init_db()
        
        # GUI Components
        self.date_entry = DateEntry(self, width=12)
        self.date_entry.grid(row=0, column=1, padx=10, pady=10)
        
        self.category_entry = tk.Entry(self, width=20)
        self.category_entry.grid(row=0, column=2, padx=10, pady=10)
        
        self.description_entry = tk.Entry(self, width=30)
        self.description_entry.grid(row=0, column=3, padx=10, pady=10)
        
        self.amount_entry = tk.Entry(self, width=10)
        self.amount_entry.grid(row=0, column=4, padx=10, pady=10)
        
        add_button = tk.Button(self, text="Add Expense", command=self.add_expense)
        add_button.grid(row=0, column=5, padx=10, pady=10)
        
        self.expense_tree = ttk.Treeview(
            self,
            columns=("Date", "Category", "Description", "Amount"),
            show="headings",
            height=10
        )
        
        self.expense_tree.heading("Date", text="Date")
        self.expense_tree.heading("Category", text="Category")
        self.expense_tree.heading("Description", text="Description")
        self.expense_tree.heading("Amount", text="Amount")
        
        self.expense_tree.column("Date", width=100)
        self.expense_tree.column("Category", width=150)
        self.expense_tree.column("Description", width=200)
        self.expense_tree.column("Amount", width=100)
        
        self.expense_tree.grid(row=1, column=0, columnspan=6, padx=10, pady=10)
        
        # Button to delete selected expense
        delete_button = tk.Button(self, text="Delete Expense", command=self.delete_expense)
        delete_button.grid(row=2, column=0, padx=10, pady=10)
        
        # Button to summarize expenses
        summary_button = tk.Button(self, text="Show Summary", command=self.show_summary)
        summary_button.grid(row=2, column=1, padx=10, pady=10)
        
        self.load_expenses()  # Load initial expenses into the Treeview
        
    def add_expense(self):
        # Get input data
        date = self.date_entry.get()
        category = self.category_entry.get().strip()
        description = self.description_entry.get().strip()
        try:
            amount = float(self.amount_entry.get().strip())
        except ValueError:
            messagebox.showerror("Invalid input", "Please enter a valid amount.")
            return
        
        if not category:
            messagebox.showerror("Invalid input", "Category cannot be empty.")
            return
        
        if amount <= 0:
            messagebox.showerror("Invalid input", "Amount must be positive.")
            return
        
        # Add to SQLite database
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO expenses (date, category, description, amount) VALUES (?, ?, ?, ?)",
            (date, category, description, amount),
        )
        conn.commit()
        conn.close()
        
        # Clear input fields
        self.date_entry.set_date(dt.date.today())  # Reset to today's date
        self.category_entry.delete(0, tk.END)
        self.description_entry.delete(0, tk.END)
        self.amount_entry.delete(0, tk.END)
        
        self.load_expenses()  # Reload expenses to include the new entry
    
    def load_expenses(self):
        # Clear existing items in the Treeview
        self.expense_tree.delete(*self.expense_tree.get_children())
        
        # Fetch data from SQLite database
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute("SELECT id, date, category, description, amount FROM expenses")
        
        for row in cur.fetchall():
            self.expense_tree.insert("", "end", values=row[1:])
        
        conn.close()
    
    def delete_expense(self):
        selected_items = self.expense_tree.selection()
        
        if not selected_items:
            messagebox.showerror("No selection", "Please select an expense to delete.")
            return
        
        # Get the expense ID from the selected item
        expense_id = self.expense_tree.item(selected_items[0], "values")[0]
        
        # Delete the expense from SQLite
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
        conn.commit()
        conn.close()
        
        self.load_expenses()  # Reload expenses to reflect deletion
    
    def show_summary(self):
        # Calculate total expenses by category
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        
        cur.execute("SELECT category, SUM(amount) FROM expenses GROUP BY category")
        summary_data = cur.fetchall()
        
        conn.close()
        
        # Plot the summary using Matplotlib
        fig, ax = plt.subplots()
        categories = [data[0] for data in summary_data]
        amounts = [data[1] for data in summary_data]
        
        ax.bar(categories, amounts)
        ax.set_title("Expenses by Category")
        ax.set_xlabel("Category")
        ax.set_ylabel("Total Expense")
        
        # Display the plot in the GUI
        summary_window = tk.Toplevel(self)
        summary_window.title("Expense Summary")
        
        canvas = FigureCanvasTkAgg(fig, master=summary_window)
        canvas.get_tk_widget().pack(pady=10, padx=10)
        
        canvas.draw()  # Render the plot

if __name__ == "__main__":
    app = ExpenseTracker()
    app.mainloop()
