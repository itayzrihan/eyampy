import tkinter as tk
import subprocess  # For launching other Python scripts
import customtkinter as ctk

# Create a launcher app with 9 buttons
class LauncherApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Launcher")
        
        ctk.set_appearance_mode("dark")  # Set to system theme (light or dark)
        ctk.set_default_color_theme("dark-blue")  # Set the default theme
        # Create a label to display the title
        title_label = ctk.CTkLabel(self, text="Welcome to the Launcher App", font=("Arial", 24))
        title_label.pack(pady=20)
        
        # Create a label to display the description
        description_label = ctk.CTkLabel(self, text="Select an application to launch", font=("Arial", 16))
        description_label.pack(pady=10)
        
        
        # Create a frame to hold the buttons
        button_frame = ctk.CTkFrame(self)
        button_frame.pack(pady=20, padx=20)

        # Button to launch RoutineApp
        launch_routine_app_button = ctk.CTkButton(button_frame, text="Launch Routinator", command=self.launch_routine_app)
        launch_routine_app_button.grid(row=0, column=0, padx=5, pady=5)

        # Placeholder buttons for future applications
        launch_renum_app_button = ctk.CTkButton(button_frame, text="Launch ReNum", command=self.launch_renum_app)
        launch_renum_app_button.grid(row=0, column=1, padx=5, pady=5)
        
                # Placeholder buttons for future applications
        launch_recard_app_button = ctk.CTkButton(button_frame, text="Launch ReCard", command=self.launch_recard_app)
        launch_recard_app_button.grid(row=0, column=2, padx=5, pady=5)
        
        launch_Money_app_button = ctk.CTkButton(button_frame, text="Launch Money", command=self.launch_Money_app)
        launch_Money_app_button.grid(row=1, column=0, padx=5, pady=5)

        launch_MemoryPalace_app_button = ctk.CTkButton(button_frame, text="Launch MemoryPalace", command=self.launch_MemoryPalace_app)
        launch_MemoryPalace_app_button.grid(row=1, column=1, padx=5, pady=5)
        
        launch_MemoryAssociation_app_button = ctk.CTkButton(button_frame, text="Launch MemoryAssociation", command=self.launch_MemoryAssociation_app)
        launch_MemoryAssociation_app_button.grid(row=1, column=2, padx=5, pady=5)
        
        launch_calen_app_button = ctk.CTkButton(button_frame, text="Launch calen", command=self.launch_calen_app)
        launch_calen_app_button.grid(row=2, column=0, padx=5, pady=5)
        
        launch_Goals_app_button = ctk.CTkButton(button_frame, text="Launch Goals", command=self.launch_Goals_app)
        launch_Goals_app_button.grid(row=2, column=1, padx=5, pady=5)
        
        launch_maze_app_button = ctk.CTkButton(button_frame, text="Launch maze", command=self.launch_maze_app)
        launch_maze_app_button.grid(row=2, column=1, padx=5, pady=5)

        launch_maple_app_button = ctk.CTkButton(button_frame, text="Launch maple", command=self.launch_maple_app)
        launch_maple_app_button.grid(row=2, column=2, padx=5, pady=5)

        launch_secretnumbers_app_button = ctk.CTkButton(button_frame, text="Launch secret numbers", command=self.launch_secretnumbers_app)
        launch_secretnumbers_app_button.grid(row=3, column=0, padx=5, pady=5)
        
        launch_secretletters_app_button = ctk.CTkButton(button_frame, text="Launch secret letters", command=self.launch_secretletters_app)  
        launch_secretletters_app_button.grid(row=3, column=1, padx=5, pady=5)
        
        launch_cardcollection_app_button = ctk.CTkButton(button_frame, text="Launch card collection", command=self.launch_cardcollection_app)   
        launch_cardcollection_app_button.grid(row=3, column=2, padx=5, pady=5)
        
        launch_recipt_app_button = ctk.CTkButton(button_frame, text="Launch receipt", command=self.launch_receipt_app)
        launch_recipt_app_button.grid(row=4, column=0, padx=5, pady=5)
        
        launch_html_viewer_app_button = ctk.CTkButton(button_frame, text="Launch html viewer", command=self.launch_html_viewer_app)
        launch_html_viewer_app_button.grid(row=4, column=1, padx=5, pady=5)
        
        launch_notification_app_button = ctk.CTkButton(button_frame, text="Launch notification", command=self.launch_notification_app)
        launch_notification_app_button.grid(row=4, column=2, padx=5, pady=5)
        
    def launch_routine_app(self):
        # Launch the RoutineApp by executing the external script
        subprocess.Popen(["python", "Routine/routine_app.py"])
        
    def launch_renum_app(self):
        # Launch the ReNum app by executing the external script
        subprocess.Popen(["python", "NumberRecall.py"])
        
    def launch_recard_app(self):
        # Launch the ReCard app by executing the external script
        subprocess.Popen(["python", "CardRecall.py"])

    def launch_Money_app(self):
        # Launch the Money app by executing the external script
        subprocess.Popen(["python", "Money.py"])
    
    def launch_MemoryPalace_app(self):
        # Launch the MemoryPalace app by executing the external script
        subprocess.Popen(["python", "MemoryPalace.py"])
    
    def launch_MemoryAssociation_app(self):
        # Launch the MemoryAssociation app by executing the external script
        subprocess.Popen(["python", "MemoryAssociation.py"])
        
    def launch_calen_app(self):
        # Launch the calen app by executing the external script
        subprocess.Popen(["python", "calen.py"])

    def launch_Goals_app(self):
        # Launch the Goals app by executing the external script
        subprocess.Popen(["python", "Goals.py"])        
    
    def launch_maze_app(self):
        # Launch the maze app by executing the external script
        subprocess.Popen(["python", "maze.py"])
        
    def launch_maple_app(self): 
        # Launch the maple app by executing the external script
        subprocess.Popen(["python", "PyMaple/game.py"])
        
    def launch_secretnumbers_app(self):
        # Launch the secret numbers app by executing the external script
        subprocess.Popen(["python", "SecretNumbers/app.py"])
        
    def launch_secretletters_app(self):
        # Launch the secret letters app by executing the external script
        subprocess.Popen(["python", "secret_letters.py"])
    
    def launch_cardcollection_app(self):
        # Launch the card collection app by executing the external script
        subprocess.Popen(["python", "card_collection.py"])
    
    def launch_receipt_app(self):
        # Launch the receipt app by executing the external script
        subprocess.Popen(["python", "Receipt.py"])
    
    def launch_html_viewer_app(self):
        # Launch the HtmlViewerApp script
        subprocess.Popen(["python", "htmlCheck/pybrowser.py"])
        
    def launch_notification_app(self):
        # Launch the notification app by executing the external script
        subprocess.Popen(["python", "notifications.py"])
        
if __name__ == "__main__":
    app = LauncherApp()
    app.mainloop()
