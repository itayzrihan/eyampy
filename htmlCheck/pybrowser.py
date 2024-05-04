import os
import customtkinter as ctk
from tkhtmlview import HTMLLabel

class HtmlViewerApp(ctk.CTk):
    def __init__(self, html_file_path):
        super().__init__()
        self.title("HTML Viewer")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        # Read the HTML file
        try:
            with open(html_file_path, 'r', encoding='utf-8') as file:
                html_content = file.read()

            # Convert relative paths to absolute paths
            base_path = os.path.dirname(html_file_path)
            # Fix href for CSS and src for JS/images
            html_content = html_content.replace('href="', f'href="{base_path}/')
            html_content = html_content.replace('src="', f'src="{base_path}/')

            html_label = HTMLLabel(self, html=html_content)
            html_label.pack(fill="both", expand=True)
        except FileNotFoundError:
            print("Error: Could not find HTML file at", html_file_path)

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.realpath(__file__))  # Directory of this script
    html_file_path = os.path.join(script_dir, "index.html")  # Absolute path to the HTML file
    
    if os.path.exists(html_file_path):
        app = HtmlViewerApp(html_file_path)
        app.mainloop()
    else:
        print("Error: HTML file not found at", html_file_path)
