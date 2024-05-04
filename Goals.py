import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import datetime as dt
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkcalendar import DateEntry

# SQLite database initialization
DB_NAME = "goal_tracker.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS goals (
            id INTEGER PRIMARY KEY,
            goal_name TEXT,
            goal_type TEXT,
            start_date TEXT,
            end_date TEXT,
            target INTEGER,
            current_progress INTEGER
        )
        """
    )
    conn.commit()
    conn.close()

# Goal Tracking Application
class GoalTrackerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Goal Tracker")
        
        init_db()  # Initialize the SQLite database
        
        # Goal entry components
        tk.Label(self, text="Goal Name:").grid(row=0, column=0, padx=5, pady=5)
        self.goal_name_entry = tk.Entry(self, width=20)
        self.goal_name_entry.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(self, text="Goal Type:").grid(row=1, column=0, padx=5, pady=5)
        self.goal_type_combo = ttk.Combobox(self, values=["Short-term", "Long-term"], state="readonly")
        self.goal_type_combo.grid(row=1, column=1, padx=5, pady=5)
        
        tk.Label(self, text="Start Date:").grid(row=2, column=0, padx=5, pady=5)
        self.start_date_entry = DateEntry(self, width=12)
        self.start_date_entry.grid(row=2, column=1, padx=5, pady=5)
        
        tk.Label(self, text="End Date:").grid(row=3, column=0, padx=5, pady=5)
        self.end_date_entry = DateEntry(self, width=12)
        self.end_date_entry.grid(row=3, column=1, padx=5, pady=5)
        
        tk.Label(self, text="Target:").grid(row=4, column=0, padx=5, pady=5)
        self.target_entry = tk.Entry(self, width=10)
        self.target_entry.grid(row=4, column=1, padx=5, pady=5)
        
        # Button to add a new goal
        add_goal_button = tk.Button(self, text="Add Goal", command=self.add_goal)
        add_goal_button.grid(row=5, column=0, columnspan=2, padx=5, pady=10)
        
        # Treeview to display goals
        self.goal_tree = ttk.Treeview(
            self,
            columns=("Goal Name", "Goal Type", "Start Date", "End Date", "Target", "Current Progress"),
            show="headings",
            height=8
        )
        self.goal_tree.heading("Goal Name", text="Goal Name")
        self.goal_tree.heading("Goal Type", text="Goal Type")
        self.goal_tree.heading("Start Date", text="Start Date")
        self.goal_tree.heading("End Date", text="End Date")
        self.goal_tree.heading("Target", text="Target")
        self.goal_tree.heading("Current Progress", text="Current Progress")
        
        self.goal_tree.grid(row=6, column=0, columnspan=2, padx=10, pady=10)
        
        # Button to update goal progress
        update_progress_button = tk.Button(self, text="Update Progress", command=self.update_progress)
        update_progress_button.grid(row=7, column=0, padx=10, pady=10)
        
        # Button to view goal progress graphically
        view_progress_button = tk.Button(self, text="View Progress", command=self.view_progress)
        view_progress_button.grid(row=7, column=1, padx=10, pady=10)
        
        self.load_goals()  # Load initial goals into the Treeview
    
    def add_goal(self):
        # Collect input data
        goal_name = self.goal_name_entry.get().strip()
        goal_type = self.goal_type_combo.get()
        start_date = self.start_date_entry.get()
        end_date = self.end_date_entry.get()
        try:
            target = int(self.target_entry.get().strip())
        except ValueError:
            messagebox.showerror("Invalid input", "Please enter a valid target (integer).")
            return
        
        if not goal_name:
            messagebox.showerror("Invalid input", "Goal name cannot be empty.")
            return
        
        # Insert into the SQLite database
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO goals (goal_name, goal_type, start_date, end_date, target, current_progress) VALUES (?, ?, ?, ?, ?, ?)",
            (goal_name, goal_type, start_date, end_date, target, 0),
        )
        conn.commit()
        conn.close()
        
        self.load_goals()  # Reload goals to include the new entry
    
    def load_goals(self):
        # Clear existing items in the Treeview
        self.goal_tree.delete(*self.goal_tree.get_children())
        
        # Fetch data from SQLite database
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute("SELECT goal_name, goal_type, start_date, end_date, target, current_progress FROM goals")
        
        for row in cur.fetchall():
            self.goal_tree.insert("", "end", values=row)
        
        conn.close()
    
    def update_progress(self):
        selected_items = self.goal_tree.selection()
        
        if not selected_items:
            messagebox.showerror("No selection", "Please select a goal to update progress.")
            return
        
        update_window = tk.Toplevel(self)
        update_window.title("Update Progress")
        
        tk.Label(update_window, text="New Progress:").pack(pady=5)
        new_progress_entry = tk.Entry(update_window, width=10)
        new_progress_entry.pack(pady=5)
        
        def save_progress():
            try:
                new_progress = int(new_progress_entry.get().strip())
            except ValueError:
                messagebox.showerror("Invalid input", "Please enter a valid progress (integer).")
                return
            
            if new_progress < 0:
                messagebox.showerror("Invalid input", "Progress cannot be negative.")
                return
            
            goal_name = self.goal_tree.item(selected_items[0], "values")[0]
            
            # Update the goal progress in SQLite
            conn = sqlite3.connect(DB_NAME)
            cur = conn.cursor()
            cur.execute(
                "UPDATE goals SET current_progress = ? WHERE goal_name = ?",
                (new_progress, goal_name),
            )
            conn.commit()
            conn.close()
            
            self.load_goals()  # Reload goals to reflect the new progress
            update_window.destroy()
        
        save_button = tk.Button(update_window, text="Save", command=save_progress)
        save_button.pack(pady=10)
    
    def view_progress(self):
        # Fetch data from SQLite database
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        
        cur.execute("SELECT goal_name, current_progress, target FROM goals")
        goal_data = cur.fetchall()
        
        conn.close()
        
        # Plot the progress using Matplotlib
        fig, ax = plt.subplots()
        goal_names = [data[0] for data in goal_data]
        current_progress = [data[1] for data in goal_data]
        targets = [data[2] for data in goal_data]
        
        ax.bar(goal_names, current_progress, label="Current Progress")
        ax.bar(goal_names, targets, alpha=0.5, label="Target")
        
        ax.set_title("Goal Progress")
        ax.set_xlabel("Goals")
        ax.set_ylabel("Progress")
        ax.legend()
        
        # Display the plot in the GUI
        progress_window = tk.Toplevel(self)
        progress_window.title("Goal Progress")
        
        canvas = FigureCanvasTkAgg(fig, master=progress_window)
        canvas.get_tk_widget().pack(pady=10, padx=10)
        
        canvas.draw()  # Render the plot

if __name__ == "__main__":
    app = GoalTrackerApp()
    app.mainloop()
