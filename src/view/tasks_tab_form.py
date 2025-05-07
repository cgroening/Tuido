from typing import Any

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.message import Message
from textual.widgets import Button, Input, Label, Select, MaskedInput

from model.tasks_model import Task, TaskPriority  # type: ignore


class TasksInputPopup(Container):
    """
    Popup for entering task details.

    This popup allows the user to enter a task description, select a priority,
    and specify start and end dates. It also includes a submit button to
    submit the entered data.

    Attributes:
        description_input: Input field for task description.
        priority_input: Dropdown for selecting task priority.
        start_date_input: Input field for start date.
        end_date_input: Input field for end date.
    """
    description_input: Input
    priority_input: Select
    start_date_input: MaskedInput
    end_date_input: MaskedInput

    class Submit(Message):
        """
        Message to be sent when the form is submitted.
        """
        def __init__(self, description: str, priority: Any, start_date: str,
                     end_date: str) -> None:
            self.description = description
            self.priority = priority
            self.start_date = start_date
            self.end_date = end_date
            super().__init__()

    def compose(self) -> ComposeResult:
        """
        Creates the child widgets for the popup.

        This includes input fields for task description, priority, start date,
        end date, and a submit button.
        """
        # Description
        yield Label('Description:')
        self.description_input = Input(placeholder='Enter description')
        yield self.description_input

        # Priority
        yield Label('Priority:')
        priorities = ['Low', 'Medium', 'High']
        self.priority_input = Select((option, option) for option in priorities)
        yield self.priority_input

        # Start Date
        yield Label('Start Date:')
        self.start_date_input = MaskedInput(template='9999-99-99;0',
                                            placeholder='YYYY-MM-DD')
        yield self.start_date_input

        # End Date
        yield Label('End Date:')
        self.end_date_input = MaskedInput(template='9999-99-99;0',
                                          placeholder='YYYY-MM-DD')
        yield self.end_date_input

        # with Vertical():
        with Horizontal():
            yield Button('Today', id='today')
            yield Button('Tomorrow', id='tomorrow')

        # Submit and Cancel Button
        with Horizontal():
            yield Button('Submit', id='submit')
            yield Button('Cancel', id='cancel')

    def set_input_values(self, task: Task):
        """
        Sets the input values in the popup based on the provided task.

        Args:
            task: The task object containing the values to be set.
        """
        self.description_input.value = task.description

        match task.priority:
            case TaskPriority.HIGH:
                task_priority = 'High'
            case TaskPriority.MEDIUM:
                task_priority = 'Medium'
            case _:
                task_priority = 'Low'
        self.priority_input.value = task_priority

        self.start_date_input.value = task.start_date
        self.end_date_input.value = task.end_date

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """
        Handles button press events.

        If the submit button is pressed, it sends a message with the entered
        data and clears the input fields.
        """
        if event.button.id == 'submit':
            # Send a message with the entered data
            self.post_message(self.Submit(
                self.description_input.value,
                self.priority_input.value,
                self.start_date_input.value,
                self.end_date_input.value
            ))

            # Clear input fields
            self.description_input.value = ''
            self.priority_input.clear()
            self.start_date_input.value = ''
            self.end_date_input.value = ''

            # Hide the popup
            self.display = False
