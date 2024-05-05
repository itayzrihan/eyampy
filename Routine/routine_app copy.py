class RoutineDetailWindow(ctk.CTkToplevel):
    def __init__(self, parent, routine_name):
        super().__init__(parent)
        self.title(f"Routine Details: {routine_name}")
        self.geometry("800x600")  # Adjust the size as needed

        self.routine_name = routine_name
        self.custom_property_widgets = {}

        # Fetch routine data early to ensure fields have data
        self.routine_data = self.fetch_routine_data(routine_name)
        if not self.routine_data:
            messagebox.showerror("Error", f"No data found for routine '{routine_name}'")
            self.destroy()
            return

        routine_names = self.fetch_routine_names()

        # Scrollable canvas and frame setup
        self.canvas = ctk.CTkCanvas(self)
        self.scrollbar = ctk.CTkScrollbar(self, command=self.canvas.yview)
        self.scrollable_frame = ctk.CTkFrame(self.canvas)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        # Define fields and initialize with placeholder data
        self.fields = {
            # Definitions for fields like "Order Number", "Routine Name", etc.
        }

        # Create input fields and labels within the scrollable_frame
        for i, (key, field) in enumerate(self.fields.items()):
            row = i // 5
            column = i % 5
            label = ctk.CTkLabel(self.scrollable_frame, text=key)
            label.grid(row=row * 2, column=column, padx=5, pady=5, sticky="w")
            field.grid(row=row * 2 + 1, column=column, padx=5, pady=5, sticky="w")

        # Add additional components as necessary...

        self.populate_fields()

    # Implementation for fetch_routine_data, populate_fields, and other methods...
