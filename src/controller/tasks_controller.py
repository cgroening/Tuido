import copy
import enum
import logging

from textual.app import App
from textual.widgets import ListView

from model.config_model import Config  # type: ignore
from model.tasks_model import Task, Tasks    # type: ignore
from view.main_tabs import MainTabs  # type: ignore
from view.tasks_tab_form import TasksInputPopup  # type: ignore


class TaskAction(enum.Enum):
    NEW = 'new'
    EDIT = 'edit'


class TaskMoveDirection(enum.Enum):
    LEFT = 'left'
    RIGHT = 'right'


class TasksController:
    """
    Controller for managing tasks in the application.

    This class handles the interaction between the tasks model and the
    user interface. It provides methods for displaying the task form,
    saving tasks, moving tasks between columns, and deleting tasks.

    Attributes:
        config: The configuration object.
        tasks_model: The tasks model object.
        main_tabs: The main tabs object.
        tuido_app: The main application object.
        task_action: The action to perform (new or edit).
        index_of_new_task: The index of the most recently added task
            (-1 if not applicable).
    """
    config: Config
    tasks_model: Tasks
    main_tabs: MainTabs
    tuido_app: App
    task_action: TaskAction
    index_of_new_task: int = -1

    def __init__(
        self, config: Config, tasks_model: Tasks, main_tabs: MainTabs,
        tuido_app: App
    ):
        """
        Initializes the TasksController.

        Args:
            config: The configuration object.
            tasks_model: The tasks model object.
            main_tabs: The main tabs object.
            tuido_app: The main application object.
        """
        self.config = config
        self.tasks_model = tasks_model
        self.main_tabs = main_tabs
        self.tuido_app = tuido_app

        # Set up the tasks tab with the tasks model data
        tasks_tab = self.main_tabs.tasks_tab
        tasks_tab.column_captions = self.tasks_model.column_captions
        tasks_tab.column_names = self.tasks_model.column_names
        tasks_tab.tasks = self.tasks_model.tasks

    def show_task_form(self, task_action: TaskAction) -> None:
        """
        Displays the task form for creating or editing a task.

        Args:
            task_action: The action to perform (new or edit).
        """
        self.task_action = task_action

        # Get the name of the focused list view, return if none is focused
        tasks_tab = self.main_tabs.tasks_tab
        focused_list_view_name: str | None = None

        for list_view_name, list_view in tasks_tab.list_views.items():
            if list_view.has_focus:
                focused_list_view_name = list_view_name
                break

        if focused_list_view_name is None and task_action == TaskAction.EDIT:
            return

        # Get the index of the selected task, return if none is selected
        selected_task_index = tasks_tab.list_views[focused_list_view_name].index  # type: ignore
        if selected_task_index is None and task_action == TaskAction.EDIT:
            return

        # Show the task form
        input_form = self.main_tabs.tasks_tab.input_form
        input_form.display = True
        self.tuido_app.set_focus(input_form.description_input)
        self.set_task_form_input_values()

    def set_task_form_input_values(self) -> None:
        """
        Sets the input values for the task form based on the selected task
        if the task action is `TaskAction.EDIT`.
        """
        if self.task_action == TaskAction.EDIT:
            # Get name of the active list view and index of the selected task
            tasks_tab = self.main_tabs.tasks_tab
            column_name = tasks_tab.selected_column_name
            selected_task_index = tasks_tab.selected_task_index

            # Get the selected task and set the input form values
            task = self.tasks_model.tasks[column_name][selected_task_index]
            input_form = self.main_tabs.tasks_tab.input_form
            input_form.set_input_values(task)

    def save_task(self, message: TasksInputPopup.Submit) -> None:
        """
        Saves the task data from the input form to the tasks model
        and updates the view.

        This method is called when the user submits the task form.

        Args:
            message: The message containing the task data from the input form.
        """
        tasks_model = self.tasks_model
        # Get the task data from the input form
        task_raw = {
            'description': message.description,
            'priority':    tasks_model.priority_str_to_num(message.priority),
            'start_date':  message.start_date,
            'end_date':    message.end_date
        }

        # Determine the task action which was set when the form was opened
        if self.task_action == TaskAction.NEW:
            # New tasks will always go to the first column/inbox
            column_name = self.config.task_column_names[0]
        elif self.task_action == TaskAction.EDIT:
            column_name = self.main_tabs.tasks_tab.selected_column_name
            selected_task_index = self.main_tabs.tasks_tab.selected_task_index

            # Remove edited task from the current column
            tasks_model.delete_task(column_name, selected_task_index)

        # Add new or edited task to the tasks model and refresh the list view
        tasks_list_old = copy.deepcopy(tasks_model.tasks[column_name])

        tasks_model.add_task_to_dict_from_raw_data(column_name, task_raw)
        tasks_model.save_to_file()
        self.recreate_list_view(column_name)

        tasks_list_new = tasks_model.tasks[column_name]
        self.store_index_of_new_task(tasks_list_old, tasks_list_new)

    def store_index_of_new_task(
        self, tasks_list_old: list[Task], tasks_list_new: list[Task]
    ) -> None:
        """
        Compares the old and new task lists to find the index of the new task
        and stores it in `self.index_of_new_task`.

        Args:
            tasks_list_old: The old list of tasks.
            tasks_list_new: The new list of tasks.
        """
        for i, task in enumerate(tasks_list_new):
            if len(tasks_list_old) >= i+1 and task != tasks_list_old[i]:
                self.index_of_new_task = i
                return

        self.index_of_new_task = -1

    def recreate_list_view(self, column_name: str) -> None:
        """
        Recreates the list view for the specified column name.

        Args:
            column_name: The name of the column to recreate the list view for.
        """
        # Remove all items
        tasks_tab = self.main_tabs.tasks_tab
        list_view: ListView = tasks_tab.list_views[column_name]
        list_view.clear()

        # Create a new instance of ListViewItem for each task in the column
        list_items = tasks_tab.create_list_items(column_name)
        for list_item in list_items:
            list_view.append(list_item)
        tasks_tab.set_can_focus()

    def move_task(self, move_direction: TaskMoveDirection) -> None:
        """
        Moves the selected task to the left or right column.

        Args:
            move_direction: The direction to move the task (left or right).
        """
        # Determine the index of the source column
        source_column_name = self.main_tabs.tasks_tab.selected_column_name
        column_names = self.config.task_column_names
        source_column_index = column_names.index(source_column_name)

        # Determine the index and name of the target column
        if move_direction == TaskMoveDirection.LEFT:
            target_column_index = \
                max(source_column_index - 1, 0)
        elif move_direction == TaskMoveDirection.RIGHT:
            target_column_index = \
                min(source_column_index + 1, len(column_names) - 1)

        target_column_name = self.config.task_column_names[target_column_index]

        # Abort conditions
        tasks_model = self.tasks_model
        if source_column_index == target_column_index:
            return

        if len(tasks_model.tasks[source_column_name]) == 0:
            return

        # Remove task from source column
        selected_task_index = self.main_tabs.tasks_tab.selected_task_index
        task_to_move = tasks_model.tasks[source_column_name] \
                           [selected_task_index]
        tasks_model.delete_task(source_column_name, selected_task_index)

        # Add task to target column
        task_to_move.column_name = target_column_name

        if target_column_name not in tasks_model.tasks:
            tasks_model.tasks[target_column_name] = []

        tasks_model.tasks[target_column_name].append(task_to_move)
        tasks_model.sort_tasks()
        tasks_model.save_to_file()

        # Update the source and target list views
        self.recreate_list_view(source_column_name)
        self.recreate_list_view(target_column_name)

        # Find the index of the moved task in the target column select it
        list_views: list[ListView] = self.main_tabs.tasks_tab.list_views
        target_list_view: ListView = list_views[target_column_name]

        target_task_index = 0
        for i, task in enumerate(self.tasks_model.tasks[target_column_name]):
            if task == task_to_move:
                target_task_index = i
                break

        target_list_view.index = target_task_index
        target_list_view.focus()

    def delete_selected_task(self) -> None:
        """
        Deletes the selected task from the tasks model and updates the view.
        """
        tasks_tab = self.main_tabs.tasks_tab
        column_name = tasks_tab.selected_column_name
        selected_task_index = tasks_tab.selected_task_index

        if selected_task_index is not None:
            self.tasks_model.delete_task(column_name, selected_task_index)
            self.tasks_model.save_to_file()
            self.recreate_list_view(column_name)