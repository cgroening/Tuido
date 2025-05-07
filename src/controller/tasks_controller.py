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
    config: Config
    tasks_model: Tasks
    main_tabs: MainTabs
    app: App
    task_action: TaskAction

    def __init__(self, config: Config, tasks_model: Tasks, main_tabs: MainTabs, app: App):
        """
        Initializes the TasksController.

        Args:
            config: The configuration object.
            tasks_model: The tasks model object.
            main_tabs: The main tabs object.
            app: The main application object.
        """
        self.config = config
        self.tasks_model = tasks_model
        self.main_tabs = main_tabs
        self.app = app

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

        input_form = self.main_tabs.tasks_tab.input_form
        input_form.display = True
        self.app.set_focus(input_form.description_input)

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
        logging.info('Saving task:')
        logging.info(f'Saving task: {message.description}')
        logging.info(f'Saving task: {message.priority}')
        logging.info(f'Saving task: {message.start_date}')
        logging.info(f'Saving task: {message.end_date}')

        # model
        task_raw = {
            'description': message.description,
            'priority':    self.tasks_model.priority_str_to_num(message.priority),
            'start_date':  message.start_date,
            'end_date':    message.end_date
        }

        if self.task_action == TaskAction.NEW:
            column_name = self.config.task_column_names[0]

        elif self.task_action == TaskAction.EDIT:

            column_name = self.main_tabs.tasks_tab.selected_column_name
            selected_task_index = self.main_tabs.tasks_tab.selected_task_index



            self.tasks_model.delete_task(column_name, selected_task_index)

        self.tasks_model.add_task_to_dict_from_raw_data(column_name, task_raw)

        # TODO: SAVE MODEL TO FILE


        # view

        self.recreate_list_view(column_name)




    def recreate_list_view(self, column_name: str) -> None:

        # view
        tasks_tab = self.main_tabs.tasks_tab
        list_view: ListView = tasks_tab.list_views[column_name]
        list_view.clear()

        list_items = tasks_tab.create_list_items(column_name)

        for list_item in list_items:
            list_view.append(list_item)



    def move_task(self, move_direction: TaskMoveDirection) -> None:
        source_column_name = self.main_tabs.tasks_tab.selected_column_name

        column_names = self.config.task_column_names

        # get index of the source column
        source_column_index = column_names.index(source_column_name)

        if move_direction == TaskMoveDirection.LEFT:
            target_column_index = max(source_column_index - 1, 0)
        elif move_direction == TaskMoveDirection.RIGHT:
            target_column_index = min(source_column_index + 1, len(column_names) - 1)

        target_column_name = self.config.task_column_names[target_column_index]

        logging.info(f'Moving task from {source_column_name} to {target_column_name}')


        if source_column_index == target_column_index:
            return

        if len(self.tasks_model.tasks[source_column_name]) == 0:
            return


        # Remove task from source column
        selected_task_index = self.main_tabs.tasks_tab.selected_task_index
        task_to_move = self.tasks_model.tasks[source_column_name][selected_task_index]
        self.tasks_model.delete_task(source_column_name, selected_task_index)

        # Add task to target column
        task_to_move.column_name = target_column_name

        if target_column_name not in self.tasks_model.tasks:
            self.tasks_model.tasks[target_column_name] = []

        self.tasks_model.tasks[target_column_name].append(task_to_move)
        self.tasks_model.tasks[target_column_name].sort(key=lambda task: task.priority.value)

        # TODO: SAVE MODEL TO FILE

        # Update the view
        self.recreate_list_view(source_column_name)
        self.recreate_list_view(target_column_name)

        # Select the moved task in the target column
        target_list_view: ListView = self.main_tabs.tasks_tab.list_views[target_column_name]

        # Find the index of the moved task in the target column
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

        logging.info(f'Deleting task from {column_name} at index {selected_task_index}')

        if selected_task_index is not None:
            self.tasks_model.delete_task(column_name, selected_task_index)

            # TODO: SAVE MODEL TO FILE

            self.recreate_list_view(column_name)