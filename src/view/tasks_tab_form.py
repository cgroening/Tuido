import logging  # noqa # type: ignore
import re
import asyncio
from enum import Enum
from datetime import datetime, timedelta
from typing import Any

from textual.app import App, ComposeResult
from textual.containers import Container
from textual.message import Message
from textual.widgets import Button, Input, Label, Select, MaskedInput, ListView

from model.tasks_model import Task, TaskPriority  # type: ignore
from model.config_model import Config  # type: ignore


class DateName(Enum):
    START_DATE = 'start_date'
    END_DATE = 'end_date'


class DateAdjustment(Enum):
    DECREASE = 'decrease'
    INCREASE = 'increase'


class TasksInputPopup(Container):
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
        end_date_input: Input field for end date.
        invalid_inputs: Set of IDs of invalid input fields.
    """
    tuido_app: App
    list_views: dict[str, ListView | Any] = {}
    description_input: Input
    priority_input: Select
    start_date_input: MaskedInput
    end_date_input: MaskedInput
    invalid_inputs: set[str] = set()


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
            list_views: A dictionary containing the list views for the tasks.
        """
        super().__init__(**kwargs)
        self.tuido_app = tuido_app
        self.list_views = list_views

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
        self.start_date_input = MaskedInput(
            id='start_date', template='9999-99-99;0', placeholder='YYYY-MM-DD'
        )
        yield self.start_date_input

        # End Date
        yield Label('End Date:')
        self.end_date_input = MaskedInput(
            id='end_date', template='9999-99-99;0', placeholder='YYYY-MM-DD'
        )
        yield self.end_date_input

        # Submit and Cancel Button
        # TODO: Remove the commented code below if no one misses the buttons
        # with Horizontal():
        #     yield Button('Cancel', id='cancel', variant='error')
        #     yield Label('  ')  # Spacer
        #     yield Button('Submit', id='submit', variant='success')

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

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """
        Handles button press events.

        If the submit button is pressed, it sends a message with the entered
        data and clears the input fields.
        """
        if event.button.id == 'submit':
            # Send a message with the entered data
            self.submit_changes()

        if event.button.id == 'cancel':
            self.clear_and_hide()

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

            self.clear_and_hide()

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

    def clear_and_hide(self):
        """
        Clears the input fields and hides the popup.
        """
        # Clear input fields
        self.description_input.value = ''
        self.priority_input.clear()
        self.start_date_input.value = ''
        self.end_date_input.value = ''

        # Hide the popup
        self.display = False
        # self.set_list_view_state(enabled=True)
        # self.reselect_list_view_item()

    def on_show(self):
        """
        Called when the popup is shown.

        Sets the flag "popup_visible" in the main application instance and makes
        the list views not focusable.
        """
        self.tuido_app.popup_name = 'edit'        # type: ignore
        self.tuido_app.footer.refresh_bindings()  # type: ignore
        self.set_list_view_state(enabled=False)

    async def on_hide(self):
        """
        Called when the popup is hidden.

        Sets the flag "popup_visible" in the main application instance and makes
        the list views focusable again.
        """
        self.tuido_app.popup_name = None          # type: ignore
        self.tuido_app.footer.refresh_bindings()  # type: ignore

        self.set_list_view_state(enabled=True)
        await self.reselect_list_view_item()

    def set_list_view_state(self, enabled: bool) -> None:
        """
        Sets the state of the list views to either enabled or disabled.
        """
        for list_view in self.list_views.values():
            list_view.can_focus = enabled
            list_view.disabled = not enabled

    async def reselect_list_view_item(self) -> None:
        """
        Re-selects the item in the list view that was selected before the popup
        was shown.
        """
        config: Config = Config.instance                    # type: ignore
        tasks_controller = self.tuido_app.tasks_controller  # type: ignore
        tasks_tab = self.tuido_app.main_tabs.tasks_tab      # type: ignore

        # Get the name of the list view to be focused and the index of the
        # task to be selected based on the task action (new or edit)
        if tasks_controller.task_action.value == 'new':
            list_view_name = config.task_column_names[0]
            task_index = tasks_controller.index_of_new_task
        else:
            list_view_name = tasks_tab.selected_column_name
            task_index = tasks_tab.selected_task_index

        # Get the list view instance and set its state to enabled
        list_view = tasks_tab.list_views[list_view_name]
        list_view.can_focus = True
        list_view.disabled = False

        # Set the selected index and focus the list view
        await self.focus_listview(list_view, task_index)

    async def focus_listview(self, list_view: ListView, selected_index: int) \
    -> None:
        """
        Focuses the specified list view and selects the specified index.
        Args:
            list_view: The list view to be focused.
            selected_index: The index of the item to be selected.
        """
        await asyncio.sleep(0.05)  # Wait for the UI to update
        list_view.index = selected_index
        list_view.focus()
        list_view.refresh()
