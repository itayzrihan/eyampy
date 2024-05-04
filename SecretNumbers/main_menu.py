import tkinter as tk
from tkinter import messagebox
from word_selector import WordSelectorApp  # Import the Word Selector App

# Main Menu Class
class MainMenu:
    def __init__(self, master):
        self.master = master
        self.master.title("Main Menu")
        self.master.geometry("500x350")

        self.frame = tk.Frame(master)
        self.frame.pack(fill="both", expand=True)

        self.word_selector_button = tk.Button(
            self.frame, text="Open Word Selector", command=self.open_word_selector
        )
        self.word_selector_button.pack(pady=10)

        self.placeholder_button = tk.Button(self.frame, text="Placeholder", command=self.placeholder_action)
        self.placeholder_button.pack(pady=10)

        self.exit_button = tk.Button(self.frame, text="Exit", command=self.exit_application)
        self.exit_button.pack(pady=10)

    def open_word_selector(self):
        self.frame.pack_forget()
        self.word_selector = WordSelectorApp(self.master, self)

    def placeholder_action(self):
        messagebox.showinfo("Placeholder", "This is a placeholder action.")

    def exit_application(self):
        self.master.quit()
