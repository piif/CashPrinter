import toga
from toga.style import Pack
from toga.style.pack import COLUMN, CENTER

def button_handler(widget):
    print("Button clicked!")

def build(app):
    button = toga.Button("Click Me", on_press=button_handler)
    button.style.padding = 10

    box = toga.Box(style=Pack(direction=COLUMN, alignment=CENTER))
    box.add(button)

    return box

if __name__ == "__main__":
    app = toga.App("Hello BeeWare", "org.example.hellobeeware", startup=build)
    app.main_loop()
