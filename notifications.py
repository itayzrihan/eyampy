import customtkinter as ctk
from plyer import notification
import threading
import sqlite3
import subprocess
import signal
import time
from pathlib import Path
from IPython.display import Audio



import speech_recognition as sr
import pyttsx3
import os
from dotenv import load_dotenv
import openai



load_dotenv()
OPENAI_KEY = os.getenv('OPENAI_KEY')
openai.api_key = OPENAI_KEY

# Initialize text-to-speech engine
engine = pyttsx3.init()
recognizer = sr.Recognizer()


def run_model(text, output_wav_path):
    call_tts_string = f"""tts --text "{text}" \
        --model_path {model_pth_path} \
        --config_path {model_config_path} \
        --vocoder_path {vocoder_pth_path} \
        --vocoder_config_path {vocoder_config_path} \
        --out_path "{output_wav_path}" """
    try:
        print(call_tts_string)
        p = subprocess.Popen(['bash', '-c', call_tts_string],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True)
        # throw an exception if the called process exited with an error
        stdout, stderr = p.communicate(timeout=60)
        print(stdout.decode('utf-8'))
        print(stderr.decode('utf-8'))
    except subprocess.TimeoutExpired as e:
        print(f'Timeout for {call_tts_string} (60s) expired', file=sys.stderr)
        print('Terminating the whole process group...', file=sys.stderr)
        os.killpg(os.getpgid(p.pid), signal.SIGTERM)


def save_reminder(message, interval):
    conn = sqlite3.connect('reminders.db')
    c = conn.cursor()
    c.execute('INSERT INTO reminders (message, interval) VALUES (?, ?)', (message, interval))
    conn.commit()
    conn.close()



# Database setup
def init_db():
    conn = sqlite3.connect('reminders.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS reminders (
            id INTEGER PRIMARY KEY,
            message TEXT NOT NULL,
            interval INTEGER NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Load reminders from the database
def load_reminders():
    conn = sqlite3.connect('reminders.db')
    c = conn.cursor()
    c.execute('SELECT id, message, interval FROM reminders')
    reminders = c.fetchall()
    conn.close()
    return reminders

def save_new_reminder(self, message, interval, window):
    try:
        interval_float = float(interval)  # Convert the interval to a float
        self.save_reminder(message, interval_float)
        self.update_reminder_list()
        window.destroy()
    except ValueError:
        print("Invalid interval. Please enter a valid number.")


class DesktopNotifierApp(ctk.CTk):
    WIDTH = 800
    HEIGHT = 600

    def __init__(self):
        super().__init__()
        self.title("Desktop Notifier")
        self.geometry(f"{self.WIDTH}x{self.HEIGHT}")
        self.reminders = {}
        init_db()
        self.setup_ui()
        self.start_reminder_thread()
        
        # Configure text-to-speech engine
        self.configure_tts()

        
    def configure_tts(self):
        engine.setProperty('rate', 150)
        zira_voice_id = "HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Speech\\Voices\\Tokens\\TTS_MS_EN-US_ZIRA_11.0"
        engine.setProperty('voice', zira_voice_id)


    def setup_ui(self):
        self.frame = ctk.CTkFrame(master=self, corner_radius=10)
        self.frame.pack(pady=20, padx=20, fill="both", expand=True)

        self.title_label = ctk.CTkLabel(master=self.frame, text="Desktop Notifier", font=("Roboto Medium", 16))
        self.title_label.pack(pady=12)

        self.reminders_frame = ctk.CTkFrame(master=self.frame)
        self.reminders_frame.pack(pady=20, fill="both", expand=True)
        self.update_reminder_list()

        self.new_reminder_button = ctk.CTkButton(master=self.frame, text="Add New Reminder", command=self.add_new_reminder)
        self.new_reminder_button.pack(pady=12)
        
    def start_listening(self):
        threading.Thread(target=self.handle_speech, daemon=True).start()

    def handle_speech(self):
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source)
            try:
                text = recognizer.recognize_google(audio)
                self.text_box.set(text)
                response = self.send_to_chatGPT(text)
                engine.say(response)
                engine.runAndWait()
            except sr.UnknownValueError:
                engine.say("Sorry, I did not understand that.")
                engine.runAndWait()
            except sr.RequestError:
                engine.say("API request failed.")
                engine.runAndWait()

    def send_to_chatGPT(self, text):
        response = openai.ChatCompletion.create(
            messages=[{"role": "user", "content": text}],
            model="gpt-3.5-turbo",
            max_tokens=150
        )
        return response.choices[0].message['content']


    def update_reminder_list(self):
        for widget in self.reminders_frame.winfo_children():
            widget.destroy()
        reminders = load_reminders()
        for reminder in reminders:
            label = ctk.CTkLabel(master=self.reminders_frame, text=f"{reminder[1]} - Every {reminder[2]} minutes", font=("Roboto", 12))
            label.pack()
            self.reminders[reminder[0]] = [label, reminder[1], reminder[2], time.time()]

    def add_new_reminder(self):
        new_window = ctk.CTkToplevel(self)
        new_window.title("Add New Reminder")
        label = ctk.CTkLabel(master=new_window, text="Enter Reminder Details (interval in minutes, e.g., 0.5 for 30 seconds)", font=("Roboto", 14))
        label.pack(pady=20)
        message_entry = ctk.CTkEntry(master=new_window, placeholder_text="Reminder message")
        message_entry.pack(pady=12)
        interval_entry = ctk.CTkEntry(master=new_window, placeholder_text="Interval in minutes")
        interval_entry.pack(pady=12)
        submit_button = ctk.CTkButton(master=new_window, text="Submit", command=lambda: self.save_new_reminder(message_entry.get(), interval_entry.get(), new_window))
        submit_button.pack(pady=20)

    def save_new_reminder(self, message, interval, window):
        save_reminder(message, int(interval))
        self.update_reminder_list()
        window.destroy()

    def start_reminder_thread(self):
        threading.Thread(target=self.run_notifier, daemon=True).start()

    def run_notifier(self):
        while True:
            time.sleep(1)
            current_time = time.time()
            for reminder_id, details in list(self.reminders.items()):
                label, message, interval, start_time = details
                elapsed = current_time - start_time
                remaining = interval * 60 - elapsed  # Convert interval to seconds
                if remaining <= 0:
                    self.notify(message)
                    self.reminders[reminder_id][3] = current_time  # reset timer
                minutes, seconds = divmod(int(remaining), 60)
                if remaining < 60:
                    self.update_label(label, f"{message} - Next in {int(remaining)}s")
                else:
                    self.update_label(label, f"{message} - Next in {minutes}m {seconds}s")

    def update_label(self, label, text):
        if self.winfo_exists():  # Check if the main window exists
            label.configure(text=text)

    def notify(self, message):
        notification.notify(title="Reminder", message=message, timeout=10)
        engine.say(message)
        engine.runAndWait()

    def on_closing(self):
        self.destroy()

if __name__ == "__main__":
    app = DesktopNotifierApp()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()