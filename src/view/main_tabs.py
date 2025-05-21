from textual.app import ComposeResult
from textual.containers import Container
from textual.reactive import reactive
from textual.widgets import Tabs, Tab
from rich.text import Text  # type: ignore # noqa

from view.topics_tab import TopicsTab
from view.tasks_tab import TasksTab
from view.notes_tab import NotesTab

from pylightlib.msc.Singleton import Singleton  # type: ignore


class MainTabs(Container):
    """
    Main tabs container

    Attributes:
        current_tab: The currently selected tab.
        topics_tab: The topics tab widget.
    """
    # current_tab = reactive('topics')
    current_tab = reactive('topics', bindings=True)
    topics_tab: TopicsTab
    tasks_tab: TasksTab
    notes_tab: NotesTab


    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.tasks_tab = TasksTab(id='tasks-tab')
        self.topics_tab = TopicsTab(id='topics-tab', classes='hidden')
        self.notes_tab = NotesTab(id='notes-tab', classes='hidden')

    def compose(self) -> ComposeResult:
        """
        Creates the child widgets.
        """
        # Tab labels
        tabs = Tabs(
            Tab('Topics', id='topics'),
            Tab('Tasks', id='tasks'),
            Tab('Notes', id='notes'),
            id='main_tabs',
        )
        tabs.can_focus = False
        yield tabs

        # Pre-create all tab contents, but only the current one will be visible
        # yield TopicsTab(id="topics-tab")
        yield self.tasks_tab
        yield self.topics_tab
        yield self.notes_tab

    def on_tabs_tab_activated(self, event: Tabs.TabActivated) -> None:
        """
        Handles tab change events.

        This method is called when a tab is activated. It hides all tabs except
        the selected one. It also updates the reactive variable `current_tab`
        to reflect the selected tab.

        Args:
            event: The event containing information about the activated tab.
        """
        if event.tab.id is not None:
            # Hide all tabs first
            for tab_id in ['topics', 'tasks', 'notes']:
                self.query_one(f'#{tab_id}-tab').add_class('hidden')

            # Show the selected tab and update reactive variable
            tab_to_show = f'#{event.tab.id}-tab'
            self.query_one(tab_to_show).remove_class('hidden')
            self.current_tab = event.tab.id