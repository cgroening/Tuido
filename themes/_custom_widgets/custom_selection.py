from textual.widgets import SelectionList
from textual.widgets._toggle_button import ToggleButton
from textual.strip import Strip
from rich.segment import Segment


class CustomSelectionList(SelectionList):
    """
    A custom Textual SelectionList whose items display a check mark when
    selected. If unselected, they show an empty box - instead of the default
    behavior of showing an "X".

    Attributes:
        CUSTOM_BUTTON_INNER: The character to display when an item is selected.
    """
    CUSTOM_BUTTON_INNER = '✔'


    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def render_line(self, y: int) -> Strip:
        """
        This methods overwrites `textual.widgets.selection_list.SelectionList
        .render_line()` to customize the look of checked and unchecked items.

        Args:
            y: The line number to render.

        Returns:
            A Strip representing the rendered line.
        """
        # Get the default rendered line from the parent class (SelectionList)
        rendered_line: Strip = super().render_line(y)

        # rendered_line contains the segments for the line including the
        # check box representation. This segment needs to be modified to
        # replace the default "X" with a custom check mark when selected.
        # Since rendered_line is immutable, a new list of segments is created.
        segments: list[Segment] = []

        # Loop through each segment in the rendered line
        for segment in rendered_line:
            # Check if the segment text matches the default button inner
            # (= the one that must be modified)
            if segment.text == ToggleButton.BUTTON_INNER:
                # Check if segment is selected
                _, scroll_y = self.scroll_offset
                selection_index = scroll_y + y
                selection = self.get_option_at_index(selection_index)
                if selection.value in self._selected:
                    segment_text = self.CUSTOM_BUTTON_INNER
                else:
                    segment_text = ' '

                # Create a new segment with the custom check mark and same style
                segment_style = segment.style
                new_segment = Segment(segment_text, segment_style)
                segments.append(new_segment)
            else:
                # Not the segment containing the check box -> keep segment as is
                segments.append(segment)

        return Strip([
            *segments
        ])
