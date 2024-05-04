import tkinter as tk
import subprocess  # For launching other Python scripts

# Create a launcher app with 9 buttons
class NumberRecall(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Launcher")

        # Create a frame to hold the buttons
        button_frame = tk.Frame(self)
        button_frame.pack(pady=20, padx=20)

        # Button to launch RoutineApp
        launch_routine_app_button = tk.Button(button_frame, text="Launch Routinator", command=self.launch_routine_app)
        launch_routine_app_button.grid(row=0, column=0, padx=5, pady=5)

        # Placeholder buttons for future applications
        launch_renum_app_button = tk.Button(button_frame, text="Level 10", command=self.launch_renum_app)
        launch_renum_app_button.grid(row=0, column=1, padx=5, pady=5)
        for i in range(2, 9):
            placeholder_button = tk.Button(button_frame, text=f"Placeholder {i}")
            placeholder_button.grid(row=i // 3, column=i % 3, padx=5, pady=5)

    def launch_routine_app(self):
        # Launch the RoutineApp by executing the external script
        subprocess.Popen(["python", "routine_app.py"])
        
    def launch_renum_app(self):
        # Launch the ReNum app by executing the external script
        subprocess.Popen(["python", "CRLevel1.py"])

if __name__ == "__main__":
    app = NumberRecall()
    app.mainloop()
