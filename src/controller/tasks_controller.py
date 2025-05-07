import enum
import logging

from textual.app import App
from textual.widgets import ListView

from model.config_model import Config  # type: ignore
from model.tasks_model import Task, Tasks    # type: ignore
from view.main_tabs import MainTabs  # type: ignore
from view.tasks_tab_form import TasksInputPopup  # type: ignore


# create enum for task actions
class TaskAction(enum.Enum):
    NEW = 'new'
    EDIT = 'edit'


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

        column_name = self.main_tabs.tasks_tab.selected_column_name
        selected_task_index = self.main_tabs.tasks_tab.selected_task_index

        # model
        task_raw = {
            'description': message.description,
            'priority':    self.tasks_model.priority_str_to_num(message.priority),
            'start_date':  message.start_date,
            'end_date':    message.end_date
        }

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





    def testest2(self):

        tasks_tab = self.main_tabs.tasks_tab
        tasks_tab.list_views['inbox'].clear()
        logging.info(list(tasks_tab.list_views.keys()))


        # New task
        list_view: ListView = tasks_tab.list_views['inbox']

        new_task = Task(
            column_name='inbox',
            description='Test task',
            priority=1,
            start_date='2023-10-01',
            end_date='2023-10-31',
            days_to_start=0,
            days_to_end=30
        )

        tasks_tab.tasks['inbox'].append(new_task)

        # for list_view in

        list_items = tasks_tab.create_list_items('inbox')


        for list_item in list_items:
            list_view.append(list_item)

        # list_view.append(list_items)

        # list_view.append(new_task)

    def testest(self):
        # self.input_form = TasksTab_Form()
        # self.input_form.display = True
        # self.app.set_focus(self.input_form.name_input)

        input_form: TasksInputPopup = self.main_tabs.tasks_tab.input_form
        input_form.display = True
        self.app.set_focus(input_form.description_input)

