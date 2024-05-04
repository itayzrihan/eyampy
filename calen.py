import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import Calendar
import sqlite3


# SQLite database initialization
DB_NAME = "calendar_events.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY,
            date TEXT,
            event_title TEXT,
            event_description TEXT
        )
        """
    )
    conn.commit()
    conn.close()


# Calendar with Events
class CalendarApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Calendar with Events")

        init_db()  # Initialize the database
        
        self.calendar = Calendar(self, selectmode="day", year=2024, month=4, day=1)
        self.calendar.pack(pady=20)

        # Controls for events
        button_frame = tk.Frame(self)
        button_frame.pack(pady=10)

        view_events_button = tk.Button(button_frame, text="View Events", command=self.view_events)
        view_events_button.pack(side=tk.LEFT, padx=5)

        add_event_button = tk.Button(button_frame, text="Add Event", command=self.add_event)
        add_event_button.pack(side=tk.LEFT, padx=5)

        edit_event_button = tk.Button(button_frame, text="Edit Event", command=self.edit_event)
        edit_event_button.pack(side=tk.LEFT, padx=5)

        delete_event_button = tk.Button(button_frame, text="Delete Event", command=self.delete_event)
        delete_event_button.pack(side=tk.LEFT, padx=5)
    
    def view_events(self):
        selected_date = self.calendar.get_date()
        events = self.get_events_for_date(selected_date)

        if not events:
            messagebox.showinfo("No Events", f"No events found for {selected_date}.")
            return

        event_list = "\n".join([f"{e[2]}: {e[3]}" for e in events])
        messagebox.showinfo(f"Events for {selected_date}", event_list)

    def add_event(self):
        selected_date = self.calendar.get_date()
        
        event_window = tk.Toplevel(self)
        event_window.title("Add Event")

        tk.Label(event_window, text="Event Title:").pack(pady=5)
        event_title_entry = tk.Entry(event_window, width=25)
        event_title_entry.pack(pady=5)

        tk.Label(event_window, text="Event Description:").pack(pady=5)
        event_description_entry = tk.Text(event_window, height=5, width=30)
        event_description_entry.pack(pady=5)

        def save_event():
            title = event_title_entry.get().strip()
            description = event_description_entry.get("1.0", "end-1c").strip()
            
            if not title:
                messagebox.showerror("Invalid input", "Event title cannot be empty.")
                return

            self.save_event_to_db(selected_date, title, description)
            messagebox.showinfo("Event Added", "Event added successfully.")
            event_window.destroy()

        save_button = tk.Button(event_window, text="Save Event", command=save_event)
        save_button.pack(pady=10)
    
    def edit_event(self):
        selected_date = self.calendar.get_date()
        events = self.get_events_for_date(selected_date)

        if not events:
            messagebox.showinfo("No Events", f"No events found for {selected_date}.")
            return

        event_list = [f"{e[2]}: {e[3]}" for e in events]
        event_choice = tk.StringVar(value=event_list)

        edit_window = tk.Toplevel(self)
        edit_window.title("Edit Event")

        tk.Label(edit_window, text="Select an event to edit:").pack(pady=5)
        
        event_listbox = tk.Listbox(edit_window, listvariable=event_choice, height=5, selectmode=tk.SINGLE)
        event_listbox.pack(pady=10)

        def edit_selected_event():
            selected_index = event_listbox.curselection()
            if not selected_index:
                messagebox.showerror("No Selection", "Please select an event to edit.")
                return

            selected_event = events[selected_index[0]]
            edit_event_window = tk.Toplevel(edit_window)
            edit_event_window.title("Edit Event")

            tk.Label(edit_event_window, text="Event Title:").pack(pady=5)
            edit_title_entry = tk.Entry(edit_event_window, width=25)
            edit_title_entry.insert(0, selected_event[2])
            edit_title_entry.pack(pady=5)

            tk.Label(edit_event_window, text="Event Description:").pack(pady=5)
            edit_description_entry = tk.Text(edit_event_window, height=5, width=30)
            edit_description_entry.insert("1.0", selected_event[3])
            edit_description_entry.pack(pady=5)

            def save_edited_event():
                new_title = edit_title_entry.get().strip()
                new_description = edit_description_entry.get("1.0", "end-1c").strip()
                
                if not new_title:
                    messagebox.showerror("Invalid input", "Event title cannot be empty.")
                    return

                self.update_event_in_db(selected_event[0], new_title, new_description)
                messagebox.showinfo("Event Updated", "Event updated successfully.")
                edit_event_window.destroy()

            save_button = tk.Button(edit_event_window, text="Save Changes", command=save_edited_event)
            save_button.pack(pady=10)
        
        edit_button = tk.Button(edit_window, text="Edit", command=edit_selected_event)
        edit_button.pack(pady=10)

    def delete_event(self):
        selected_date = self.calendar.get_date()
        events = self.get_events_for_date(selected_date)

        if not events:
            messagebox.showinfo("No Events", f"No events found for {selected_date}.")
            return

        event_list = [f"{e[2]}: {e[3]}" for e in events]
        event_choice = tk.StringVar(value=event_list)

        delete_window = tk.Toplevel(self)
        delete_window.title("Delete Event")

        tk.Label(delete_window, text="Select an event to delete:").pack(pady=5)
        
        event_listbox = tk.Listbox(delete_window, listvariable=event_choice, height=5, selectmode=tk.SINGLE)
        event_listbox.pack(pady=10)

        def delete_selected_event():
            selected_index = event_listbox.curselection()
            if not selected_index:
                messagebox.showerror("No Selection", "Please select an event to delete.")
                return

            selected_event = events[selected_index[0]]

            if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{selected_event[2]}'?"):
                self.delete_event_from_db(selected_event[0])
                messagebox.showinfo("Event Deleted", f"'{selected_event[2]}' has been deleted.")
                delete_window.destroy()

        delete_button = tk.Button(delete_window, text="Delete", command=delete_selected_event)
        delete_button.pack(pady=10)

    def get_events_for_date(self, date):
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute("SELECT * FROM events WHERE date = ?", (date,))
        events = cur.fetchall()
        conn.close()
        return events

    def save_event_to_db(self, date, title, description):
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO events (date, event_title, event_description) VALUES (?, ?, ?)",
            (date, title, description),
        )
        conn.commit()
        conn.close()

    def update_event_in_db(self, event_id, title, description):
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute(
            "UPDATE events SET event_title = ?, event_description = ? WHERE id = ?",
            (title, description, event_id),
        )
        conn.commit()
        conn.close()

    def delete_event_from_db(self, event_id):
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute("DELETE FROM events WHERE id = ?", (event_id,))
        conn.commit()
        conn.close()

if __name__ == "__main__":
    app = CalendarApp()
    app.mainloop()
