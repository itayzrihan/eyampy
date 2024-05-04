import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import time
import random
from PIL import Image, ImageTk

# A set of predefined images and their corresponding words
image_set = {
    "Apple": "apple.png",
    "Banana": "banana.png",
    "Cherry": "cherry.png",
    "Grape": "grape.png",
    "Orange": "orange.png",
    "Pineapple": "pineapple.png",
}

# Memory Association Game
class MemoryAssociationGame(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Memory Association Game")
        
        # Images to be shown to players
        self.images = []
        self.associations = []
        
        # Initialize game elements
        self.intro_label = tk.Label(self, text="Welcome to the Memory Association Game!")
        self.intro_label.pack(pady=10)
        
        self.start_button = tk.Button(self, text="Start Game", command=self.start_game)
        self.start_button.pack(pady=10)
        
        self.image_display_frame = tk.Frame(self)
        self.image_display_frame.pack(pady=10)
        
        self.recall_frame = tk.Frame(self)
        
    def start_game(self):
        # Disable start button while the game is running
        self.start_button.config(state=tk.DISABLED)
        
        # Clear previous game elements
        self.clear_game_elements()
        
        # Randomly select a subset of images and their corresponding words
        self.associations = random.sample(list(image_set.items()), 3)  # 3 pairs for simplicity
        
        # Load images into memory and display them
        self.images = [Image.open(image_set[word]).resize((100, 100)) for word, _ in self.associations]
        
        for idx, (word, _) in enumerate(self.associations):
            img = ImageTk.PhotoImage(self.images[idx])
            label = tk.Label(self.image_display_frame, image=img, text=word, compound=tk.TOP)
            label.image = img
            label.pack(side=tk.LEFT, padx=10)
        
        # Start a timer to hide images after 10 seconds
        self.after(10000, self.hide_images)  # 10 seconds

    def hide_images(self):
        # Hide the images and start the recall phase
        self.clear_game_elements()
        
        self.recall_frame = tk.Frame(self)
        self.recall_frame.pack(pady=10)
        
        instructions = tk.Label(self.recall_frame, text="Match the correct image to its word.")
        instructions.pack(pady=10)
        
        self.recall_tree = ttk.Treeview(
            self.recall_frame,
            columns=("Word"),
            show="headings",
            height=3,
        )
        
        self.recall_tree.heading("Word", text="Select the correct image for each word")
        
        for word, _ in self.associations:
            self.recall_tree.insert("", "end", values=(word,))
        
        self.recall_tree.pack(pady=10)
        
        submit_button = tk.Button(
            self.recall_frame, text="Submit", command=self.check_recall
        )
        submit_button.pack(pady=10)
    
    def check_recall(self):
        selected_items = self.recall_tree.selection()
        
        if not selected_items:
            messagebox.showerror("No selection", "Please select a word to recall its image.")
            return
        
        # Compare the correct associations with the user selections
        correct = all(
            self.recall_tree.item(item, "values")[0] == word
            for word, _ in self.associations
        )
        
        if correct:
            messagebox.showinfo("Result", "Correct! You remembered the correct associations.")
        else:
            messagebox.showerror(
                "Result", "Incorrect! Try again."
            )
        
        # Reset the game
        self.start_button.config(state=tk.NORMAL)
        self.clear_game_elements()

    def clear_game_elements(self):
        # Clear image display and recall frame
        for widget in self.image_display_frame.winfo_children():
            widget.destroy()
        
        for widget in self.recall_frame.winfo_children():
            widget.destroy()

if __name__ == "__main__":
    app = MemoryAssociationGame()
    app.mainloop()
