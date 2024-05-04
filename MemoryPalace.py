import tkinter as tk
from tkinter import messagebox
import random
from PIL import Image, ImageTk


# Memory Palace Game
class MemoryPalaceGame(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Memory Palace Game")
        
        # Create a 52-location map
        self.map_canvas = tk.Canvas(self, width=600, height=400, bg="lightgray")
        self.map_canvas.pack(pady=20)
        
        self.map_locations = []  # Track the locations of each card on the map
        self.card_deck = [f"Card {i + 1}" for i in range(52)]  # 52 unique cards
        
        self.place_button = tk.Button(self, text="Place Cards", command=self.place_cards)
        self.place_button.pack(pady=10)
        
        self.recall_button = tk.Button(self, text="Recall Cards", command=self.start_recall, state=tk.DISABLED)
        self.recall_button.pack(pady=10)
        
        self.reset_button = tk.Button(self, text="Reset", command=self.reset_game)
        self.reset_button.pack(pady=10)
        
        self.selected_card = None  # Track which card is being placed
        self.cards_on_map = {}  # Dictionary to track card placements
    
    def place_cards(self):
        if self.cards_on_map:
            messagebox.showinfo("Already Placed", "Cards are already placed on the map.")
            return
        
        random.shuffle(self.card_deck)  # Shuffle the deck for randomness
        
        # Create 52 distinct locations on the map (arbitrary example)
        self.map_locations = [
            (i % 13 * 45 + 20, i // 13 * 80 + 20) for i in range(52)
        ]
        
        self.map_canvas.bind("<Button-1>", self.map_click_handler)  # Handle map clicks
        
        self.selected_card = 0  # Start placing from the first card
        
        self.place_button.config(state=tk.DISABLED)
        self.recall_button.config(state=tk.NORMAL)  # Enable recall once cards are placed
    
    def map_click_handler(self, event):
        if self.selected_card is not None and self.selected_card < 52:
            # Get the card and the click location
            card = self.card_deck[self.selected_card]
            x, y = event.x, event.y
            
            # Place the card at the location
            self.map_canvas.create_text(x, y, text=card, fill="black", font=("Arial", 10))
            
            # Track the card placement
            self.cards_on_map[card] = (x, y)
            
            # Move to the next card to place
            self.selected_card += 1
            
            # If all cards are placed, unbind the click handler
            if self.selected_card == 52:
                self.map_canvas.unbind("<Button-1>")
    
    def start_recall(self):
        # Randomly select a location and ask the user to recall the card placed there
        if not self.cards_on_map:
            messagebox.showinfo("Place Cards First", "Place cards on the map before recalling.")
            return
        
        self.recall_button.config(state=tk.DISABLED)  # Disable while recalling
        
        # Select a random location to recall
        random_location = random.choice(list(self.map_locations))
        
        # Ask the user to recall the card at the selected location
        recall_result = messagebox.askquestion(
            "Recall Card",
            f"Which card was placed at location {random_location}?",
            icon="question",
            type="okcancel"
        )
        
        if recall_result == "ok":
            correct_card = None
            for card, loc in self.cards_on_map.items():
                if loc == random_location:
                    correct_card = card
                    break
            
            user_input = self.map_canvas.create_text(
                random_location[0], random_location[1],
                text="?",
                fill="red",
                font=("Arial", 10)
            )
            
            if correct_card:
                if messagebox.askyesno("Correct?", f"Was the card {correct_card}?"):
                    messagebox.showinfo("Correct!", f"You remembered correctly!")
                else:
                    messagebox.showerror("Incorrect!", f"The correct card was {correct_card}.")
            
            self.map_canvas.delete(user_input)  # Remove the question mark after feedback
        
        self.recall_button.config(state=tk.NORMAL)  # Re-enable for further recalls
    
    def reset_game(self):
        # Reset the map and cards on map
        self.map_canvas.delete("all")  # Clear the map
        self.cards_on_map.clear()  # Reset the card placement tracker
        self.selected_card = None
        
        # Re-enable place button and disable recall
        self.place_button.config(state=tk.NORMAL)
        self.recall_button.config(state=tk.DISABLED)

if __name__ == "__main__":
    app = MemoryPalaceGame()
    app.mainloop()
