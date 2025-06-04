import logging
import threading
from typing import Callable

from textual import on
from textual.app import ComposeResult
from textual.containers import Grid
from textual.widgets import Static, TextArea, Markdown

from textual_textarea import TextEditor


class NotesTab(Static):
    """
    Notes tab content.

    Attributes:
        textarea: A TextArea widget for user input.
        markdown: A Markdown widget for displaying formatted text.
    """
    textarea: TextArea
    markdown: Markdown
    text_area_changed_action: Callable

    def __init__(self, **kwargs):
        """
        Initializes the Notes tab.

        Creates a TextArea widget for user input and a Markdown widget for
        displaying formatted text.
        """
        super().__init__(**kwargs)
        self.textarea = TextArea(id='notes_textarea', classes="notes-textarea",
                                 show_line_numbers=True)
        self.markdown = Markdown(id='notes_markdown', classes="notes-markdown")

    def compose(self) -> ComposeResult:
        """
        Adds the TextArea and Markdown widgets to the Notes tab.
        """
        with Grid():
            # yield TextEditor(text='', theme='nord-darker', id='ta')
            # yield TextEditor(text='', id='ta')
            yield self.textarea
            yield self.markdown

    @on(TextArea.Changed)
    async def update_markdown(self, event: TextArea.Changed) -> None:
        """
        Updates the Markdown widget when the TextArea content changes and .
        """
        # Update the Markdown widget with the content of the TextArea
        await self.query_one('#notes_markdown').update(event.text_area.text)  # type: ignore

        # Run text_area_changed_action in a separate thread to avoid blocking
        # the UI thread
        if self.text_area_changed_action is not None:
            threading.Thread(
                target=self.text_area_changed_action,
                args=(event.text_area.text,)
            ).start()
