import logging  # noqa # type: ignore
import re
from enum import Enum
from datetime import datetime, timedelta
from typing import Any

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.message import Message
from textual.screen import ModalScreen
from textual.widgets import Input, Label, Select, MaskedInput, ListView, Static, Footer

from model.tasks_model import Task, TaskPriority  # type: ignore
from model.config_model import Config  # type: ignore


class DateName(Enum):
    START_DATE = 'start_date'
    END_DATE = 'end_date'


class DateAdjustment(Enum):
    DECREASE = 'decrease'
    INCREASE = 'increase'


class TaskEditScreen(ModalScreen):
    """
    Popup for entering task details.

    This popup allows the user to enter a task description, select a priority,
    and specify start and end dates. It also includes a submit button to
    submit the entered data.

    Attributes:
        tuido_app: The main application instance.
        list_views: Dictionary of list views for the tasks.
        description_input: Input field for task description.
        priority_input: Dropdown for selecting task priority.
        start_date_input: Input field for start date.
        start_date_label: Label for displaying the start date.
        end_date_input: Input field for end date.
        end_date_label: Label for displaying the end date.
        invalid_inputs: Set of IDs of invalid input fields.
    """
    tuido_app: App
    list_views: dict[str, ListView | Any] = {}
    description_input: Input
    priority_input: Select
    start_date_input: MaskedInput
    start_date_weekday_label: Label
    end_date_input: MaskedInput
    end_date_weekday_label: Label
    invalid_inputs: set[str] = set()

    BINDINGS = [
        Binding(key='escape', key_display='ESC', action='close_modal',
                description='Cancel',
                tooltip='Discard changes and close the popup',
                show=False),
        Binding(key='f4', key_display='F4', action='close_modal',
                description='Cancel',
                tooltip='Discard changes and close the popup'),
        Binding(key='f5', key_display='F5', action='save',
                description='Save',
                tooltip='Save changes and close the popup'),
        Binding(key='f7', key_display='F7',
                action='decrease_start_date',
                description='Start-1',
                tooltip='Decrease the start date by 1 day'),
        Binding(key='f8', key_display='F8',
                action='increase_start_date',
                description='Start+1',
                tooltip='Increase the start date by 1 day'),
        Binding(key='f9', key_display='F9',
                action='decrease_end_date',
                description='End-1',
                tooltip='Decrease the end date by 1 day'),
        Binding(key='f10', key_display='F10',
                action='increase_end_date',
                description='End+1',
                tooltip='Increase the end date by 1 day'),
    ]


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


    def __init__(self, tuido_app: App, list_views: dict[str, ListView | Any],
                 **kwargs) -> None:
        """
        Initializes the popup with a dictionary of list views.

        Args:
            tuido_app: The main application instance.
            list_views: A dictionary containing the list views for the tasks.
        """
        super().__init__(**kwargs)
        self.tuido_app = tuido_app
        self.list_views = list_views

        self.description_input = Input(placeholder='Enter description')

        priorities = ['Low', 'Medium', 'High']
        self.priority_input = Select((option, option) for option in priorities)

        self.start_date_input = MaskedInput(
            id='start_date', template='9999-99-99;0', placeholder='YYYY-MM-DD'
        )

        self.start_date_weekday_label = Label(
            '(Wednesday)', id='task_start_date_weekday_label'
        )

        self.end_date_input = MaskedInput(
            id='end_date', template='9999-99-99;0', placeholder='YYYY-MM-DD'
        )

        self.end_date_weekday_label = Label(
            '(Wednesday)', id='task_end_date_weekday_label'
        )

    def compose(self) -> ComposeResult:
        """
        Creates the child widgets for the popup.

        This includes input fields for task description, priority, start date,
        end date, and a submit button.
        """
        with Static(id='main_container'):
            # with VerticalGroup():
            # Description
            yield Label('Description:')
            yield self.description_input

            # Priority
            yield Label('Priority:')
            yield self.priority_input

            # Start Date
            yield Label('Start Date:')
                # with HorizontalGroup():
            yield self.start_date_input
            yield self.start_date_weekday_label

            # End Date
            yield Label('End Date:')
            yield self.end_date_input
            yield self.end_date_weekday_label

            yield Footer()

    def action_close_modal(self) -> None:
        """
        Closes the modal popup without saving changes.
        """
        self.app.pop_screen()

    def action_save(self) -> None:
        """
        Saves the changes made in the popup and closes it.
        """
        self.submit_changes()
        self.app.pop_screen()

    def action_decrease_start_date(self) -> None:
        """
        Decreases the start date by 1 day.
        """
        self.adjust_date(DateName.START_DATE, DateAdjustment.DECREASE)

    def action_increase_start_date(self) -> None:
        """
        Increases the start date by 1 day.
        """
        self.adjust_date(DateName.START_DATE, DateAdjustment.INCREASE)

    def action_decrease_end_date(self) -> None:
        """
        Decreases the end date by 1 day.
        """
        self.adjust_date(DateName.END_DATE, DateAdjustment.DECREASE)

    def action_increase_end_date(self) -> None:
        """
        Increases the end date by 1 day.
        """
        self.adjust_date(DateName.END_DATE, DateAdjustment.INCREASE)

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

    def adjust_date(self, date_name: DateName, adjustment: DateAdjustment) \
    -> None:
        """
        Adjusts the date in the input field based on the provided date name
        and adjustment type.

        Args:
            date_name: The name of the date input field (start or end date).
            adjustment: The type of adjustment (increase or decrease).
        """
        # Get the input widget instance and determine the adjustment factor
        match date_name:
            case DateName.START_DATE:
                input_widget: MaskedInput = self.start_date_input
            case _:
                input_widget: MaskedInput = self.end_date_input

        if adjustment == DateAdjustment.INCREASE:
            delta_factor = 1
        else:
            delta_factor = -1

        # Adjust the date in the input field
        if input_widget.value:
            # Try to parse the date and adjust it
            try:
                date = datetime.strptime(input_widget.value, "%Y-%m-%d")
                new_date = date + timedelta(days=1) * delta_factor
                input_widget.value = new_date.strftime("%Y-%m-%d")
            except ValueError:
                pass
        else:
            # If the input is empty, set it to today's date
            input_widget.value = datetime.now().strftime("%Y-%m-%d")

        input_widget.refresh()

    def on_input_changed(self, event: Input.Changed) -> None:
        """
        Handles input change events.

        Validates the input values for start and end dates. If the input is
        valid, it removes the invalid class from the input field. If the input
        is invalid, it adds the invalid class to the input field and stores the
        input ID in the invalid_inputs set.

        Also updates the weekday labels for the start and end date inputs.

        Args:
            event: The input change event.
        """
        if event.input.id in ['start_date', 'end_date']:
            value = event.value

            if self.is_valid_date(value) or value == '':
                if event.input.id in self.invalid_inputs:
                    self.invalid_inputs.remove(event.input.id)
                event.input.remove_class('invalid_input')
            else:
                self.invalid_inputs.add(event.input.id)
                event.input.add_class('invalid_input')

            self.update_weekday_labels()
            event.input.refresh()

    def is_valid_date(self, date_str: str) -> bool:
        """
        Validates the date format.

        Checks if the date string is in the format YYYY-MM-DD and if it is a
        valid date.

        Args:
            date_str: The date string to validate.

        Returns:
            bool: True if the date string is valid, False otherwise.
        """
        # Check if the date string matches the format YYYY-MM-DD
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", date_str):
            return False

        # Check if the date string is a valid date
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except ValueError:
            return False

    def update_weekday_labels(self):
        """
        Sets the weekday labels for the start and end date inputs.

        This method updates the weekday labels based on the current values of
        the start and end date inputs.
        """
        self.start_date_weekday_label.update(
            self.get_weekday_name(self.start_date_input.value)
        )
        self.end_date_weekday_label.update(self.get_weekday_name(
            self.end_date_input.value)
        )

    def get_weekday_name(self, date_str: str) -> str:
        """
        Returns the name of the weekday for a given date string.

        Args:
            date_str: The date string in the format YYYY-MM-DD.

        Returns:
            str: The name of the weekday.
        """
        if not date_str:
            return ''

        try:
            date = datetime.strptime(date_str, "%Y-%m-%d")
            return f'({date.strftime('%A')})'
        except ValueError:
            return ''

    def submit_changes(self):
        """
        Submits the changes made in the popup.

        This method is called when the submit button is pressed. It sends a
        message with the entered data and clears the input fields.
        """
        if self.check_invalid_inputs():
            return
        else:
            self.post_message(self.Submit(
                self.description_input.value,
                self.priority_input.value,
                self.start_date_input.value,
                self.end_date_input.value
            ))

    def check_invalid_inputs(self) -> bool:
        """
        Checks if there are any invalid inputs.

        If there are invalid inputs, it shows an error message and returns
        True. Otherwise, it returns False.

        Returns:
            bool: True if there are invalid inputs, False otherwise.
        """
        if len(self.invalid_inputs) > 0:
            self.app.notify(
                'Please correct the invalid input(s) before submitting.',
                severity='error'
            )
            return True
        else:
            return False

    async def on_unmount(self, event: Message):
        """
        Called when the popup is unmounted.
        This method is currently empty but can be used to perform any cleanup
        actions when the popup is removed from the screen.
        """
        pass

    def set_list_view_state(self, enabled: bool) -> None:
        """
        Sets the state of the list views to either enabled or disabled.
        """
        for list_view in self.list_views.values():
            list_view.can_focus = enabled
            list_view.disabled = not enabled
