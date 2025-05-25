from textual.app import ComposeResult
from textual.containers import Grid, Horizontal, Vertical
from textual.screen import Screen, ModalScreen
from textual.widgets import Button, Label
from textual import on


# class QuestionScreen(Screen[bool]):
class QuestionScreen(ModalScreen[bool]):
    """
    A screen that asks a question and returns the answer as a boolean value.
    """
    BINDINGS = [
        ('escape', 'close_modal', 'Close'),
    ]


    def __init__(self, question: str) -> None:
        """
        Initialize the QuestionScreen with a question.
        """
        self.question = question
        super().__init__()

    def compose(self) -> ComposeResult:
        """
        Compose the screen layout.
        """
        yield Grid(
            Label(self.question, id='question'),
            Button('Yes', variant='error', id='yes'),
            Button('No', variant='primary', id='no'),
            id='dialog',
        )

    def action_close_modal(self) -> None:
        """
        Closes the modal popup.
        """
        self.app.pop_screen()

    @on(Button.Pressed, '#yes')
    def handle_yes(self) -> None:
        """
        Handle the "Yes" button press.
        """
        self.dismiss(True)

    @on(Button.Pressed, '#no')
    def handle_no(self) -> None:
        """
        Handle the "No" button press.
        """
        self.dismiss(False)
