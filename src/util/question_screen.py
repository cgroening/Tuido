from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, Label
from textual import on


class QuestionScreen(Screen[bool]):
    """
    A screen that asks a question and returns the answer as a boolean value.
    """

    CSS = """
    QuestionScreen {
        align: center middle;
        content-align: center middle;
    }

    .question-container {
        align: center middle;
        height: auto;
        padding-top: 3;
        width: auto;
    }

    .question-label {
        content-align: center middle;
        margin-bottom: 1;
        text-align: center;
        width: 100%;
    }

    .button-container {
        align-horizontal: center;
        margin-top: 1;
        width: auto;
    }
    """

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
        with Vertical(classes="question-container"):
            yield Label(self.question, classes="question-label")
            with Horizontal(classes="button-container"):
                yield Button('Yes', id='yes', variant='success')
                yield Button('No', id='no')

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
