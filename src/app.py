import argparse
import logging

from textual import events, work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Footer, Header, Tabs, DataTable, Input, Select, TextArea, Markdown

from pylightlib.txtl import CustomBindings
from pylightlib.txtl.QuestionScreen import QuestionScreen

from model.config_model import Config
from model.notes_model import Notes
from model.tasks_model import Tasks
from model.topics_model import Topic
from view.main_view import MainTabs
from view.tasks_tab_edit_screen import TaskEditScreen
from controller.topics_controller import TopicsController
from controller.tasks_controller import TasksController, TaskAction, TaskMoveDirection
from controller.notes_controller import NotesController


CUSTOM_BINDINGS = CustomBindings(with_copy_paste_keys=True)


class TuidoApp(App):
    """
    Main application class (main controller) for the Tuido app.

    Tuido app is a simple application that provides a user interface for
    managing topics, tasks and notes.

    Attributes:
        config: The configuration object for the app.
        topics_model: The topics model.
        notes_model: The notes model.
        topics_controller: The controller object for managing topics.
        notes_controller: The controller object for managing notes.
        main_view: Main view of the application, containing the main layout
            and widgets.
        popup_name: The name of the currently displayed popup; None if no
            popup is shown.
        footer: The footer widget of the app.
        last_escape_key: Timestamp of the last 'escape' key press, used to
            toggle global key bindings.
        escape_pressed_twice: Reactive flag indicating whether the 'escape' key
            was pressed twice.
    """
    TITLE = "Tuido"
    CSS_PATH = 'view/app_style.css'
    BINDINGS = CUSTOM_BINDINGS.get_bindings()  # type: ignore
    config: Config
    topics_model: Topic
    notes_model: Notes
    main_view: MainTabs
    topics_controller: TopicsController
    notes_controller: NotesController
    popup_name: str | None = None
    footer: Footer
    last_escape_key: float = 0.0
    escape_pressed_twice = reactive(False, bindings=True)


    BINDINGSS = [
        # Binding(key='c', key_display='^c', action='shortcut_test'),
        # Binding(key='meta+c', key_display='^c', action='shortcut_test'),

        # Global
        Binding(key='q', key_display='q', action='app_previous_tab',
                description='Tab ←',
                tooltip='Select the previous tab',
                show=False),
        Binding(key='w', key_display='w', action='app_next_tab',
                description='Tab →',
                tooltip='Select the next tab',
                show=False),
        Binding(key='d', key_display='d', action='app_toggle_dark',
                description='Lights',
                tooltip='Toggle between dark and light mode',
                show=False),
        Binding(key='ctrl+q', key_display='^q', action='quit',
                description='Quit',
                tooltip='Quit the app',
                show=False),

        # Tasks controller
        Binding(key='f1', key_display='F1', action='tasks_new',
                description='New',
                tooltip='Create a new task'),
        Binding(key='f2', key_display='F2', action='tasks_edit',
                description='Edit',
                tooltip='Edit the currently selected task'),
        Binding(key='f3', key_display='F3', action='tasks_left',
                description='Move ←',
                tooltip='Move the currently selected task left'),
        Binding(key='f4', key_display='F4', action='tasks_right',
                description='Move →',
                tooltip='Move the currently selected task right'),

        # Woraround: Ensures the correct order of the bindings in the following
        # tabs
        Binding(key='f5', key_display='F5', action='', show=False),
        Binding(key='f6', key_display='F6', action='', show=False),
        Binding(key='f7', key_display='F7', action='', show=False),

        Binding(key='f8', key_display='F8', action='tasks_delete',
                description='Del',
                tooltip='Delete the currently selected task'),
        # Binding(key='f5', key_display='F5', action='tasks_today',
        #         description='Today',
        #         tooltip='Set start and end date to today'),
        # Binding(key='f6', key_display='F6', action='tasks_tomorrow',
        #         description='Tomorrow',
        #         tooltip='Set start and end date to tomorrow'),
        # Binding(key='f7', key_display='F7', action='tasks_add_date',
        #         description='Date +',
        #         tooltip='Open the date picker to set start and end date'),
        # Binding(key='f8', key_display='F8', action='tasks_remove_date',
        #         description='Date -',
        #         tooltip='Remove the date from the task'),

        # TODO: Delete when transformation to TaskEditScreen is done
        # Tasks controller: Popup
        # Binding(key='f4', key_display='F4', action='tasks_popup_edit_cancel',
        #         description='Cancel',
        #         tooltip='Discard changes and close the popup'),
        # Binding(key='f5', key_display='F5', action='tasks_popup_edit_save',
        #         description='Save',
        #         tooltip='Save changes and close the popup'),
        # Binding(key='f7', key_display='F7',
        #         action='tasks_popup_edit_decrease_start_date',
        #         description='Start-1',
        #         tooltip='Decrease the start date by 1 day'),
        # Binding(key='f8', key_display='F8',
        #         action='tasks_popup_edit_increase_start_date',
        #         description='Start+1',
        #         tooltip='Increase the start date by 1 day'),
        # Binding(key='f9', key_display='F9',
        #         action='tasks_popup_edit_decrease_end_date',
        #         description='End-1',
        #         tooltip='Decrease the end date by 1 day'),
        # Binding(key='f10', key_display='F10',
        #         action='tasks_popup_edit_increase_end_date',
        #         description='End+1',
        #         tooltip='Increase the end date by 1 day'),


        # Topics controller
        Binding(key='f1', key_display='F1', action='topics_new',
                description='New',
                tooltip='Create a new topic'),
        Binding(key='f2', key_display='F2', action='topics_focus_table',
                description='Table',
                tooltip='Focus the topic list'),
        Binding(key='f5', key_display='F5', action='topics_save',
                description='Save',
                tooltip='Save the currently selected topic'),
        Binding(key='f7', key_display='F7', action='topics_discard',
                description='Discard',
                tooltip='Discard the changes made on the current topic'),
        Binding(key='f8', key_display='F8', action='topics_delete',
                description='Del',
                tooltip='Delete the currently selected topic'),

        # Notes controller
        # Binding(key='f1', key_display='F1', action='notes_do_something',
        #         description='Do something',
        #         tooltip='XXX'),
        Binding(key='f2', key_display='F2', action='notes_show_textarea',
            description='Text',
            tooltip='Show the textarea and markdown'),
        Binding(key='f3', key_display='F3', action='notes_show_md',
            description='Markdown',
            tooltip='Show the textarea and markdown'),
        Binding(key='f4', key_display='F4', action='notes_show_textarea_and_md',
            description='Text+Md',
            tooltip='Show the textarea and markdown'),

        # Global
        # Binding(key='f9', key_display='F9', action='app_get_focus',
        #         description='Get focus',
        #         tooltip='Get ID of the focused widget'),
        Binding(key='f11', key_display='F11',
                action='app_copy_selection_to_clipboard',
                description='CpySel',
                tooltip='Copy the selected text to the clipboard',
                show=False),
        Binding(key='f12', key_display='F12',
                action='app_paste_from_clipboard',
                description='Paste',
                tooltip='Paste the text from the clipboard',
                show=False),

        Binding(key='shift+f11', key_display='⇧F11',
                action='app_copy_widget_value_to_clipboard',
                description='CpyVal',
                tooltip='Copy value of the selected input widget to clipboard',
                show=False),
    ]


    def __init__(self) -> None:
        """
        Initializes the app.

        Args:
            args: The command line arguments.
        """
        super().__init__()

        # Get data folder from command line arguments
        parser = argparse.ArgumentParser()
        parser.add_argument('--data_folder', type=str)
        args = parser.parse_args()
        data_folder = args.data_folder if args.data_folder else 'data'

        # Config
        self.config = Config(f'{data_folder}/config.yaml')

        # Models
        self.tasks_model = Tasks(f'{data_folder}/tasks.json')
        self.topics_model = Topic(f'{data_folder}/topics.json')
        self.notes_model = Notes(f'{data_folder}/notes.md')

        # Views
        self.main_view = MainTabs(self)

        # Controllers
        self.tasks_controller = TasksController(
            self.config, self.tasks_model, self.main_view, self
        )

        self.topics_controller = TopicsController(
            self.config, self.topics_model, self.main_view
        )

        self.notes_controller = NotesController(
            self.config, self.notes_model, self.main_view
        )

        logging.info('App initialized')

    def compose(self) -> ComposeResult:
        """
        Creates the child widgets.
        """
        yield Header(icon='🗂️')
        yield self.main_view
        self.footer = Footer(show_command_palette=False)
        self.footer.compact = True
        yield self.footer

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

        self.main_view.tasks_tab.set_can_focus()

    def on_ready(self) -> None:
        """
        Gets called after mounting.
        """
        # self.topics_controller.app_startup = False
        pass

    async def on_key(self, event: events.Key) -> None:
        """
        Handles key press events.

        If the 'escape' key is pressed, it toggles the global key bindings
        based on the time interval between presses.

        Args:
            event: The key press event.
        """
        # self.notify(f'Key pressed: {event.key}')
        if event.key == 'escape':
            if event.time - self.last_escape_key < 0.5:
                self.escape_pressed_twice = not self.escape_pressed_twice

            self.last_escape_key = event.time

    def check_action(self, action: str, parameters: tuple[object, ...]) \
    -> bool | None:
        """
        Checks if the action is valid for the current context.

        If the action is recognized, it will be handled by the
        `CUSTOM_BINDINGS` instance. The action is checked against the
        current active group (tab) and whether global keys should be shown
        based on the `escape_pressed_twice` flag.

        Args:
            action: The action to check.
            parameters: Parameters for the action.

        Returns:
            bool | None: True if the corresponding key of the action is to be
                displayed or None if not. False if the action is valid for the
                current context but is to be displayed as disabled.
        """
        return CUSTOM_BINDINGS.handle_check_action(
            action, parameters, active_group=str(self.main_view.current_tab_name),
            show_global_keys=bool(self.escape_pressed_twice)
        )

    def action_globalalways_toggle_dark(self) -> None:
        """
        Toggles dark mode.
        """
        self.theme = (
            'textual-dark' if self.theme == 'textual-light' else 'textual-light'
        )

    def action_globalalways_previous_tab(self) -> None:
        """
        Selects the previous tab.
        """
        tabs = self.query_one('#main_tabs', expect_type=Tabs)
        tabs.action_previous_tab()

    def action_globalalways_next_tab(self) -> None:
        """
        Selects the next tab.
        """
        tabs = self.query_one('#main_tabs', expect_type=Tabs)
        tabs.action_next_tab()



    # Debugging
    # def action_app_get_focus(self) -> None:
    #     focused_widget = self.focused  # TODO: or self.screen.focused ?
    #     if focused_widget:
    #         # logging.info(f'Focus on: {focused_widget.id}')
    #         self.notify(f'Focus on: {focused_widget.id} ({type(focused_widget)})')
    #     else:
    #         # logging.info('No widget focused')
    #         self.notify('No widget focused')
    def action_shortcut_test(self) -> None:
        self.notify('The shortcut was triggered!')


    def action_tasks_new(self) -> None:
        """
        Displays the task form for creating a new task.
        """
        self.tasks_controller.show_task_form(TaskAction.NEW)

    def action_tasks_edit(self) -> None:
        """
        Displays the task form for editing the currently selected task.
        """
        self.tasks_controller.show_task_form(TaskAction.EDIT)

    def action_tasks_left(self) -> None:
        """
        Moves the currently selected task to the left column.
        """
        self.tasks_controller.move_task(TaskMoveDirection.LEFT)

    def action_tasks_right(self) -> None:
        """
        Moves the currently selected task to the right column.
        """
        self.tasks_controller.move_task(TaskMoveDirection.RIGHT)

    @work
    async def action_tasks_delete(self) -> None:
        """
        Deletes the currently selected task.
        The user will be asked for confirmation before the task is deleted.
        """
        if await self.push_screen_wait(
            QuestionScreen('Really delete the selected task?'),
        ):
            self.tasks_controller.delete_selected_task()
            self.notify('Task deleted!')
        else:
            self.notify('Deletion canceled.', severity='warning')

    # def action_tasks_popup_edit_cancel(self) -> None:
    #     """
    #     Closes the task form popup without saving changes.
    #     """
    #     self.main_tabs.tasks_tab.input_form.clear_and_hide()

    # def action_tasks_popup_edit_save(self) -> None:
    #     """
    #     Saves the changes made in the task form popup and closes it.
    #     """
    #     self.main_tabs.tasks_tab.input_form.submit_changes()

    # def action_tasks_popup_edit_decrease_start_date(self) -> None:
    #     """
    #     Decreases the start date of the task by 1 day.
    #     """
    #     self.main_tabs.tasks_tab.input_form.adjust_date(
    #         DateName.START_DATE, DateAdjustment.DECREASE
    #     )

    # def action_tasks_popup_edit_increase_start_date(self) -> None:
    #     """
    #     Decreases the start date of the task by 1 day.
    #     """
    #     self.main_tabs.tasks_tab.input_form.adjust_date(
    #         DateName.START_DATE, DateAdjustment.INCREASE
    #     )

    # def action_tasks_popup_edit_decrease_end_date(self) -> None:
    #     """
    #     Decreases the start date of the task by 1 day.
    #     """
    #     self.main_tabs.tasks_tab.input_form.adjust_date(
    #         DateName.END_DATE, DateAdjustment.DECREASE
    #     )

    # def action_tasks_popup_edit_increase_end_date(self) -> None:
    #     """
    #     Decreases the start date of the task by 1 day.
    #     """
    #     self.main_tabs.tasks_tab.input_form.adjust_date(
    #         DateName.END_DATE, DateAdjustment.INCREASE
    #     )

    def action_topics_new(self) -> None:
        """
        Creates a new topic.
        """
        if len(self.topics_controller.user_changed_inputs) > 0:
            self.notify('Discard or save changes first.',
                        severity='warning')
            return

        self.topics_controller.create_new_topic()

    def action_topics_focus_table(self) -> None:
        """
        Focuses the topics table.
        """
        table = self.query_one('#topics_table', expect_type=DataTable)
        self.set_focus(table)
        self.notify('Topics table focused!')

    def action_topics_save(self) -> None:
        """
        Saves the currently selected topic.
        """
        # Update topics model with the values from the input fields
        self.topics_controller.save_topic(lambda id: self.query_one(id))

        # self.topics_controller.update_input_fields(
        #     lambda id: self.query_one(id), called_from_discard=True
        # )

        # Remove class "changed-input" from all changed inputs
        for field in self.topics_controller.user_changed_inputs:
            self.query_one(f'#{field}').remove_class('changed-input')

        # Re-enable the topics table which was disabled when the user changed an
        # input to prevent switching topics while there are unsaved changes
        self.main_view.topics_tab.topics_table.disabled = False
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

    # def on_tasks_input_popup_submit(self, message: TasksInputPopup.Submit) \
    # -> None:
    #     self.tasks_controller.save_task(message)

    def on_task_edit_screen_submit(self, message: TaskEditScreen.Submit) \
    -> None:
        logging.info(f'on_tasks_tab_edit_screen_submit: {message}')
        self.tasks_controller.save_task(message)

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
        topic_id = self.main_view.topics_tab.topics_table.get_current_id()
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
            self.main_view.topics_tab.topics_table.disabled = True
        else:
            self.main_view.topics_tab.topics_table.disabled = False


    def _paste_into_input(self, input: Input, text: str) \
    -> None:
        """
        Pastes the given text into the input widget at the cursor position.
        """
        cursor_pos = input.cursor_position or len(input.value)
        input.insert(text, cursor_pos)
        input.cursor_position = cursor_pos + len(text)
        self.notify('Text pasted into input field!')

    def _paste_into_textarea(self, textarea: TextArea, text: str) \
    -> None:
        """
        Pastes the given text into the textarea at the cursor position.
        """
        cursor_pos: tuple[int, int] = textarea.cursor_location or (0, 0)
        textarea.insert(text, cursor_pos)
        textarea.cursor_location = (cursor_pos[0], cursor_pos[1]+len(text))
        self.notify('Text pasted into text area!')

    # Debugging
    # async def on_key(self, event: events.Key) -> None:
    #     self.notify(f"Key pressed: {event.key}")