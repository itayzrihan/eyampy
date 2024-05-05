from kivy.app import App
from kivy.uix.label import Label

class HelloWorldApp(App):
    def build(self):
        # Return a Label widget with text 'Hello, World!'
        return Label(text='Hello, World!')

if __name__ == '__main__':
    HelloWorldApp().run()
