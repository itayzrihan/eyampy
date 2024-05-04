import tkinter as tk
import random
import time
import threading
from tkinter import messagebox
from tkinter import ttk


class CardRecallGame(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Card Recall Game")
        
        self.deck = self.generate_deck()  # Full deck of 52 cards
        self.cards_to_recall = []  # Cards shown for the recall game
        
        self.intro_label = tk.Label(self, text="Welcome to the Card Recall Game!")
        self.intro_label.pack(pady=10)
        
        self.start_button = tk.Button(self, text="Start Game", command=self.start_game)
        self.start_button.pack(pady=10)
        
        self.cards_display = tk.Label(self, text="", font=("Arial", 14))
        self.cards_display.pack(pady=10)
        
        self.recall_frame = None  # Frame to display card selection
        self.correct_cards = None  # Correct card list for validation
    
    def generate_deck(self):
        suits = ["Hearts", "Diamonds", "Clubs", "Spades"]
        ranks = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
        return [f"{rank} of {suit}" for suit in suits for rank in ranks]

    def start_game(self):
        self.start_button.config(state=tk.DISABLED)
        
        # Randomly select 5 cards from the deck
        self.cards_to_recall = random.sample(self.deck, 5)
        
        # Display the 5 cards for 10 seconds
        self.cards_display.config(text="\n".join(self.cards_to_recall))
        
        # Start a thread to hide the cards after 10 seconds
        threading.Thread(target=self.hide_cards).start()

    def hide_cards(self):
        time.sleep(10)  # Display for 10 seconds
        self.cards_display.config(text="")

        # Display the recall options
        self.show_recall_options()

    def show_recall_options(self):
        if self.recall_frame:
            self.recall_frame.destroy()
        
        self.recall_frame = tk.Frame(self)
        self.recall_frame.pack(pady=10, padx=10)
        
        self.correct_cards = []

        # Create a Treeview to display all 52 cards
        self.card_tree = ttk.Treeview(
            self.recall_frame,
            columns=("Card"), 
            show="headings", 
            height=15
        )
        
        self.card_tree.heading("Card", text="Select the 5 cards you saw")
        
        # Populate the Treeview with all 52 cards
        for card in self.deck:
            self.card_tree.insert("", "end", values=(card,))
        
        self.card_tree.pack(pady=10, padx=10)

        # Button to submit the selected cards
        submit_button = tk.Button(
            self.recall_frame, 
            text="Submit", 
            command=self.check_recall
        )
        submit_button.pack(pady=10)
        
    def check_recall(self):
        selected_items = self.card_tree.selection()
        
        if len(selected_items) != 5:
            messagebox.showwarning(
                "Invalid Selection",
                "Please select exactly 5 cards."
            )
            return
        
        # Get the selected cards
        user_selected_cards = [self.card_tree.item(item, "values")[0] for item in selected_items]
        
        # Compare with the correct cards
        correct = set(self.cards_to_recall) == set(user_selected_cards)
        
        if correct:
            messagebox.showinfo("Result", "Correct! You remembered the correct 5 cards.")
        else:
            correct_cards_str = "\n".join(self.cards_to_recall)
            messagebox.showerror(
                "Result",
                f"Incorrect! The correct 5 cards were:\n{correct_cards_str}"
            )
        
        # Reset the game
        self.start_button.config(state=tk.NORMAL)
        self.recall_frame.destroy()  # Clear the recall frame
        
        self.cards_to_recall = []  # Reset the cards to recall
        self.correct_cards = None  # Reset the correct card list

if __name__ == "__main__":
    app = CardRecallGame()
    app.mainloop()
