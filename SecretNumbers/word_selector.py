import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd
import os

# Word Selector Class
class WordSelectorApp:
    def __init__(self, master, main_menu):
        self.master = master
        self.main_menu = main_menu
        self.master.title("Word Selector")
        self.master.geometry("500x350")

        self.frame = tk.Frame(master)
        self.frame.pack(fill="both", expand=True)

        self.undo_stack = []
        self.redo_stack = []

        self.frame.bind("<Control-z>", self.undo_last_save)
        self.frame.bind("<Control-y>", self.redo_last_undo)
        self.frame.focus_set()

        self.back_button = tk.Button(self.frame, text="Back", command=self.go_back)
        self.back_button.pack(pady=10)

        self.csv_path = None
        self.word_df = None
        self.saved_choices = {}

        self.load_button = tk.Button(self.frame, text="Load CSV", command=self.load_csv)
        self.load_button.pack(pady=10)

        self.number_label = tk.Label(self.frame, text="Next available number:")
        self.number_label.pack(pady=10)

        self.number_entry = tk.Entry(self.frame)
        self.number_entry.pack(pady=5)

        self.number_display = tk.Label(self.frame, text="", wraplength=400)
        self.number_display.pack(pady=10)

        self.display_button = tk.Button(
            self.frame, text="Display Combinations", command=self.display_combinations
        )
        self.display_button.pack(pady=5)

        self.word_combobox = ttk.Combobox(self.frame, state="readonly")
        self.word_combobox.pack(pady=5)

        self.save_button = tk.Button(self.frame, text="Save Selection", command=self.save_selection)
        self.save_button.pack(pady=5)

        self.saved_table = ttk.Treeview(self.frame, columns=("Number", "Word"), show="headings", height=5)
        self.saved_table.heading("Number", text="Number")
        self.saved_table.heading("Word", text="Selected Word")
        self.saved_table.pack(pady=10)

        self.load_csv()  # Load CSV on start

    def go_back(self):
        self.frame.pack_forget()
        self.main_menu.frame.pack(fill="both", expand=True)

    def load_csv(self):
        self.csv_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if self.csv_path:
            self.word_df = pd.read_csv(self.csv_path, low_memory=False)
            self.saved_choices_path = self.csv_path.replace(".csv", "_choices.csv")
            if os.path.exists(self.saved_choices_path):
                
                self.saved_choices = pd.read_csv(self.saved_choices_path).set_index("Number").to_dict()["Word"]
            self.update_saved_table()
            self.update_next_number()
            messagebox.showinfo("Success", "CSV loaded successfully!")

    def update_saved_table(self):
        self.saved_table.delete(*self.saved_table.get_children())
        
        for number, word in reversed(list(self.saved_choices.items())):
            self.saved_table.insert("", "0", values=(number, word))

    def update_next_number(self):
     if self.word_df is not None:
        existing_numbers = [str(num).zfill(3) for num in self.word_df["Number"]]
        available_numbers = [num for num in existing_numbers if num not in self.saved_choices]
        
        # Determine the last used number from the saved choices
        if self.saved_choices:
            last_saved_number = max(map(int, self.saved_choices.keys()))
            next_number = str(last_saved_number + 1).zfill(3)  # Increment by 1 and ensure three-digit format
        else:
            next_number = available_numbers[0] if available_numbers else "000"  # Default if no saved choices
        
        self.number_entry.delete(0, tk.END)  # Clear existing content
        self.number_entry.insert(0, next_number)  # Set the next available number
        self.display_combinations()  # Refresh combinations
    def display_combinations(self):
        number = self.number_entry.get().zfill(3)
        if self.word_df is not None and number.isdigit() and int(number) in range(1000):
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
            
            self.current_button_index = 0
            self.highlight_current_button()

            self.frame.bind("<Left>", self.move_left)
            self.frame.bind("<Right>", self.move_right)
            self.frame.bind("<Return>", self.enter_key_pressed)
            self.frame.focus_set()
            
            self.number_display.config(text=f"Available combinations for {number}: " + ", ".join(combinations))
        else:
            messagebox.showwarning("Invalid", "Please enter a valid number or load a CSV file.")

    def undo_last_save(self, event=None):
        if self.saved_choices:
            last_saved_choice = list(self.saved_choices.items())[-1]
            self.undo_stack.append(last_saved_choice)
            del self.saved_choices[last_saved_choice[0]]
            self.update_saved_table()

            self.number_entry.delete(0, tk.END)
            self.number_entry.insert(0, last_saved_choice[0])
            self.display_combinations()

    def redo_last_undo(self, event=None):
        if self.undo_stack:
            last_undone_choice = self.undo_stack.pop()
            self.saved_choices[last_undone_choice[0]] = last_undone_choice[1]
            self.save_choices_to_csv()
            self.update_saved_table()
            self.update_next_number()

    def highlight_current_button(self):
        for i, button in enumerate(self.word_buttons):
            if i == self.current_button_index:
                button.config(bg="lightblue")
            else:
                button.config(bg="SystemButtonFace")

    def move_left(self, event=None):
        if self.current_button_index > 0:
            self.current_button_index -= 1
            self.highlight_current_button()

    def move_right(self, event=None):
        if self.current_button_index < len(self.word_buttons) - 1:
            self.current_button_index += 1
            self.highlight_current_button()

    def enter_key_pressed(self, event=None):
        self.on_button_click(self.word_buttons[self.current_button_index].cget("text"))

    def on_button_click(self, combination):
        self.save_selection(combination)

    def save_selection(self, selected_word=None):
        if selected_word is None:
            selected_word = self.word_buttons[self.current_button_index].cget("text")
        
        number = self.number_entry.get().zfill(3)

        if self.word_df is not None and selected_word:
            self.saved_choices[number] = selected_word
            self.save_choices_to_csv()
            self.update_saved_table()
            self.update_next_number()
            messagebox.showinfo("Success", "Selection saved!")
        else:
            messagebox.showwarning("Invalid", "Please select a valid combination.")

    def save_choices_to_csv(self):
        pd.DataFrame(
            [(number.zfill(3), word) for number, word in self.saved_choices.items()],
            columns=["Number", "Word"]
        ).to_csv(self.saved_choices_path, index=False)
