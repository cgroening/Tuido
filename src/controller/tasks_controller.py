import logging

from textual.app import App
from textual.widgets import ListView

from model.config_model import Config  # type: ignore
from model.tasks_model import Task, Tasks    # type: ignore
from view.main_tabs import MainTabs  # type: ignore
from view.tasks_tab_form import TasksInputPopup  # type: ignore


class TasksController:
    config: Config
    tasks_model: Tasks
    main_tabs: MainTabs
    app: App

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

        tasks_tab = self.main_tabs.tasks_tab

        tasks_tab.column_captions = self.tasks_model.column_captions
        tasks_tab.column_names = self.tasks_model.column_names
        tasks_tab.tasks = self.tasks_model.tasks

        # tasks_tab.add_list_view()
        # tasks_tab.add_list_view()
        # tasks_tab.add_list_view()

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

