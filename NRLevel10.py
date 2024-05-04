import tkinter as tk
from tkinter import messagebox
import random
import time
import threading

class MemoryGame(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Memory Game")
        
        self.numbers_to_recall = []
        self.display_duration = 15  # 15 seconds for displaying numbers
        self.total_groups = 6  # 6 groups of 3 numbers each
        self.group_size = 3  # Each group has 3 numbers
        
        self.intro_label = tk.Label(self, text="Welcome to the Memory Game!")
        self.intro_label.pack(pady=10)
        
        self.start_button = tk.Button(self, text="Start Game", command=self.start_game)
        self.start_button.pack(pady=10)
        
        self.result_label = tk.Label(self, text="")
        self.result_label.pack(pady=10)
        
        self.user_input = tk.Entry(self, state=tk.DISABLED)
        self.user_input.pack(pady=10)
        
        self.submit_button = tk.Button(
            self, text="Submit Answers", state=tk.DISABLED, command=self.check_answers
        )
        self.submit_button.pack(pady=10)
    
    def start_game(self):
        # Disable the start button while the game is running
        self.start_button.config(state=tk.DISABLED)
        
        # Reset the numbers to recall
        self.numbers_to_recall = []
        
        # Clear the previous results
        self.result_label.config(text="")
        
        # Start a new thread to show the numbers
        threading.Thread(target=self.show_numbers).start()

    def show_numbers(self):
        # Generate and display 6 groups of 3 random numbers each
        for _ in range(self.total_groups):
            group = [random.randint(1, 9) for _ in range(self.group_size)]
            self.numbers_to_recall.append(group)
            
            # Display the group
            self.result_label.config(text=" ".join(map(str, group)))
            
            # Wait for a short period before showing the next group
            time.sleep(2.5)  # Adjust as needed to fit the 15 seconds

        # After showing all numbers, enable the user input field
        self.user_input.config(state=tk.NORMAL)
        self.submit_button.config(state=tk.NORMAL)
        
        # Reset the result label
        self.result_label.config(text="Enter the numbers shown:")
    
    def check_answers(self):
        # Get the user's input and compare it with the expected results
        user_input = self.user_input.get().strip()
        
        # Reformat the expected numbers to a single line of space-separated numbers
        expected_output = " ".join(" ".join(map(str, group)) for group in self.numbers_to_recall)
        
        if user_input == expected_output:
            self.result_label.config(text="Correct! Well done!")
        else:
            self.result_label.config(text=f"Incorrect! The correct answer was: {expected_output}")
        
        # Reset input field and disable buttons after the check
        self.user_input.delete(0, tk.END)
        self.user_input.config(state=tk.DISABLED)
        self.submit_button.config(state=tk.DISABLED)
        self.start_button.config(state=tk.NORMAL)

if __name__ == "__main__":
    app = MemoryGame()
    app.mainloop()
