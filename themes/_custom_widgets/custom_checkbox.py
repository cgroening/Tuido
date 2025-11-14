from textual.events import Callback, Mount
from textual.widgets import Checkbox


class CustomCheckbox(Checkbox):
    """
    A custom Textual Checkbox that displays a check mark when selected.
    When nothing is selected, it shows an empty box - instead of the default
    behavior of showing an "X".

    Attributes:
        CUSTOM_BUTTON_INNER: The character to display when the checkbox
        is checked.
    """
    CUSTOM_BUTTON_INNER = '✔'


    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def _on_mount(self, event: Mount) -> None:
        self.toggle_button_inner()
        return super()._on_mount(event)

    def on_checkbox_changed(self, event: Callback) -> None:
        self.toggle_button_inner()

    def toggle_button_inner(self):
        if self.value:
            self.BUTTON_INNER = self.CUSTOM_BUTTON_INNER
        else:
            self.BUTTON_INNER = ' '
