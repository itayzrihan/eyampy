import flet as ft
import sqlite3
import datetime as dt
import matplotlib.pyplot as plt
from io import BytesIO
import base64

# Database setup
DB_NAME = "expense_tracker.db"

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

def convert_plot_to_base64(fig):
    buffer = BytesIO()
    fig.savefig(buffer, format="png")
    buffer.seek(0)
    img_bytes = buffer.read()
    base64_bytes = base64.b64encode(img_bytes)
    base64_str = base64_bytes.decod
    return base64_str

class ExpenseTrackerApp(ft.UserControl):  # Updated to use Control
    def __init__(self):
        super().__init__()
        init_db()

        self.date_field = ft.DatePicker(value=dt.date.today())
        self.category_field = ft.TextField(label="Category")
        self.description_field = ft.TextField(label="Description")
        self.amount_field = ft.TextField(label="Amount")

        self.expense_list = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Date")),
                ft.DataColumn(ft.Text("Category")),
                ft.DataColumn(ft.Text("Description")),
                ft.DataColumn(ft.Text("Amount")),
            ],
        )

        self.add_button = ft.ElevatedButton("Add Expense", on_click=self.add_expense)
        self.delete_button = ft.ElevatedButton("Delete Expense", on_click=self.delete_expense)
        self.summary_button = ft.ElevatedButton("Show Summary", on_click=self.show_summary)

        self.load_expenses()

    def build(self):
        return ft.Container(
            ft.Column(
                [
                    ft.Row(
                        [
                            ft.Text("Date"),
                            self.date_field,
                            self.category_field,
                            self.description_field,
                            self.amount_field,
                            self.add_button,
                        ],
                        alignment="spaceBetween",
                    ),
                    self.expense_list,
                    ft.Row([self.delete_button, self.summary_button]),
                ]
            )
        )

    def add_expense(self, e):
        date = str(self.date_field.value)
        category = self.category_field.value.strip()
        description = self.description_field.value.strip()
        try:
            amount = float(self.amount_field.value.strip())
        except ValueError:
            ft.AlertDialog(
                content=ft.Text("Invalid input: Please enter a valid amount."),
                open=True,
            )
            return

        if not category:
            ft.AlertDialog(
                content=ft.Text("Invalid input: Category cannot be empty."),
                open=True,
            )
            return

        if amount <= 0:
            ft.AlertDialog(
                content=ft.Text("Invalid input: Amount must be positive."),
                open=True,
            )
            return

        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO expenses (date, category, description, amount) VALUES (?, ?, ?, ?)",
            (date, category, description, amount),
        )
        conn.commit()
        conn.close()

        self.date_field.value = dt.date.today()  # Reset to today's date
        self.category_field.value = ""
        self.description_field.value = ""
        self.amount_field.value = ""
        
        self.load_expenses()

    def load_expenses(self):
        self.expense_list.rows = []
        
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute("SELECT date, category, description, amount FROM expenses")
        
        for row in cur.fetchall():
            self.expense_list.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(row[0])),
                        ft.DataCell(ft.Text(row[1])),
                        ft.DataCell(ft.Text(row[2])),
                        ft.DataCell(ft.Text(str(row[3]))),
                    ],
                )
            )
        
        conn.close()
    
    def delete_expense(self, e):
        if self.expense_list.selected_index is not None:
            conn = sqlite3.connect(DB_NAME)
            cur = conn.cursor()
            selected_row = self.expense_list.rows[self.expense_list.selected_index]
            expense_id = selected_row.cells[0].value
            cur.execute("DELETE FROM expenses WHERE date = ?", (expense_id,))
            conn.commit()
            conn.close()
            
            self.load_expenses()

    def show_summary(self, e):
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute("SELECT category, SUM(amount) FROM expenses GROUP BY category")
        
        categories = []
        amounts = []
        
        for data in cur.fetchall():
            categories.append(data[0])
            amounts.append(data[1])
        
        conn.close()
        
        fig, ax = plt.subplots()
        ax.bar(categories, amounts)
        ax.set_title("Expenses by Category")
        ax.set_xlabel("Category")
        ax.set_ylabel("Total Expense")
        
        base64_str = convert_plot_to_base64(fig)
        
        self.page.dialog(
            ft.AlertDialog(
                content=ft.Image(
                    src_base64=base64_str,
                    width=500,
                    height=400,
                ),
                open=True,
            )
        )

def main(page: ft.Page):
    page.title = "Expense Tracker"
    expense_app = ExpenseTrackerApp()
    page.add(expense_app)

ft.app(target=main)
