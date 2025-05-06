from textual.app import App, ComposeResult
from textual.widgets import Button, Input, Label
from textual.containers import Container, Vertical
from textual.message import Message

class InputPopup(Container):
    class Submit(Message):
        def __init__(self, name: str, email: str) -> None:
            self.name = name
            self.email = email
            super().__init__()

    def compose(self) -> ComposeResult:
        yield Label("Name:")
        self.name_input = Input(placeholder="Name eingeben")
        yield self.name_input
        yield Label("E-Mail:")
        self.email_input = Input(placeholder="E-Mail eingeben")
        yield self.email_input
        yield Button("Senden", id="submit")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "submit":
            self.post_message(self.Submit(self.name_input.value, self.email_input.value))
            self.display = False  # Popup ausblenden

class MyApp(App):
    CSS = """
    InputPopup {
        background: $background;
        padding: 2;
        border: round $secondary;
        width: 50%;
        height: auto;
        dock: top;
        layer: popup;
        align: center middle;
    }
    """

    def compose(self) -> ComposeResult:
        yield Button("Öffne Popup", id="open")
        self.popup = InputPopup()
        self.popup.display = False
        yield self.popup

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "open":
            self.popup.display = True
            self.set_focus(self.popup.name_input)

    def on_input_popup_submit(self, message: InputPopup.Submit) -> None:
        # Hier könntest du die Daten weiterverarbeiten
        self.console.log(f"Name: {message.name}, Email: {message.email}")

MyApp().run()