from model.config import Config  # type: ignore
from model.tasks import Tasks    # type: ignore
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