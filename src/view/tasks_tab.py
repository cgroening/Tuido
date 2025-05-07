from __future__ import annotations
import logging

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.events import Key, Focus, Blur
from textual.reactive import reactive
from textual.widgets import Static, ListView, ListItem, Label

from rich.padding import Padding
from rich.text import Text

from model.tasks_model import Task, TaskPriority
from view.tasks_tab_form import TasksInputPopup  # Import the TasksTab_Form class


class CustomListView(ListView):
    """
    Custom ListView that scrolls the parent container (`VerticalScroll`).

    Normally, the ListView should be scrollable by itself, but it doesn't work
    as expected in this application. So this custom ListView that scrolls the
    parent container is used instead.

    This is a workaround until the ListView is fixed.

    Attributes:
        vertical_scroll: The parent container that is scrolled.
        tasks_tab: The TasksTab object that contains the list of tasks.
        column_name: The name of the column the ListView belongs to.
    """
    vertical_scroll: VerticalScroll
    tasks_tab: TasksTab
    column_name: str


    def __init__(self, vertical_scroll: VerticalScroll, tasks_tab: TasksTab,
                 column_name: str, *args, **kwargs):
        """
        Initializes the CustomListView.

        Args:
            vscroll: The parent container that is scrolled.
            *args: Positional arguments for the ListView.
            **kwargs: Keyword arguments for the ListView.
        """
        super().__init__(*args, **kwargs)
        self.vertical_scroll = vertical_scroll
        self.vertical_scroll.can_focus = False
        self.tasks_tab = tasks_tab
        self.column_name = column_name

    async def on_key(self, event: Key) -> None:
        """
        Handles key events for the ListView.

        This method is called when a key event occurs. If the key is 'up' or
        'down', the parent container is scrolled accordingly to maintain the
        current item in view.

        Args:
            event: The key event that occurred.
        """
        # Get index of the currently selected item
        index = self.index or 0
        if event.key == 'up':
            index = max(0, index - 1)
        elif event.key == 'down':
            index = min(len(self.children) - 1, index + 1)
        else:
            return

        # Get the item at the new index and scroll to it
        item = self.children[index]
        self.vertical_scroll.scroll_to_widget(item)
        self.change_class(index)
        self.tasks_tab.selected_column_name = self.column_name
        self.tasks_tab.selected_task_index = index or 0


    def change_class(self, index: int) -> None:
        """
        Changes the class of the currently selected item.

        This method is called to update the class of the currently selected item
        in the ListView. It removes the 'selected' class from all items and adds
        'selected' class to the currently selected item.
        """
        for i, item in enumerate(self.children):
            if isinstance(item, ListItem):
                if i == index:
                    item.add_class('selected')
                else:
                    item.remove_class('selected')

    def on_focus(self, event: Focus) -> None:
        """
        Handles the focus event for the ListView.

        This method is called when the ListView gains focus. It adds
        the 'selected' class to the currently selected item and removes it
        from all other items.
        """
        for item in self.children:
            item.remove_class('selected')

        self.change_class(self.index or 0)
        self.tasks_tab.selected_column_name = self.column_name
        self.tasks_tab.selected_task_index = self.index or 0

    def on_blur(self, event: Blur) -> None:
        """
        Handles the blur event for the ListView.

        This method is called when the ListView loses focus. It removes the
        'selected' class from all items to indicate that no item is currently
        selected.
        """
        for item in self.children:
            item.remove_class('selected')

    async def on_list_view_selected(self, event: ListView.Selected):
        """
        Handles the selection event for the ListView.

        This method is called when an item in the ListView is selected with
        the cursor. It adds  the 'selected' class to the currently selected
        item and removes it from all other items.
        """
        for item in self.children:
            item.remove_class('selected')

        event.item.add_class('selected')
        self.tasks_tab.selected_column_name = self.column_name
        self.tasks_tab.selected_task_index = self.index or 0


class TasksTab(Static):
    """
    Tasks tab content.

    This class is used to display the tasks in a tabular format. Each column
    represents a different task category, and each row represents a task.

    The tasks are displayed in a list format, with the task description,
    start date, and end date shown. The tasks are color-coded based on their
    priority and the number of days until the start date and end date.

    The class uses the `CustomListView` to display the tasks in a scrollable
    list format. The `CustomListView` is a subclass of `ListView` that scrolls
    its parent container (`VerticalScroll`) instead of scrolling itself.

    Attributes:
        list_views: A dictionary of CustomListView objects for each column.
        column_names: A list of column names.
        column_captions: A dictionary mapping column names to their captions.
        tasks: A dictionary mapping column names to lists of Task objects.
        input_form: The input form for adding or editing tasks.
        selected_column_name: The name of the currently selected column.
        selected_task_index: The index of the currently selected task.
    """
    list_views: dict[str, CustomListView] = {}
    column_names: list[str]
    column_captions: dict[str, str]
    tasks: dict[str, list[Task]]
    input_form: TasksInputPopup
    selected_column_name: str
    selected_task_index: int


    def compose(self) -> ComposeResult:
        """
        Composes the tasks tab content.
        """
        with Horizontal():
            for column_name in self.column_names:
                list_items = self.create_list_items(column_name)

                with Vertical():
                    # Header for the column
                    text = Text(f'{self.column_captions[column_name]}:',
                                style='bold underline')
                    yield(Label(text, classes='task_column_header'))

                    # ListView for the column
                    vertical_scroll = VerticalScroll()
                    with vertical_scroll:
                        list_view = CustomListView(vertical_scroll, self,
                                                   column_name, *list_items)
                        self.list_views[column_name] = list_view
                        yield list_view

        self.input_form = TasksInputPopup(id='tasks-input-popup')
        self.input_form.display = False
        yield self.input_form

    def create_list_items(self, column_name: str) -> list[ListItem]:
        # Return empty list if the column doesn't have any tasks
        list_items: list[ListItem] = []
        if column_name not in self.tasks.keys():
            return list_items

        # Create a ListItem for each task
        for task in self.tasks[column_name]:
            start_date_text, start_date_style = \
                self.start_date_text_and_style(task)
            end_date_text, end_date_style = self.end_date_text_and_style(task)

            list_item = ListItem(
                    Static(Text(task.description, style='bold')),
                    Static(),
                    Static(Text('↑' + start_date_text, style=start_date_style)),
                    Static(Text('↓' + end_date_text, style=end_date_style)),
            )

            self.set_priority_class(list_item, task)
            list_items.append(list_item)

        return list_items

    def start_date_text_and_style(self, task: Task) -> tuple[str, str]:
        """
        Returns the text and style for the start date of a task.

        The date text is formatted as "YYYY-MM-DD (x d)" where x is the
        number of days until the start date.

        The style is determined based on the number of days until the date:
            - Green: if the date is in the future (x > 0)
            - Yellow: if the date is today (x = 0)
            - Red: if the start date is in the past (x < 0) and end date is in the past, too.

        If the date is not set, it returns '---' as the text and an empty style.

        Args:
            task: The task object.
        """
        start_date_text = ' ---'
        start_date_style = ''

        if task.start_date is not None and task.start_date != '':
            start_date_text = f'{task.start_date} ({task.days_to_start} d)'

            if task.days_to_start > 0:
                start_date_style = 'green'
            elif task.days_to_start < 0 and task.days_to_end < 0:
                start_date_style = 'red'
            elif task.days_to_start <= 0:
                start_date_style = 'yellow'

        return start_date_text, start_date_style

    def end_date_text_and_style(self, task: Task) -> tuple[str, str]:
        """
        Returns the text and style for the end date of a task.

        The date text is formatted as "YYYY-MM-DD (x d)" where x is the
        number of days until the end date.

        The style is determined based on the number of days until the date:
            - Green: if the date is in the future (x > 0)
            - Yellow: if the date is today (x = 0)
            - Red: if the date is in the past (x < 0)

        If the date is not set, it returns '---' as the text and an empty style.

        Args:
            task: The task object.
        """
        end_date_text = ' ---'
        end_date_style = ''

        if task.end_date is not None and task.end_date != '':
            end_date_text = f'{task.end_date} ({task.days_to_end} d)'

            if task.days_to_end > 0:
                end_date_style = 'green'
            elif task.days_to_end == 0:
                end_date_style = 'yellow'
            elif task.days_to_end < 0:
                end_date_style = 'red'

        return end_date_text, end_date_style

    def set_priority_class(self, list_item: ListItem, task: Task) -> None:
        """
        Sets the class for the ListItem based on the task's priority.

        The class is used to color-code the task based on its priority:
            - High priority: 'task_prio_high'
            - Medium priority: 'task_prio_medium'
            - Low priority: 'task_prio_low'

        Args:
            list_item: The ListItem to set the class for.
            task: The task object.
        """
        match task.priority:
            case TaskPriority.HIGH:
                list_item.add_class('task_prio_high')
            case TaskPriority.MEDIUM:
                list_item.add_class('task_prio_medium')
            case _:
                list_item.add_class('task_prio_low')