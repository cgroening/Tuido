import logging

from textual.widgets import ListView

from model.config import Config  # type: ignore
from model.tasks import Task, Tasks    # type: ignore
from view.main_tabs import MainTabs  # type: ignore


class TasksController:
    config: Config
    tasks_model: Tasks
    main_tabs: MainTabs

    def __init__(self, config: Config, tasks_model: Tasks, main_tabs: MainTabs):
        """
        Initializes the TasksController.

        Args:
            config: The configuration object.
            tasks_model: The tasks model object.
            main_tabs: The main tabs object.
        """
        self.config = config
        self.tasks_model = tasks_model
        self.main_tabs = main_tabs

        tasks_tab = self.main_tabs.tasks_tab

        tasks_tab.column_captions = self.tasks_model.column_captions
        tasks_tab.column_names = self.tasks_model.column_names
        tasks_tab.tasks = self.tasks_model.tasks

        # tasks_tab.add_list_view()
        # tasks_tab.add_list_view()
        # tasks_tab.add_list_view()

    def testest(self):

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


