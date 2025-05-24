from textual.app import App, ComposeResult
from textual.widgets import DataTable, Button
from textual.containers import Vertical
import random
import string


class LargeDataTableApp(App):
    CSS = """
    Screen {
        align: center middle;
    }

    #main-container {
        height: 100%;
        width: 100%;
        layout: vertical;
    }

    DataTable {
        height: 1fr;
    }

    Button {
        margin: 1;
    }
    """

    def compose(self) -> ComposeResult:
        with Vertical(id="main-container"):
            yield DataTable(zebra_stripes=True, id="datatable")
            yield Button("Zeile oben einfügen", id="add-row-button")

    @staticmethod
    def random_string(length=8):
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

    def on_mount(self) -> None:
        table = self.query_one("#datatable", DataTable)

        columns = ["sort_order"] + [f"Spalte {i+1}" for i in range(20)]
        # Save actual ColumnKeys returned
        self.sort_key_column, *_ = table.add_columns(*columns)

        for i in range(10000):
            row = [i] + [self.random_string(8) for _ in range(20)]
            table.add_row(*row, key=i)

        table.cursor_type = "row"

        # table.move_cursor(row=5, scroll=True)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "add-row-button":
            table = self.query_one("#datatable", DataTable)

            # Get the current sort_key_column and use it to determine
            # the new row's sort order
            sort_orders = [
                table.get_cell_at((row_index, 0))
                for row_index in range(len(table.rows))
            ]
            min_sort_order = min(sort_orders) if sort_orders else 0
            new_sort_order = min_sort_order - 1

            new_row = [new_sort_order] + ["XXX"] * 20
            table.add_row(*new_row, key=new_sort_order)

            # Use current sort_key_column to sort the table
            table.sort(self.sort_key_column)

            # for idx, k in enumerate(table.rows.keys()):
            #     if k.value == new_sort_order:
            #         table.cursor_coordinate = (idx, 0)
            #         table.cursor_coordinate = (0, 0)
            #         break

            table.move_cursor(row=0)


if __name__ == "__main__":
    LargeDataTableApp().run()