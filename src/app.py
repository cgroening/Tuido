import logging
from pprint import pprint  # type: ignore # noqa

from textual import work, events
from textual.app import App, ComposeResult
# from textual.events import DataTableRowHighlighted
from textual.binding import Binding
from textual.widget import Widget
from textual.widgets import Footer, Header, Tabs, DataTable, Input, Select, TextArea, Markdown
from rich.text import Text  # type: ignore # noqa

from controller.topics_controller import TopicsController
from controller.tasks_controller import TasksController
from controller.notes_controller import NotesController
from model.config import Config
from model.notes import Notes
from model.tasks import Tasks
from model.topics import Topic
from view.main_tabs import MainTabs
from util.question_screen import QuestionScreen


class TuidoApp(App):
    """
    Main application class (main controller) for the Tuido app.

    Tuido app is a simple application that provides a user interface for
    managing topics, tasks and notes.

    Attributes:
        TITLE: The title of the app.
        CSS_PATH: The path to the CSS file for styling.
        config: The configuration object for the app.
        topics_model: The topics model.
        notes_model: The notes model.
        topics_controller: The controller object for managing topics.
        notes_controller: The controller object for managing notes.
        main_tabs: The main tabs widget for the app.
    """

    TITLE = "Tuido"
    CSS_PATH = 'view/app_style.css'
    config: Config
    topics_model: Topic
    notes_model: Notes
    main_tabs: MainTabs
    topics_controller: TopicsController
    notes_controller: NotesController

    BINDINGS = [
        # Global
        Binding(key='q', key_display='q', action='app_previous_tab',
                description='Tab ←',
                tooltip='Select the previous tab'),
        Binding(key='w', key_display='w', action='app_next_tab',
                description='Tab →',
                tooltip='Select the next tab'),
        Binding(key='d', key_display='d', action='app_toggle_dark',
                description='Lights',
                tooltip='Toggle between dark and light mode'),
        Binding(key='ctrl+q', key_display='^q', action='quit',
                description='Quit',
                tooltip='Quit the app'),

        Binding(key='f11', key_display='F11',
                action='app_copy_selection_to_clipboard',
                description='Copy',
                tooltip='Copy selection to clipboard'),

        # Tasks controller
        Binding(key='f1', key_display='F1', action='tasks_new',
                description='New',
                tooltip='Create a new task'),
        Binding(key='f2', key_display='F2', action='tasks_list',
                description='List',
                tooltip='Focus the tasks list'),
        Binding(key='f3', key_display='F3', action='tasks_down',
                description='↓',
                tooltip='Move the currently selected task down'),
        Binding(key='f4', key_display='F4', action='tasks_up',
                description='↑',
                tooltip='Move the currently selected task up'),
        Binding(key='f5', key_display='F5', action='tasks_today',
                description='Today',
                tooltip='Set start and end date to today'),
        Binding(key='f6', key_display='F6', action='tasks_tomorrow',
                description='Tomorrow',
                tooltip='Set start and end date to tomorrow'),
        Binding(key='f7', key_display='F7', action='tasks_add_date',
                description='Date +',
                tooltip='Open the date picker to set start and end date'),
        Binding(key='f8', key_display='F8', action='tasks_remove_date',
                description='Date -',
                tooltip='Remove the date from the task'),

        # Topics controller
        Binding(key='f1', key_display='F1', action='topics_new',
                description='New',
                tooltip='Create a new topic'),
        Binding(key='f2', key_display='F2', action='topics_focus_list',
                description='List',
                tooltip='Focus the topic list'),
        Binding(key='f5', key_display='F5', action='topics_save',
                description='Save',
                tooltip='Save the currently selected topic'),
        Binding(key='f10', key_display='F10', action='topics_copy_clipboard',
                description='Copy',
                tooltip='Copy the content of the selected input to ' + \
                             'the clipboard'),
        Binding(key='shift+f5', key_display='⇧F5', action='topics_discard',
                description='Discard',
                tooltip='Discard the changes made on the current topic'),
        Binding(key='shift+f8', key_display='⇧F8', action='topics_delete',
                description='Delete',
                tooltip='Delete the currently selected topic'),

        # Notes controller
        Binding(key='f1', key_display='F1', action='notes_do_something',
                description='Do something',
                tooltip='XXX'),
        Binding(key='f2', key_display='F2', action='notes_show_textarea',
            description='TXT',
            tooltip='Show the textarea and markdown'),
        Binding(key='f3', key_display='F3', action='notes_show_md',
            description='MD',
            tooltip='Show the textarea and markdown'),
        Binding(key='f4', key_display='F4', action='notes_show_textarea_and_md',
            description='TXT+MD',
            tooltip='Show the textarea and markdown'),

        # TextOps controller
        Binding(key='f1', key_display='F1', action='textops_insert',
                description='Insert',
                tooltip='Insert text from the clipboard'),
        Binding(key='f12', key_display='F12', action='textops_copy',
                description='Copy',
                tooltip='Copy the content of the textarea to the clipboard'),
    ]


    def __init__(self) -> None:
        """
        Initializes the app.
        """
        super().__init__()
        # Config
        self.config = Config('data/config.yaml')

        # Models
        self.topics_model = Topic('data/topics.json')
        self.tasks_model = Tasks('data/tasks.json')
        self.notes_model = Notes('data/notes.md')

        # Views
        self.main_tabs = MainTabs()

        # Controllers
        self.topics_controller = TopicsController(
            self.config, self.topics_model, self.main_tabs
        )

        self.tasks_controller = TasksController(
            self.config, self.tasks_model, self.main_tabs
        )

        self.notes_controller = NotesController(
            self.config, self.notes_model, self.main_tabs
        )

        logging.info('App initialized')

    def compose(self) -> ComposeResult:
        """
        Creates the child widgets.
        """
        yield Header(icon='🗂️')
        yield self.main_tabs
        yield Footer(show_command_palette=True)

    def on_startup(self) -> None:
        """
        Gets called before mount.
        """
        pass

    def on_mount(self) -> None:
        """
        Initializes the app after mounting.
        """
        # self.screen.styles.debug = True

        # Initialize the topics table
        table = self.query_one("#topics_table", expect_type=DataTable)
        self.topics_controller.initialize_topics_table(table)

    def on_ready(self) -> None:
        """
        Gets called after mounting.
        """
        # self.topics_controller.app_startup = False
        pass

    def check_action(self, action: str, parameters: tuple[object, ...]) \
        -> None | bool:
        """
        Checks if the action is valid for the current tab. The name of the
        action must follow the following scheme:
        `action_<controller_name>_<action_name>`.

        Args:
            action: The action to check.
            parameters: The parameters for the action.

        Returns:
            - `True` if the action is valid for the current tab, the
              corresponding key will be shown in the footer.
            - `False` if the action is not valid for the current tab, the
              corresponding key will not be shown in the footer.
            - `None` if the action is valid for the current tab but not the
              current state, the key will be grayed out in the footer.

        See also:
            https://textual.textualize.io/guide/actions/#dynamic-actions
        """
        # List of global actions that are valid for all tabs
        GLOBAL_ACTIONS = ['app', 'quit', 'copy_to_clipboard',
                          'focus_next', 'focus_previous']

        # Get name if the current tab
        current_tab = self.main_tabs.current_tab

        # Extract the name of the controller from the action
        controller_name = action.split('_')[0]

        # Check if the action is valid for the current tab
        if controller_name in ['topics', 'tasks', 'notes', 'textops']:
            if controller_name == current_tab \
                or controller_name in GLOBAL_ACTIONS \
                or action == 'command_palette':
                return True
            else:
                return False
        return True

    async def on_data_table_row_highlighted(
        self, event: DataTable.RowHighlighted
    ) -> None:
        """
        Is triggered when a row in the DataTable is highlighted.
        This method updates the input fields with the values from the
        selected row.

        Args:
            event: The event containing information about the
            highlighted row.
        """
        self.topics_controller.update_input_fields(
            lambda id: self.query_one(id)
        )

        # Disable startup state after first selection
        # This is necessary to prevent the input fields from being
        # marked as changed when the app starts
        # and the topics table is initialized
        self.topics_controller.app_startup = False

    def on_input_changed(self, event: Input.Changed) -> None:
        """
        Is triggered when the value of an Input is changed.
        If the input field is changed programmatically, it will be ignored.
        Otherwise, `self.compare_input_value_to_original` is called.

        Args:
            event: The event containing information about the changed input.
        """
        input_name = event.input.id
        if input_name in self.topics_controller.programmatically_changed_inputs:
            self.topics_controller.programmatically_changed_inputs \
                .remove(input_name)
            return

        self.compare_input_value_to_original(event)

    def on_text_area_changed(self, event: TextArea.Changed) -> None:
        """
        Is triggered when the value of a TextArea is changed.
        If the input field is changed programmatically, it will be ignored.
        Otherwise, `self.compare_input_value_to_original` is called.

        Args:
            event: The event containing information about the changed input.
        """
        input_name = event.text_area.id

        # logging.info(f'input_name: {input_name}')

        # # TODO: Prüfen, ob topics_.... oder notes....

        if input_name in self.topics_controller.programmatically_changed_inputs:
            self.topics_controller.programmatically_changed_inputs.remove(
                input_name
            )
            return

        self.compare_input_value_to_original(event)

    def on_select_changed(self, event: Select.Changed) -> None:
        """
        Is triggered when the value of a Select is changed.
        If the input field is changed programmatically, it will be ignored.
        Otherwise, `self.compare_input_value_to_original` is called.

        Args:
            event: The event containing information about the changed select.
        """
        input_name = event.select.id
        if input_name in self.topics_controller.programmatically_changed_inputs:
            self.topics_controller.programmatically_changed_inputs \
                .remove(input_name)
            return

        self.compare_input_value_to_original(event)

    def compare_input_value_to_original(
        self, event: Input.Changed | TextArea.Changed | Select.Changed
    ) -> None:
        """
        Compares the current value of the input field to the original value
        from the model. If the values are different, the input field is
        marked as changed and the topics table is deactivated. If the
        values are the same, the input field is marked as unchanged and
        the topics table is activated.

        Args:
            event: The event containing information about the changed input.
        """
        # TODO: Cleanup/extract code to separate methods

        input_widget: Input | TextArea | Select

        # Get the input widget that triggered the event and the value of it
        if isinstance(event, Input.Changed):
            input_widget = event.input
            current_value = input_widget.value
        elif isinstance(event, TextArea.Changed):
            input_widget = event.text_area
            current_value = input_widget.text
        elif isinstance(event, Select.Changed):
            input_widget = event.select
            current_value = input_widget.value
        else:
            return

        # Ignore events from tabs other than "Topics"
        if input_widget.id is None or not input_widget.id.startswith('topics_'):
            return

        if current_value == Select.BLANK:
            current_value = ''

        # Get original value from the model
        topics_ctrl = self.topics_controller
        topic_id = self.main_tabs.topics_tab.topics_table.get_current_id()
        field_name = input_widget.id.replace('topics_', '') \
                                    .replace('_input', '')

        if field_name in topics_ctrl.topics_model.topics_by_id[topic_id].keys():
            original_value = topics_ctrl.topics_model \
                             .topics_by_id[topic_id][field_name]
        else:
            original_value = ''

        # Debugging
        # logging.info(
        #     f'compare_input_value_to_original: {input_widget.id} ' +
        #     f'current_value: {current_value}, ' +
        #     f'original_value: {original_value}')

        # Compare current value to original value
        if current_value == original_value:
            input_widget.remove_class('changed-input')

            if input_widget.id in topics_ctrl.user_changed_inputs:
                topics_ctrl.user_changed_inputs.remove(input_widget.id)
        else:
            input_widget.add_class('changed-input')
            topics_ctrl.user_changed_inputs.add(input_widget.id)

        # Change the state of the topics table
        self.activate_deactivate_topics_table()

    def activate_deactivate_topics_table(self) -> None:
        """
        Activates or deactivates the topics table based on the number of
        user changed inputs.
        If there are any user changed inputs, the topics table is
        deactivated (disabled). Otherwise, it is activated (enabled).
        This is used to prevent the user from selecting a different topic
        while there are unsaved changes in the current topic.
        """
        if len(self.topics_controller.user_changed_inputs) > 0:
            self.main_tabs.topics_tab.topics_table.disabled = True
        else:
            self.main_tabs.topics_tab.topics_table.disabled = False

    def action_do_nothing(self) -> None:
        # focused_widget = self.focused  # TODO: or self.screen.focused ?
        # if focused_widget:
        #     logging.info(f'Fokus liegt auf: {focused_widget.id}')
        # else:
        #     logging.info('Kein Widget hat den Fokus.')
        pass

    def action_tasks_new(self) -> None:
        """
        Creates a new topic.
        """
        self.tasks_controller.testest()

    def action_topics_new(self) -> None:
        """
        Creates a new topic.
        """
        self.topics_controller.create_new_topic()

    def action_topics_focus_table(self) -> None:
        """
        Focuses the topics table.
        """
        table = self.query_one('#topics_table', expect_type=DataTable)
        self.set_focus(table)

    def action_topics_save(self) -> None:
        """
        Saves the currently selected topic.
        """
        # Update topics model with the values from the input fields
        self.topics_controller.save_topic(lambda id: self.query_one(id))

        # Remove class "changed-input" from all changed inputs
        for field in self.topics_controller.user_changed_inputs:
            self.query_one(f'#{field}').remove_class('changed-input')

        # Re-enable the topics table which was disabled when the user changed an
        # input to prevent switching topics while there are unsaved changes
        self.main_tabs.topics_tab.topics_table.disabled = False
        self.notify('Topic updated!')

    @work
    async def action_topics_discard(self) -> None:
        """
        Discards the changes made to the currently selected topic.
        The input fields will be reset to the original values from the model.
        The topics table will be re-enabled. The user will be asked for
        confirmation before the changes are discarded.
        """
        if await self.push_screen_wait(
            QuestionScreen('Really discard changes?'),
        ):
            self.topics_controller.update_input_fields(
                lambda id: self.query_one(id), called_from_discard=True
            )
            self.notify('Changes discarded!')
        else:
            self.notify('Discard canceled.', severity='warning')

    @work
    async def action_topics_delete(self) -> None:
        """
        Deletes the currently selected topic.
        The user will be asked for confirmation before the topic is
        deleted.
        """
        if await self.push_screen_wait(
            QuestionScreen("Really delete the selected topic?"),
        ):
            self.topics_controller.delete_topic()
            self.notify('Topic deleted!')
        else:
            self.notify('Deletion canceled.', severity='warning')

    def action_notes_show_textarea(self) -> None:
        """
        Shows the textarea and hides the markdown.
        """
        textarea = self.query_one('#notes_textarea', expect_type=TextArea)
        markdown = self.query_one('#notes_markdown', expect_type=Markdown)
        textarea.remove_class('hidden')
        markdown.add_class('hidden')

    def action_notes_show_md(self) -> None:
        """
        Hides the textarea and shows the markdown.
        """
        textarea = self.query_one('#notes_textarea', expect_type=TextArea)
        markdown = self.query_one('#notes_markdown', expect_type=Markdown)
        textarea.add_class('hidden')
        markdown.remove_class('hidden')

    def action_notes_show_textarea_and_md(self) -> None:
        """
        Shows the textarea and markdown.
        """
        textarea = self.query_one('#notes_textarea', expect_type=TextArea)
        markdown = self.query_one('#notes_markdown', expect_type=Markdown)
        textarea.remove_class('hidden')
        markdown.remove_class('hidden')

    def action_app_toggle_dark(self) -> None:
        """
        Toggles dark mode.
        """
        self.theme = (
            'textual-dark' if self.theme == 'textual-light' else 'textual-light'
        )

    def action_app_previous_tab(self) -> None:
        """
        Selects the previous tab.
        """
        tabs = self.query_one('#main_tabs', expect_type=Tabs)
        tabs.action_previous_tab()

    def action_app_next_tab(self) -> None:
        """
        Selects the next tab.
        """
        tabs = self.query_one('#main_tabs', expect_type=Tabs)
        tabs.action_next_tab()

    def action_copy_to_clipboard(self) -> None:
        """
        Copies content from the currently focused input or textarea to
        the clipboard.
        """
        focused_widget = self.focused

        # if isinstance(focused_widget, (Input, TextArea)):
        if hasattr(focused_widget, 'value'):
            self.copy_to_clipboard(focused_widget.value)  # type: ignore

    def action_app_copy_selection_to_clipboard(self) -> None:
        """
        Copies the selected text from the currently focused widget to
        the clipboard.
        """
        focused_widget: Widget | None = self.focused

        if hasattr(focused_widget, 'selected_text'):
            self.copy_to_clipboard(focused_widget.selected_text)  # type: ignore

        self.notify('Selection copied to clipboard!')


    # async def on_key(self, event: events.Key) -> None:
    #     self.notify(f"Key pressed: {event.key}")