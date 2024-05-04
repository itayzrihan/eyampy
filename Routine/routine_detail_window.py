import tkinter as tk
import customtkinter as ctk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import sqlite3
import datetime as dt
import time
import threading
from tkhtmlview import HTMLScrolledText

# Database setup (adjust to match your database setup)
DB_NAME = "routine_manager_v3.db"

class RoutineDetailWindow(ctk.CTkToplevel):
    def __init__(self, parent, routine_name):
        super().__init__(parent)
        self.title(f"Routine Details: {routine_name}")

        self.routine_name = routine_name
        
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

        # Add fields to the grid
        for i, (key, field) in enumerate(self.fields.items()):
            row = i // 3
            column = i % 3
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

        # Rich text box for detailed descriptions
        detail_frame = ctk.CTkFrame(self)
        detail_frame.grid(row=(len(self.fields) // 3) * 2 + 4, column=0, padx=10, pady=10)

        self.rich_text = HTMLScrolledText(detail_frame, height=10)
        self.rich_text.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        self.save_button = ctk.CTkButton(detail_frame, text="Save Changes", command=self.save_changes)
        self.save_button.grid(row=(len(self.fields) // 3) * 2 + 5, column=0, columnspan=3, padx=10, pady=10)

        self.add_propperty_button = ctk.CTkButton(detail_frame, text="Add Propperty", command=self.open_add_property_dialog)   
        self.add_propperty_button.grid(row=(len(self.fields) // 3) * 2 + 6, column=0, columnspan=3, padx=10, pady=10)
        self.populate_fields()  # Populate fields with fetched routine data

    def fetch_routine_data(self, routine_name):
        """Fetch routine data from the SQLite database."""
        try:
            conn = sqlite3.connect(DB_NAME)
            cur = conn.cursor()
            cur.execute("SELECT * FROM routines WHERE name = ?", (routine_name,))
            routine_data = cur.fetchone()
        except Exception as e:
            messagebox.showerror("Database Error", f"Error fetching routine data: {e}")
            return None
        finally:
            conn.close()  # Always ensure connection is closed

        return routine_data

    def populate_fields(self):
        """Populate fields with fetched routine data."""
        if not self.routine_data:
            messagebox.showerror("Error", "Routine data could not be fetched.")
            return

        # Clear fields before populating
        for field in self.fields.values():
            if isinstance(field, ctk.CTkEntry):
                field.delete(0, tk.END)

        # Populate each field with appropriate data, handling exceptions
        try:
            self.fields["Routine Name"].insert(0, self.routine_data[2])
            self.fields["Duration (sec)"].insert(0, str(self.routine_data[3]))
            self.fields["Path"].insert(0, self.routine_data[4])

            due_date = self.routine_data[6]
            if due_date:
                self.fields["Due Date"].set_date(dt.datetime.strptime(due_date, "%Y-%m-%d"))
            else:
                self.fields["Due Date"].set_date(dt.datetime.now())

            self.fields["Short Description"].insert(0, self.routine_data[7] or "")
            self.fields["Description"].insert(0, self.routine_data[8] or "")

            self.rich_text.delete("1.0", tk.END)  # Clear any existing text
            self.rich_text.insert("1.0", self.routine_data[8] or "")  # Insert description
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while populating fields: {e}")


    def open_add_property_dialog(self):
        AddPropertyDialog(self)

    def save_changes(self):
        """Save changes made to the routine details."""
        try:
            conn = sqlite3.connect(DB_NAME)
            cur = conn.cursor()

            order_num_text = self.fields["Order Number"].cget("text")  # "Order Number: X"
            order_num = int(order_num_text.split(":")[1].strip())  # Extracts the number after ":"

            full_description = self.rich_text.get("1.0", tk.END).strip()  # Get the text from the rich text box

            updated_values = {
                "name": self.fields["Routine Name"].get(),
                "order_num": order_num,  # Use extracted order number
                "duration": int(self.fields["Duration (sec)"].get()),
                "path": self.fields["Path"].get(),
                "due_date": self.fields["Due Date"].get_date().strftime("%Y-%m-%d"),
                "short_description": self.fields["Short Description"].get(),
                "description": full_description,
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

            cur.execute(
                """
                UPDATE routines 
                SET order_num = ?, name = ?, duration = ?, path = ?, due_date = ?, short_description = ?, description = ?, 
                repeat = ?, days = ?, human_name = ?, contact = ?, email = ?, verified = ?, importance = ?, 
                status = ?, price = ?, link = ?
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
                    self.routine_name,
                ),
            )

            conn.commit()

            self.routine_data = self.fetch_routine_data(self.routine_name)
            self.populate_fields()  # Re-populate fields after save

            messagebox.showinfo("Changes Saved", f"Changes to {self.routine_name} have been saved.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while saving changes: {e}")
        finally:
            conn.close()  # Ensure the database connection is always closed



class AddPropertyDialog(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Add Property")
        self.geometry("300x200")

        # Entry for property name
        self.property_name_entry = ctk.CTkEntry(self, placeholder_text="Property Name")
        self.property_name_entry.pack(pady=10)

        # Dropdown for property type
        self.property_type_var = tk.StringVar()
        self.property_type_combobox = ttk.Combobox(self, textvariable=self.property_type_var, state="readonly")
        self.property_type_combobox['values'] = ['number', 'text', 'URL']
        self.property_type_combobox.pack(pady=10)

        # Save button
        self.save_button = ctk.CTkButton(self, text="Save Property", command=self.save_property)
        self.save_button.pack(pady=10)

    def save_property(self):
        property_name = self.property_name_entry.get()
        property_type = self.property_type_var.get()
        if not property_name or not property_type:
            messagebox.showerror("Error", "All fields are required.")
            return

        # Save the new property in the database
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        try:
            cur.execute("INSERT INTO properties (type, name) VALUES (?, ?)", (property_type, property_name))
            conn.commit()
            messagebox.showinfo("Success", "Property added successfully.")
            self.destroy()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Property name must be unique.")
        finally:
            conn.close()
