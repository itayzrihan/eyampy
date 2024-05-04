
class RoutineDetailWindow(ctk.CTkToplevel):
    def __init__(self, parent, routine_name):
        super().__init__(parent)
        self.title(f"Routine Details: {routine_name}")
        self.routine_name = routine_name
        self.routine_data = self.fetch_routine_data(routine_name)

        if not self.routine_data:
            messagebox.showerror("Error", f"No data found for routine '{routine_name}'")
            self.destroy()
            return

        # Scrollable frame setup
        self.scrolled_frame = ScrolledFrame(self, scrollbars="vertical")
        self.scrolled_frame.grid(row=0, column=0, sticky='nsew')
        self.scrolled_frame.bind_scroll_wheel(self)
        self.content_frame = self.scrolled_frame.display_widget(ctk.CTkFrame)

        # Define fields and initialize with placeholder data
        self.fields = self.create_fields(self.content_frame)

        # Populate fields with fetched data
        self.populate_fields()

        # Custom properties display
        self.custom_properties_frame = ctk.CTkFrame(self.content_frame)
        self.custom_properties_frame.grid(row=len(self.fields) // 3 + 1, column=0, padx=10, pady=10, sticky="ew")
        self.display_custom_properties()

        # Save and Add Property buttons
        self.setup_buttons()

    def create_fields(self, frame):
        fields = {}
        labels = ["Order Number", "Routine Name", "Duration (sec)", "Path", "Due Date", "Short Description",
                  "Description", "Repeat", "Days", "Human Name", "Contact", "Email", "Importance", "Status", "Price",
                  "Link", "Created Date"]
        for i, label in enumerate(labels):
            row = i // 3 * 2
            column = i % 3
            if label in ["Order Number", "Created Date"]:
                fields[label] = ctk.CTkLabel(frame, text=label)
            elif label == "Status":
                fields[label] = ctk.CTkComboBox(frame, values=["not stated", "in progress", "complete"])
            else:
                fields[label] = ctk.CTkEntry(frame, width=150)
            ctk.CTkLabel(frame, text=label).grid(row=row, column=column, padx=5, pady=2, sticky="w")
            fields[label].grid(row=row + 1, column=column, padx=5, pady=2, sticky="w")
        return fields

    def setup_buttons(self):
        row = (len(self.fields) // 3 + 1) * 2
        self.save_button = ctk.CTkButton(self.content_frame, text="Save Changes", command=self.save_changes)
        self.save_button.grid(row=row, column=0, padx=10, pady=10)

        self.add_property_button = ctk.CTkButton(self.content_frame, text="+ Add Property", command=self.add_property)
        self.add_property_button.grid(row=row, column=1, padx=10, pady=10)

    def display_custom_properties(self):
        # Implementation to fetch and display custom properties
        pass

    def fetch_routine_data(self, routine_name):
        # Implementation to fetch routine data from the database
        pass

    def populate_fields(self):
        # Implementation to populate fields with fetched data
        pass

    def save_changes(self):
        # Implementation to save changes made to the routine details
        pass

    def add_property(self):
        # Implementation to add a new property to the routine
        pass