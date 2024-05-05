import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkcalendar import DateEntry
import time
import threading
import datetime as dt
import sqlite3
import customtkinter as ctk
from tkinter import ttk, Text  # Import Text for multi-line text box
from tkhtmlview import HTMLScrolledText  # Supports HTML-like formatting
import ast  # For literal evaluation of custom properties
import json  # For serializing custom properties
# Database setup
DB_NAME = "routine_manager_v3.db"  # New database name to avoid conflicts with older DB

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    
    # Optionally drop existing tables if a fresh setup is okay
    cur.execute("DROP TABLE IF EXISTS routines")
    cur.execute("DROP TABLE IF EXISTS logs")
    cur.execute("DROP TABLE IF EXISTS properties")
    
    # Recreate tables
    cur.execute("""
        CREATE TABLE routines (
            id INTEGER PRIMARY KEY,
            order_num INTEGER,
            name TEXT UNIQUE,
            duration INTEGER,
            path TEXT,
            created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            due_date DATETIME DEFAULT NULL,
            short_description TEXT DEFAULT NULL,
            description TEXT DEFAULT NULL,
            human_name TEXT DEFAULT NULL,
            verified INTEGER DEFAULT 0,
            importance TEXT DEFAULT 'not',
            status TEXT DEFAULT 'not stated',
            price REAL DEFAULT 0,
            repeat TEXT DEFAULT 'none',
            days TEXT DEFAULT '0,0,0,0,0,0,0',
            contact TEXT DEFAULT '',
            email TEXT DEFAULT '',
            link TEXT DEFAULT 'https://',
            other_properties TEXT DEFAULT ''
        )
    """)
    
    cur.execute("""
        CREATE TABLE logs (
            id INTEGER PRIMARY KEY,
            routine_name TEXT,
            start_time TEXT,
            end_time TEXT,
            status TEXT
        )
    """)
    
    cur.execute("""
        CREATE TABLE properties (
            property_id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT,
            name TEXT,
            path TEXT
        )
    """)

    conn.commit()
    conn.close()

    
    
# Define a function to apply text styles
def apply_text_style(rich_text, style):
    """Apply a given text style to the selected text in the rich text box."""
    try:
        tags = rich_text.tag_names("sel.first")
        if style in tags:
            rich_text.tag_remove(style, "sel.first", "sel.last")
        else:
            rich_text.tag_add(style, "sel.first", "sel.last")
    except tk.TclError:
        pass

# Define a function to change text alignment
def set_text_alignment(rich_text, align):
    """Set the text alignment for the selected lines."""
    try:
        rich_text.tag_configure(align, justify=align)
        rich_text.tag_add(align, "sel.first linestart", "sel.last lineend+1c")
    except tk.TclError:
        pass

# Define a function for Right-to-Left (RTL) support
def set_right_to_left(rich_text):
    """Toggle Right-to-Left text direction for the rich text box."""
    rtl_state = rich_text.tk.call(rich_text._w, "cget", "-dir")
    new_state = "rtl" if rtl_state == "ltr" else "ltr"
    rich_text.tk.call(rich_text._w, "configure", "-dir", new_state)



class RoutineDetailWindow(ctk.CTkToplevel):
    def __init__(self, parent, routine_name):
        super().__init__(parent)
        
        self.title(f"Routine Details: {routine_name}")

        self.routine_name = routine_name
        self.custom_property_widgets = {}  # Add this line to initialize the dictionary

        
        # Fetch routine data early to ensure fields have data
        self.routine_data = self.fetch_routine_data(routine_name)
        if not self.routine_data:
            messagebox.showerror("Error", f"No data found for routine '{routine_name}'")
            self.destroy()
            return
        
        # Frame for detail entry fields
        detail_frame = ctk.CTkFrame(self)
        detail_frame.grid(row=0, column=0, padx=10, pady=10)

        # Define fields and initialize with placeholder data
        self.fields = {
            "Order Number": ctk.CTkLabel(detail_frame, text=f"Order Number: {self.routine_data[1]}"),
            "Routine Name": ctk.CTkEntry(detail_frame, width=150),
            "Duration (sec)": ctk.CTkEntry(detail_frame, width=150),
            "Path": ctk.CTkEntry(detail_frame, width=150),
            "Due Date": DateEntry(detail_frame),
            "Short Description": ctk.CTkEntry(detail_frame, width=150),
            "Description": ctk.CTkEntry(detail_frame, width=150),
            "Repeat": ctk.CTkEntry(detail_frame, width=150),
            "Days": ctk.CTkEntry(detail_frame, width=150),
            "Human Name": ctk.CTkEntry(detail_frame, width=150),
            "Contact": ctk.CTkEntry(detail_frame, width=150),
            "Email": ctk.CTkEntry(detail_frame, width=150),
            "Importance": ctk.CTkEntry(detail_frame, width=150),
            "Status": ctk.CTkComboBox(detail_frame, values=["not stated", "in progress", "complete"]),
            "Price": ctk.CTkEntry(detail_frame, width=150),
            "Link": ctk.CTkEntry(detail_frame, width=150),
            "Created Date": ctk.CTkLabel(detail_frame, text=f"Created Date: {self.routine_data[5]}"),
        }

        for i, (key, field) in enumerate(self.fields.items()):
            row = i // 5
            column = i % 5
            ctk.CTkLabel(detail_frame, text=key).grid(row=row * 2, column=column, padx=5, pady=5, sticky="w")
            field.grid(row=row * 2 + 1, column=column, padx=5, pady=5, sticky="w")

        # Checkbox for "Verified" with correct initial state
        self.verified_var = ctk.BooleanVar(value=self.routine_data[14] == 1)
        verified_checkbox = ctk.CTkCheckBox(detail_frame, text="Verified", variable=self.verified_var)
        verified_checkbox.grid(row=(len(self.fields) // 3) * 2 + 2, column=0, columnspan=3, padx=5, pady=5, sticky="w")




        # Create a toolbar for text editing features
        toolbar = tk.Frame(self)
        toolbar.grid(row=(len(self.fields) // 3) * 2 + 3, column=0, padx=10, pady=10, sticky="w")

        # Buttons for bold, italic, underline, and alignment
        bold_btn = tk.Button(
            toolbar, text="B", command=lambda: apply_text_style(self.rich_text, "bold")
        )
        italic_btn = tk.Button(
            toolbar, text="I", command=lambda: apply_text_style(self.rich_text, "italic")
        )
        underline_btn = tk.Button(
            toolbar, text="U", command=lambda: apply_text_style(self.rich_text, "underline")
        )
        align_left_btn = tk.Button(
            toolbar, text="L", command=lambda: set_text_alignment(self.rich_text, "left")
        )
        align_center_btn = tk.Button(
            toolbar, text="C", command=lambda: set_text_alignment(self.rich_text, "center")
        )
        align_right_btn = tk.Button(
            toolbar, text="R", command=lambda: set_text_alignment(self.rich_text, "right")
        )
        rtl_btn = tk.Button(
            toolbar, text="RTL", command=lambda: set_right_to_left(self.rich_text)
        )

        # Arrange toolbar buttons
        for button in [bold_btn, italic_btn, underline_btn, align_left_btn, align_center_btn, align_right_btn, rtl_btn]:
            button.pack(side="left", padx=5, pady=5)


        # Frame for detail entry fields
        detail_frame = ctk.CTkFrame(self)
        detail_frame.grid(row=(len(self.fields) // 3) * 2 + 4, column=0, padx=10, pady=10)

     # Rich text box for detailed descriptions
        # Rich text box with HTML formatting
        self.rich_text = HTMLScrolledText(detail_frame, height=10)
        self.rich_text.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        # Save button to update the database
        self.save_button = ctk.CTkButton(detail_frame, text="Save Changes", command=self.save_changes)
        self.save_button.grid(row=(len(self.fields) // 3) * 2 + 5, column=0, columnspan=3, padx=10, pady=10)

        self.add_property_button = ctk.CTkButton(detail_frame, text="+ Add Property", command=self.add_property)
        self.add_property_button.grid(row=len(self.fields) // 3 * 2 + 6, column=0, columnspan=3, pady=5)

        

        # Populate fields with fetched data
        self.populate_fields()

# Method to fetch and display custom properties
        self.custom_properties_frame = ctk.CTkFrame(self)
        self.custom_properties_frame.grid(row=len(self.fields) // 3 * 2 + 6, column=0, columnspan=3, pady=5)
        self.display_custom_properties()

    def display_custom_properties(self):
        """Fetch and display custom properties based on the routine's path, with dynamic input widgets."""
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute("SELECT name, type FROM properties WHERE path = ?", (self.routine_data[4],))  # Assuming path is at index 4
        properties = cur.fetchall()
        row = 1  # Start from the second row to give space for headers or other elements
        for name, prop_type in properties:
            print(f"Property: {name}, Type: {prop_type}")
        # Existing widget creation code
        # Existing widget grid code
            print(f"Widget for {name} created and placed.")
            label = ctk.CTkLabel(self.custom_properties_frame, text=name)
            label.grid(row=row, column=0, padx=5, pady=2, sticky="w")
            
            # Create dynamic input based on property type
            input_widget = None
            if prop_type == "date":
                input_widget = DateEntry(self.custom_properties_frame)
            elif prop_type == "number":
                input_widget = ctk.CTkEntry(self.custom_properties_frame, placeholder_text="Enter number")
            elif prop_type == "checkbox":
                var = tk.BooleanVar()
                input_widget = ctk.CTkCheckBox(self.custom_properties_frame, text="", variable=var)
            elif prop_type == "URL":
                input_widget = ctk.CTkEntry(self.custom_properties_frame, placeholder_text="Enter URL")
            elif prop_type == "email":
                input_widget = ctk.CTkEntry(self.custom_properties_frame, placeholder_text="Enter email")
            elif prop_type == "phone":
                input_widget = ctk.CTkEntry(self.custom_properties_frame, placeholder_text="Enter phone number")
            elif prop_type == "long text":
                input_widget = ctk.CTkEntry(self.custom_properties_frame, placeholder_text="Enter text", width=300)
            elif prop_type == "short text":
                input_widget = ctk.CTkEntry(self.custom_properties_frame, placeholder_text="Enter text", width=150)
            else:
                input_widget = ctk.CTkLabel(self.custom_properties_frame, text=f"Unhandled type: {prop_type}")

            if input_widget:
                input_widget.grid(row=row, column=1, padx=5, pady=2, sticky="w")
                self.custom_property_widgets[name] = input_widget
            row += 1
            
        conn.close()
        self.populate_fields()


    def show_tooltip(self, event, text):
        """Show tooltip with property type."""
        self.tooltip = tk.Toplevel()
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{event.widget.winfo_pointerx()}+{event.widget.winfo_pointery() + 20}")
        tk.Label(self.tooltip, text=text, background="yellow", relief='solid', borderwidth=1).pack()

    def hide_tooltip(self):
        """Hide tooltip."""
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None

    def add_property(self):
        if self.routine_data:
            routine_path = self.routine_data[4]  # Assuming the path is at index 4
            property_window = PropertyWindow(self, path=routine_path)
            property_window.grab_set()  # Make the property window modal
    
    def fetch_routine_data(self, routine_name):
        """Fetch routine data from the SQLite database."""
        try:
            conn = sqlite3.connect(DB_NAME)
            cur = conn.cursor()
            cur.execute("SELECT * FROM routines WHERE name = ?", (routine_name,))
            routine_data = cur.fetchone()
            print("Fetched routine data:", routine_data)  # Diagnostic print
            return routine_data
        except Exception as e:
            messagebox.showerror("Database Error", f"Error fetching routine data: {e}")
            return None
        finally:
            conn.close()
        return routine_data
    def populate_fields(self):
        """Populate fields with fetched routine data."""
        print("Populating fields...")

        if not self.routine_data:
            messagebox.showerror("Error", "Routine data could not be fetched.")
            return
        print("Routine Data:", self.routine_data)  # Diagnostic print to see what data was fetched

        # Clear fields before populating
        for field in self.fields.values():
            if isinstance(field, ctk.CTkEntry):
                field.delete(0, tk.END)

        # Populate each field with appropriate data, handling exceptions
        try:
            self.fields["Routine Name"].insert(0, self.routine_data[2])  # name
            self.fields["Duration (sec)"].insert(0, str(self.routine_data[3]))  # duration
            self.fields["Path"].insert(0, self.routine_data[4])  # path
            due_date = self.routine_data[6]  # due_date
            if due_date:
                self.fields["Due Date"].set_date(dt.datetime.strptime(due_date, "%Y-%m-%d"))
            else:
                self.fields["Due Date"].set_date(dt.datetime.now())
            self.fields["Short Description"].insert(0, self.routine_data[7] or "")  # short_description
            self.fields["Description"].insert(0, self.routine_data[8] or "")  # description
            self.fields["Repeat"].insert(0, self.routine_data[14] or "none")  # repeat
            self.fields["Days"].insert(0, self.routine_data[15] or "0,0,0,0,0,0,0")  # days
            self.fields["Human Name"].insert(0, self.routine_data[9] or "guest")  # human_name
            self.fields["Contact"].insert(0, self.routine_data[16] or "")  # contact
            self.fields["Email"].insert(0, self.routine_data[17] or "")  # email
            self.fields["Importance"].insert(0, self.routine_data[11] or "not")  # importance
            self.fields["Status"].set(self.routine_data[12] or "not stated")  # status
            self.fields["Price"].insert(0, str(self.routine_data[13] or 0))  # price
            self.fields["Link"].insert(0, self.routine_data[18] or "https://")  # link
            # Clear the rich text box and populate with the description
            self.rich_text.delete("1.0", tk.END)
            self.rich_text.insert("1.0", self.routine_data[8] or "")
            
            
            other_properties = json.loads(self.routine_data[19])
            print("Other Properties:", other_properties)  # Print the deserialized other_properties data
            print("Populating custom properties...")
            for prop_name, value in other_properties.items():
                widget = self.custom_property_widgets.get(prop_name)
                if widget:
                    if isinstance(widget, ctk.CTkEntry) or isinstance(widget, DateEntry):
                        widget.delete(0, tk.END)
                        widget.insert(0, value)
                    elif isinstance(widget, ctk.CTkCheckBox):
                        widget.var.set(value)
                    print(f"Populated {prop_name} with {value}")

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while populating fields: {e}")

    
    def save_changes(self):
        """Save changes made to the routine details."""
        try:
            conn = sqlite3.connect(DB_NAME)
            cur = conn.cursor()

            # Get the order number from the label and extract the numeric part
            order_num_text = self.fields["Order Number"].cget("text")  # "Order Number: X"
            order_num = int(order_num_text.split(":")[1].strip())  # Extracts the number after ":"

            # Retrieve rich text content and update the description
            full_description = self.rich_text.get("1.0", tk.END).strip()  # Get the text from the rich text box

            # Updated values with correct order number extraction
            updated_values = {
                "name": self.fields["Routine Name"].get(),
                "order_num": order_num,  # Use extracted order number
                "duration": int(self.fields["Duration (sec)"].get()),
                "path": self.fields["Path"].get(),
                "due_date": self.fields["Due Date"].get_date().strftime("%Y-%m-%d"),
                "short_description": self.fields["Short Description"].get(),
                "description": full_description,  # Save the rich text content
                "repeat": self.fields["Repeat"].get(),
                "days": self.fields["Days"].get(),
                "human_name": self.fields["Human Name"].get(),
                "contact": self.fields["Contact"].get(),
                "email": self.fields["Email"].get(),
                "importance": self.fields["Importance"].get(),
                "status": self.fields["Status"].get(),
                "price": float(self.fields["Price"].get()),
                "link": self.fields["Link"].get(),
                "verified": self.verified_var.get(),  # Checkbox value
            }

            custom_props = {}
            for prop_name, widget in self.custom_property_widgets.items():
                if isinstance(widget, (ctk.CTkEntry, DateEntry)):
                    custom_props[prop_name] = widget.get()
                elif isinstance(widget, ctk.CTkCheckBox):
                    custom_props[prop_name] = widget.var.get()
            updated_values['other_properties'] = json.dumps(custom_props)  # Serialize as JSON

            # Update the routine in the database with the correct order number
            cur.execute(
                """
                UPDATE routines 
                SET order_num = ?, name = ?, duration = ?, path = ?, due_date = ?, short_description = ?, description = ?, repeat = ?, 
                days = ?, human_name = ?, contact = ?, email = ?, verified = ?, importance = ?, status = ?, price = ?, 
                link = ?, other_properties = ?
                WHERE name = ?
                """,
                (
                    updated_values["order_num"],
                    updated_values["name"],
                    updated_values["duration"],
                    updated_values["path"],
                    updated_values["due_date"],
                    updated_values["short_description"],
                    updated_values["description"],
                    updated_values["repeat"],
                    updated_values["days"],
                    updated_values["human_name"],
                    updated_values["contact"],
                    updated_values["email"],
                    updated_values["verified"],
                    updated_values["importance"],
                    updated_values["status"],
                    updated_values["price"],
                    updated_values["link"],
                    updated_values["other_properties"],
                    self.routine_name,
                ),
            )

            conn.commit()

            # Refresh data after saving and repopulate fields
            self.routine_data = self.fetch_routine_data(self.routine_name)
            self.populate_fields()  # Re-populate fields after save

            messagebox.showinfo("Changes Saved", f"Changes to {self.routine_name} have been saved.")

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while saving changes: {e}")

        finally:
            conn.close()  # Ensure the database connection is always closed
            
class PlayRoutineWindow(ctk.CTkToplevel):
    def __init__(self, parent, routine_name, routine_duration, log_callback, on_completion=None):
        super().__init__(parent)
        self.title(f"Playing {routine_name}")

        self.routine_name = routine_name
        self.routine_duration = routine_duration
        self.log_callback = log_callback
        self.on_completion = on_completion
        self.remaining_time = routine_duration
        self.is_paused = False
        self.is_running = True  # Flag to determine if the window is still open

        self.countdown_label = ctk.CTkLabel(self, text=f"Time Remaining: {self.remaining_time} sec")
        self.countdown_label.pack(pady=10)


        button_frame = ctk.CTkFrame(self)
        button_frame.pack(pady=10)
        

        self.pause_button = ctk.CTkButton(button_frame, text="Pause", command=self.pause_resume)
        self.pause_button.pack(side=tk.LEFT, padx=5)

        skip_button = ctk.CTkButton(button_frame, text="Skip", command=self.skip)
        skip_button.pack(side=tk.LEFT, padx=5)

        early_finish_button = ctk.CTkButton(button_frame, text="Finish Early", command=self.finish_early)
        early_finish_button.pack(side=tk.LEFT, padx=5)

        self.countdown_thread = threading.Thread(target=self.countdown)
        self.countdown_thread.start()

    def pause_resume(self):
        if self.is_paused:
            self.is_paused = False
            self.pause_button.configure(text="Pause")
        else:
            self.is_paused = True
            self.pause_button.configure(text="Resume")

    def skip(self):
        self.remaining_time = 0
        self.close_window("Skipped")

    def finish_early(self):
        self.remaining_time = 0
        self.close_window("Finished Early")

    def close_window(self, status):
        self.is_running = False  # Stop the countdown thread
        end_time = time.strftime("%Y-%m-%d %H:%M:%S")
        self.log_callback(self.routine_name, self.start_time, end_time, status)
        if self.on_completion:
            self.on_completion()  # Callback for when the routine is completed
        self.destroy()

    def countdown(self):
        self.start_time = time.strftime("%Y-%m-%d %H:%M:%S")
        while self.is_running and self.remaining_time > 0:
            if not self.is_paused:
                time.sleep(1)
                self.remaining_time -= 1
                # Check if the window is still running before updating the label
                if self.is_running:
                    self.countdown_label.configure(text=f"Time Remaining: {self.remaining_time} sec")
            else:
                time.sleep(1)

        if self.is_running and self.remaining_time == 0 and not self.is_paused:
            self.close_window("Finished")

    def pause_resume(self):
        if self.is_paused:
            self.is_paused = False
            self.pause_button.configure(text="Pause")
        else:
            self.is_paused = True
            self.pause_button.configure(text="Resume")

    def skip(self):
        self.remaining_time = 0
        self.close_window("Skipped")

    def finish_early(self):
        self.remaining_time = 0
        self.close_window("Finished Early")

    def close_window(self, status):
        end_time = time.strftime("%Y-%m-%d %H:%M:%S")
        self.log_callback(self.routine_name, self.start_time, end_time, status)
        if self.on_completion:
            self.on_completion()  # Callback for when the routine is completed
        self.destroy()

    def countdown(self):
        self.start_time = time.strftime("%Y-%m-%d %H:%M:%S")
        while self.remaining_time > 0:
            if not self.is_paused:
                time.sleep(1)
                self.remaining_time -= 1
                self.countdown_label.configure(text=f"Time Remaining: {self.remaining_time} sec")
            else:
                time.sleep(1)

        if self.remaining_time == 0 and not self.is_paused:
            self.close_window("Finished")


class RoutineApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Routine Manager")
        init_db()
        
        
        ctk.set_appearance_mode("dark")  # Set to system theme (light or dark)
        ctk.set_default_color_theme("dark-blue")  # Set the default theme
        
        
        
        
        #background color
        
        self.path = "home"
        self.path_label = ctk.CTkLabel(self, text=f"Path: {self.path}")
        self.path_label.pack(pady=10)

        change_path_button = ctk.CTkButton(self, text="Go Home", command=lambda: self.update_path("home"))
        change_path_button.pack(pady=10)

        self.next_order = 1
        
        self.routine_tree = ttk.Treeview(
            self, columns=("Order", "Name", "Duration", "Path"), show="headings"
        )
        self.routine_tree.heading("Order", text="Order")
        self.routine_tree.heading("Name", text="Routine Name")
        self.routine_tree.heading("Duration", text="Duration (sec)")
        self.routine_tree.heading("Path", text="Path")
        self.routine_tree.pack(pady=10, padx=10, expand=True, fill="both")
        
        self.routine_tree.bind("<Double-Button-1>", self.on_double_click_routine)
        

        

        self.load_routines()
        self.next_order = self.determine_next_order()  # Determine next order number

        addupdate_frame = ctk.CTkFrame(self)
        addupdate_frame.pack(pady=10, padx=10)
        
        play_button = ctk.CTkButton(addupdate_frame, text="Play Routine", command=self.play_routine)
        play_button.grid(row=0, column=4)

        # Button to play all routines
        play_all_button = ctk.CTkButton(addupdate_frame, text="Play All Routines", command=self.play_all_routines)
        play_all_button.grid(row=0, column=5)

        # "Move Up" and "Move Down" buttons
        move_up_button = ctk.CTkButton(addupdate_frame, text="Move Up", command=self.move_up)
        move_up_button.grid(row=0, column=6)

        move_down_button = ctk.CTkButton(addupdate_frame, text="Move Down", command=self.move_down)
        move_down_button.grid(row=0, column=7)

       
        control_frame = ctk.CTkFrame(self)
        control_frame.pack(pady=10, padx=10)

        self.name_entry = ctk.CTkEntry(control_frame, width=100)
        self.name_entry.grid(row=0, column=0)

        self.duration_entry = ctk.CTkEntry(control_frame, width=100)
        self.duration_entry.grid(row=0, column=1)
        
        add_button = ctk.CTkButton(control_frame, text="Add Routine", command=self.add_routine)
        add_button.grid(row=0, column=2)


        update_button = ctk.CTkButton(control_frame, text="Update Routine", command=self.update_routine)
        update_button.grid(row=0, column=3)
        
        open_card_button = ctk.CTkButton(control_frame, text="Open Full Card", command=self.open_full_card)
        open_card_button.grid(row=0, column=4)


 
        self.reassign_order_numbers()

        # Treeview to show logs
        self.log_tree = ttk.Treeview(self, columns=("Routine", "Start Time", "End Time", "Status"), show="headings")
        self.log_tree.heading("Routine", text="Routine Name")
        self.log_tree.heading("Start Time", text="Start Time")
        self.log_tree.heading("End Time", text="End Time")
        self.log_tree.heading("Status", text="Status")
        self.log_tree.pack(pady=10, padx=10, expand=True, fill=tk.BOTH)

        # Frame for date filter
        self.filter_frame = ctk.CTkFrame(self)
        self.filter_frame.pack(pady=10, padx=10)

        self.start_date_picker = DateEntry(
            self.filter_frame,
            width=12,
            background="darkblue",
            foreground="white",
            borderwidth=2,
            year=2024,
            month=4,
            day=26,
        )
        self.start_date_picker.pack(side=ctk.LEFT, padx=5)

        self.end_date_picker = DateEntry(
            self.filter_frame,
            width=12,
            background="darkblue",
            foreground="white",
            borderwidth=2,
            year=2024,
            month=4,
            day=26,
        )
        self.end_date_picker.pack(side=ctk.LEFT, padx=5)

        filter_button = ctk.CTkButton(self.filter_frame, text="Filter Logs", command=self.filter_logs_by_date)
        filter_button.pack(side=tk.LEFT, padx=5)
        self.load_routines()  # Load routines from SQLite database
        self.load_logs()  # Load logs from SQLite database
        
        self.update_path("home")



    def open_full_card(self):
        selected = self.routine_tree.selection()
        if not selected:
            messagebox.showerror("No selection", "Please select a routine to view details.")
            return

        routine_name = self.routine_tree.item(selected[0], "values")[1]
        RoutineDetailWindow(self, routine_name)  # Open the detail window for the selected routine
    def load_routines(self):
        """Load routines from the SQLite database based on the current path."""
        self.routine_tree.delete(*self.routine_tree.get_children())  # Clear existing routines
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()

        cur.execute(
            "SELECT order_num, name, duration, path FROM routines WHERE path = ? ORDER BY order_num",
            (self.path,)
        )

        routines = cur.fetchall()
        for routine in routines:
            self.routine_tree.insert("", "end", values=routine)  # Add routines to the Treeview

        conn.close()  # Close the connection

        
    def refresh_routines(self):
        """Refresh routines in the Treeview based on the current path."""
        self.routine_tree.delete(*self.routine_tree.get_children())  # Clear existing routines
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        # Fetch routines matching the current path
        cur.execute(
            "SELECT order_num, name, duration, path FROM routines WHERE path = ? ORDER BY order_num",
            (self.path,)
        )
        for row in cur.fetchall():
            self.routine_tree.insert("", "end", values=row)  # Add matching routines to the Treeview
        conn.close()



        
    def on_double_click_routine(self, event):
        """Handler for double-clicking a routine. Updates the path."""
        selected = self.routine_tree.selection()
        if selected:
            item = selected[0]
            values = self.routine_tree.item(item, "values")
            _, routine_name, _, path = values  # Get the routine name and path
            new_path = f"{self.path}/{routine_name}"  # Create the new path
            self.update_path(new_path)  # Update the path

    def update_path(self, new_path):
        """Update the path and refresh the routines based on the updated path."""
        self.path = new_path  # Update the current path
        self.path_label.configure(text=f"Path: {self.path}")  # Reflect the change in the label
        self.load_routines()  # Reload routines to reflect the updated path



    def save_routines(self):
        """Save all routines from the Treeview to the SQLite database."""
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()

        # Save routines with updated order numbers
        for item in self.routine_tree.get_children():
            order_num, name, duration, path = self.routine_tree.item(item, "values")

            # Fetch existing routine data to avoid overwriting important details
            cur.execute("SELECT * FROM routines WHERE name = ?", (name,))
            existing_data = cur.fetchone()

            # If existing data is found, preserve all details except order_num
            if existing_data:
                updated_values = list(existing_data)
                updated_values[1] = order_num  # Update the order number

                cur.execute(
                    """
                    UPDATE routines 
                    SET order_num = ?, name = ?, duration = ?, path = ?, due_date = ?, short_description = ?, description = ?, repeat = ?, 
                    days = ?, human_name = ?, contact = ?, email = ?, verified = ?, importance = ?, status = ?, price = ?, 
                    link = ?
                    WHERE id = ?
                    """,
                    updated_values
                )
            else:
                # If no existing data, insert new routine with minimal data
                cur.execute(
                    "INSERT INTO routines (order_num, name, duration, path) VALUES (?, ?, ?, ?)",
                    (order_num, name, duration, path),
                )

        conn.commit()  # Commit changes to database
        conn.close()  # Close connection
    def load_logs(self):
        # Clear existing logs in the Treeview
        self.log_tree.delete(*self.log_tree.get_children())

        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        # Select all logs
        cur.execute("SELECT routine_name, start_time, end_time, status FROM logs")
        logs = cur.fetchall()

        for log in logs:
            # Unpack the log data into individual variables
            routine_name, start_time, end_time, status = log
            # Insert into Treeview
            self.log_tree.insert("", "end", values=(routine_name, start_time, end_time, status))

        conn.close()

        

    def play_all_routines(self):
        # Get the starting index from the selected routine
        selected = self.routine_tree.selection()
        if not selected:
            messagebox.showerror("No selection", "Please select a routine to start playing.")
            return

        start_idx = self.routine_tree.index(selected[0])

        # Get all routines from the starting index onwards
        all_routines = self.routine_tree.get_children()
        routines_to_play = all_routines[start_idx:]

        # Play each routine one after another
        self.play_next_routine(routines_to_play, 0)

    def play_next_routine(self, routines_to_play, index):
        if index >= len(routines_to_play):
            return  # No more routines to play

        routine_item = routines_to_play[index]
        # Unpack with correct number of variables
        order, routine_name, routine_duration, path = self.routine_tree.item(routine_item, "values")
        routine_duration = int(routine_duration)

        # Create a new PlayRoutineWindow with a callback to move to the next routine
        play_window = PlayRoutineWindow(
            self,
            routine_name,
            routine_duration,
            self.log_routine,
            on_completion=lambda: self.play_next_routine(routines_to_play, index + 1),
        )

    def move_up(self):
            selected = self.routine_tree.selection()
            if not selected:
                messagebox.showerror("No selection", "Please select a routine to move up.")
                return

            item_id = selected[0]
            current_idx = self.routine_tree.index(item_id)

            if current_idx == 0:
                messagebox.showwarning("Cannot Move", "This routine is already at the top.")
                return

            self.routine_tree.move(item_id, "", current_idx - 1)  # Move item up
            self.reassign_order_numbers()  # Reassign order numbers
            self.save_routines()  # Save the new order to the database

            # Refresh the Treeview to reflect the new order
            self.load_routines()


    def move_down(self):
        selected = self.routine_tree.selection()
        if not selected:
            messagebox.showerror("No selection", "Please select a routine to move down.")
            return

        item_id = selected[0]
        current_idx = self.routine_tree.index(item_id)

        last_idx = len(self.routine_tree.get_children()) - 1
        if current_idx == last_idx:
            messagebox.showwarning("Cannot Move", "This routine is already at the bottom.")
            return

        self.routine_tree.move(item_id, "", current_idx + 1)  # Move item down
        self.reassign_order_numbers()  # Reassign order numbers
        self.save_routines()  # Save the new order to the database

        # Refresh the Treeview to reflect the new order
        self.load_routines()

    def reassign_order_numbers(self):
        """Reassign order numbers based on the current order in the Treeview."""
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()

        for idx, item_id in enumerate(self.routine_tree.get_children()):
            order_num = idx + 1  # New order number
            values = self.routine_tree.item(item_id, "values")

            # Update the order number in the Treeview and database
            new_values = (order_num, *values[1:])
            self.routine_tree.item(item_id, values=new_values)  # Update in Treeview

            # Save to database
            cur.execute("UPDATE routines SET order_num = ? WHERE name = ?", (order_num, values[1]))

        conn.commit()
        conn.close()
    def determine_next_order(self):
        """Determine the next available order number from the routines in the Treeview."""
        current_orders = [
            int(self.routine_tree.item(item, "values")[0])
            for item in self.routine_tree.get_children()
        ]
        return max(current_orders, default=0) + 1

    def filter_logs_by_date(self):
        start_date = self.start_date_picker.get_date()  # datetime.date instance
        end_date = self.start_date_picker.get_date()  # datetime.date instance

        # Clear current log entries
        for row in self.log_tree.get_children():
            self.log_tree.delete(row)

        # Filter log history
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute("SELECT * FROM logs")
        logs = cur.fetchall()

        for log in logs:
            routine_name, start_time, end_time, status = log
            log_start_date = dt.datetime.strptime(start_time.split(" ")[0], "%Y-%m-%d").date()

            if start_date <= log_start_date <= end_date:
                self.log_tree.insert("", "end", values=(routine_name, start_time, end_time, status))

            conn.close()
    def add_routine(self):
        name = self.name_entry.get().strip() or "Guest"  # Default name if blank
        try:
            duration = int(self.duration_entry.get().strip())  # Ensure duration is an integer
        except ValueError:
            messagebox.showerror("Invalid input", "Please enter a valid duration (integer).")
            return

        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()

        # Check if the routine name already exists
        cur.execute("SELECT name FROM routines WHERE name = ?", (name,))
        if cur.fetchone():
            messagebox.showerror("Duplicate name", "A routine with this name already exists.")
            conn.close()
            return

        # Assign the order number and add to Treeview
        order = self.next_order
        self.next_order += 1

        # Prepare default values for the routine
        path = self.path
        due_date = None
        short_description = "A short description"
        description = "A detailed description"
        human_name = "guest"
        repeat = "none"  # No repeat by default
        days = "0,0,0,0,0,0,0"  # No days selected by default
        contact = ''  # Blank by default
        email = ''  # Blank by default
        verified = 0
        importance = "not"
        status = "not stated"
        price = 0
        link = 'https://'  # Default link prefix

        # Execute the corrected insert query
        cur.execute(
            """
            INSERT INTO routines (
                order_num, name, duration, path, due_date, short_description,
                description, human_name, repeat, days, contact, email, verified,
                importance, status, price, link
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                order, name, duration, path, due_date, short_description, description,
                human_name, repeat, days, contact, email, verified, importance,
                status, price, link,
            ),
        )

        conn.commit()
        conn.close()

        # Add routine to the Treeview
        self.routine_tree.insert("", "end", values=(order, name, duration, path))

        self.name_entry.delete(0, tk.END)
        self.duration_entry.delete(0, tk.END)
        messagebox.showinfo("Routine Added", "New routine added successfully with default settings.")

    def update_routine(self):
        selected = self.routine_tree.selection()
        if not selected:
            messagebox.showerror("No selection", "Please select a routine to update.")
            return

        name = self.name_entry.get().strip()
        try:
            duration = int(self.duration_entry.get().strip())
        except ValueError:
            messagebox.showerror("Invalid input", "Please enter a valid duration (integer).")
            return

        if not name:
            messagebox.showerror("Invalid input", "Routine name cannot be empty.")
            return

        selected_item = self.routine_tree.selection()[0]
        current_values = self.routine_tree.item(selected_item, "values")

        # Keep the original order and path while updating name and duration
        order = current_values[0]
        path = current_values[3]  # Keep existing path
        self.routine_tree.item(selected_item, values=(order, name, duration, path))  # Keep original path

        # Update the existing routine in the database
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute(
            "UPDATE routines SET name = ?, duration = ? WHERE order_num = ?",
            (name, duration, order),
        )
        conn.commit()
        conn.close()

        self.name_entry.delete(0, tk.END)
        self.duration_entry.delete(0, tk.END)

    def play_routine(self):
        selected = self.routine_tree.selection()
        if not selected:
            messagebox.showerror("No selection", "Please select a routine to play.")
            return

        # Get routine details, including the path
        order, routine_name, routine_duration, _ = self.routine_tree.item(selected, "values")

        # Open PlayRoutineWindow
        play_window = PlayRoutineWindow(
            self, routine_name, int(routine_duration), self.log_routine
        )
        
    def log_routine(self, routine_name, start_time, end_time, status):
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO logs (routine_name, start_time, end_time, status) VALUES (?, ?, ?, ?)",
            (routine_name, start_time, end_time, status),
        )
        conn.commit()
        conn.close()

        self.log_tree.insert("", "end", values=(routine_name, start_time, end_time, status))
class PropertyWindow(ctk.CTkToplevel):
    def __init__(self, parent, path):
        super().__init__(parent)
        self.title("Add New Property")
        self.path = path  # Store the path

        # Dropdown for selecting property type
        property_types = ["priority", "tags", "long text", "short text", "number",
                          "checkbox", "URL", "email", "phone", "formula",
                          "related routine", "created by", "assigned to", "button", "multi select", "date"]
        self.property_type_dropdown = ctk.CTkComboBox(self, values=property_types)
        self.property_type_dropdown.pack(pady=10)

        # Entry for naming the property
        self.property_name_entry = ctk.CTkEntry(self)
        self.property_name_entry.pack(pady=10)

        # Button to add the property
        add_button = ctk.CTkButton(self, text="Add Property", command=self.add_property_to_db)
        add_button.pack(pady=10)

    def add_property_to_db(self):
            property_type = self.property_type_dropdown.get()
            property_name = self.property_name_entry.get()

            # Open a connection to the database
            conn = sqlite3.connect(DB_NAME)
            cur = conn.cursor()

            # Insert new property into the properties table including the path
            try:
                cur.execute(
                    "INSERT INTO properties (type, name, path) VALUES (?, ?, ?)",
                    (property_type, property_name, self.path)
                )
                conn.commit()
                messagebox.showinfo("Success", "Property added successfully.")
            except sqlite3.Error as e:
                messagebox.showerror("Error", f"Failed to add property: {e}")
            finally:
                conn.close()

            self.destroy()

    def close_window(self):
        try:
            super().destroy()
        except AttributeError as e:
            print("Caught an AttributeError during destruction:", e)

if __name__ == "__main__":
    app = RoutineApp()
    app.mainloop()