import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd
import os

# Main Menu Class
class MainMenu:
    def __init__(self, master):
        self.master = master
        self.master.title("Main Menu")
        self.master.geometry("500x350")

        self.frame = tk.Frame(master)
        self.frame.pack(fill="both", expand=True)

        # Button to open the word selector app
        self.word_selector_button = tk.Button(
            self.frame, text="Open Word Selector", command=self.open_word_selector
        )
        self.word_selector_button.pack(pady=10)

        # Placeholder button for future functionality
        self.placeholder_button = tk.Button(self.frame, text="Placeholder", command=self.placeholder_action)
        self.placeholder_button.pack(pady=10)

        # Button to exit the application
        self.exit_button = tk.Button(self.frame, text="Exit", command=self.exit_application)
        self.exit_button.pack(pady=10)

    def open_word_selector(self):
        self.frame.pack_forget()  # Hide the current frame
        self.word_selector = WordSelectorApp(self.master, self)  # Pass the main menu instance for navigation

    def placeholder_action(self):
        messagebox.showinfo("Placeholder", "This is a placeholder action.")

    def exit_application(self):
        self.master.quit()

# Word Selector Class (existing functionality)
class WordSelectorApp:
    def __init__(self, master, main_menu):
        self.master = master
        self.main_menu = main_menu  # Store the main menu reference
        self.master.title("Word Selector")
        self.master.geometry("500x350")

        self.frame = tk.Frame(master)
        self.frame.pack(fill="both", expand=True)


        # Initialize undo and redo stacks
        self.undo_stack = []
        self.redo_stack = []

        # Bind undo and redo keyboard shortcuts
        self.frame.bind("<Control-z>", self.undo_last_save)
        self.frame.bind("<Control-y>", self.redo_last_undo)
        self.frame.focus_set()
        
        
        
        # Back button to return to the main menu
        self.back_button = tk.Button(self.frame, text="Back", command=self.go_back)
        self.back_button.pack(pady=10)

        self.csv_path = None
        self.word_df = None
        self.saved_choices = {}

        # Load button to select a CSV file
        self.load_button = tk.Button(self.frame, text="Load CSV", command=self.load_csv)
        self.load_button.pack(pady=10)

        # Number label and entry to navigate through numbers
        self.number_label = tk.Label(self.frame, text="Next available number:")
        self.number_label.pack(pady=10)

        self.number_entry = tk.Entry(self.frame)
        self.number_entry.pack(pady=5)

        self.number_display = tk.Label(self.frame, text="", wraplength=400)
        self.number_display.pack(pady=10)

        # Display combinations button
        self.display_button = tk.Button(
            self.frame, text="Display Combinations", command=self.display_combinations
        )
        self.display_button.pack(pady=5)

        # Combobox to select a single word option
        self.word_combobox = ttk.Combobox(self.frame, state="readonly")
        self.word_combobox.pack(pady=5)

        # Save button
        self.save_button = tk.Button(self.frame, text="Save Selection", command=self.save_selection)
        self.save_button.pack(pady=5)

        # Table to show saved words
        self.saved_table = ttk.Treeview(self.frame, columns=("Number", "Word"), show="headings", height=5)
        self.saved_table.heading("Number", text="Number")
        self.saved_table.heading("Word", text="Selected Word")
        self.saved_table.pack(pady=10)

        self.load_csv()  # Load CSV on start

    def go_back(self):
        self.frame.pack_forget()  # Hide the current frame
        self.main_menu.frame.pack(fill="both", expand=True)  # Show the main menu

    def load_csv(self):
        self.csv_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if self.csv_path:
            self.word_df = pd.read_csv(self.csv_path, low_memory=False)  # Read CSV with low_memory=False
            self.saved_choices_path = self.csv_path.replace(".csv", "_choices.csv")
            if os.path.exists(self.saved_choices_path):
                self.saved_choices = pd.read_csv(self.saved_choices_path).set_index("Number").to_dict()["Word"]
            self.update_saved_table()
            self.update_next_number()
            messagebox.showinfo("Success", "CSV loaded successfully!")
    def update_saved_table(self):
        self.saved_table.delete(*self.saved_table.get_children())
        
        # Display saved choices in reverse order to have the latest at the top
        for number, word in reversed(list(self.saved_choices.items())):
            self.saved_table.insert("", "0", values=(number, word))  # Insert at the top

    def update_next_number(self):
        if self.word_df is not None:
            existing_numbers = [str(num).zfill(3) for num in self.word_df["Number"]]  # Ensure three-digit format
            available_numbers = [num for num in existing_numbers if num not in self.saved_choices]

            if available_numbers:
                # Update the number entry with the next available
                self.number_entry.delete(0, tk.END)
                self.number_entry.insert(0, available_numbers[0])
                self.display_combinations()  # Refresh combinations
            else:
                self.number_display.config(text="No available combinations.")

    def display_combinations(self):
        number = self.number_entry.get().zfill(3)  # Ensure three-digit format
        if self.word_df is not None and number.isdigit() and int(number) in range(1000):
            # Clear any existing buttons
            if hasattr(self, 'button_frame'):
                self.button_frame.destroy()
            
            combinations = self.word_df[self.word_df["Number"] == int(number)].iloc[0, 1:].dropna().tolist()
            
            self.button_frame = tk.Frame(self.frame)
            self.button_frame.pack(pady=10)
            
            self.word_buttons = []
            for i, combination in enumerate(combinations):
                button = tk.Button(
                    self.button_frame, 
                    text=combination, 
                    command=lambda c=combination: self.on_button_click(c)
                )
                self.word_buttons.append(button)
                button.pack(side=tk.LEFT, padx=5)
            
            # Highlight the first button
            self.current_button_index = 0
            self.highlight_current_button()
            
            # Bind arrow keys for navigation
            self.frame.bind("<Left>", self.move_left)
            self.frame.bind("<Right>", self.move_right)
            self.frame.bind("<Return>", self.enter_key_pressed)
            self.frame.focus_set()
            
            self.number_display.config(text=f"Available combinations for {number}: " + ", ".join(combinations))
        else:
            messagebox.showwarning("Invalid", "Please enter a valid number or load a CSV file.")

    def undo_last_save(self, event=None):
            if self.saved_choices:
              last_saved_choice = list(self.saved_choices.items())[-1]  # Last saved
            self.undo_stack.append(last_saved_choice)  # Add to undo stack
            
            # Remove from saved choices and update the table
            del self.saved_choices[last_saved_choice[0]]
            self.update_saved_table()  # Update the table with the latest at the top

            # Reset to the previous number and display combinations
            self.number_entry.delete(0, tk.END)
            self.number_entry.insert(0, last_saved_choice[0])
            self.display_combinations()  # Update combinations
    def redo_last_undo(self, event=None):
        if self.undo_stack:
            last_undone_choice = self.undo_stack.pop()  # Last undone choice
            self.saved_choices[last_undone_choice[0]] = last_undone_choice[1]  # Restore to saved choices
            
            self.save_choices_to_csv()  # Save to CSV
            self.update_saved_table()  # Update the table with the latest at the top

            # Update the next available number
            self.update_next_number()


    def highlight_current_button(self):
        # Add a blue border to the focused button
        for i, button in enumerate(self.word_buttons):
            if i == self.current_button_index:
                button.config(bg="lightblue")  # Highlight
            else:
                button.config(bg="SystemButtonFace")  # Default color

    def move_left(self, event=None):
        # Move focus left and update highlight
        if self.current_button_index > 0:
            self.current_button_index -= 1
            self.highlight_current_button()

    def move_right(self, event=None):
        # Move focus right and update highlight
        if self.current_button_index < len(self.word_buttons) - 1:
            self.current_button_index += 1
            self.highlight_current_button()

    def enter_key_pressed(self, event=None):
        # Simulate button click
        self.on_button_click(self.word_buttons[self.current_button_index].cget("text"))


    def on_button_click(self, combination):
        # Save the selection when clicking a button
        self.save_selection(combination)
    def save_selection(self, selected_word=None):
        if selected_word is None:
            selected_word = self.word_buttons[self.current_button_index].cget("text")  # Get the current selection
        
        number = self.number_entry.get().zfill(3)  # Ensure three-digit format

        if self.word_df is not None and selected_word:
            self.saved_choices[number] = selected_word  # Save to the dictionary
            self.save_choices_to_csv()  # Save to CSV
            self.update_saved_table()  # Update the GUI table, inserting the latest at the top
            self.update_next_number()  # Move to the next number
            messagebox.showinfo("Success", "Selection saved!")  # Confirmation message
        else:
            messagebox.showwarning("Invalid", "Please select a valid combination.")

        if self.word_df is not None and selected_word:
            self.saved_choices[number] = selected_word
            self.save_choices_to_csv()
            self.update_saved_table() 
            self.update_next_number()  # This will reset the leftmost button to focus
            messagebox.showinfo("Success", "Selection saved!")
        else:
            messagebox.showwarning("Invalid", "Please select a word combination to save.")


    def save_selection(self, selected_word=None):
        if selected_word is None:
            selected_word = self.word_combobox.get()  # Backup method for mouse interaction
        
        number = self.number_entry.get().zfill(3)  # Ensure three-digit format
        
        if self.word_df is not None and selected_word:
            self.saved_choices[number] = selected_word
            self.save_choices_to_csv()
            self.update_saved_table() 
            self.update_next_number()  # This will reset the leftmost button to focus
            messagebox.showinfo("Success", "Selection saved!")
        else:
            messagebox.showwarning("Invalid", "Please select a word combination to save.")
    def save_choices_to_csv(self):
      pd.DataFrame(
    [(number.zfill(3), word) for number, word in self.saved_choices.items()],
    columns=["Number", "Word"],
).to_csv(self.saved_choices_path, index=False)  # Save with correct format

# Run the application with the Main Menu
root = tk.Tk()
main_menu = MainMenu(root)
root.mainloop()
