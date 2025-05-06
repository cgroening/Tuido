import logging
from textual.app import ComposeResult
from textual.containers import Grid, Horizontal, Vertical, VerticalScroll
from textual.events import Key, Focus, Blur
from textual.widgets import Static, ListView, ListItem, Label

from rich.text import Text



from model.tasks import Task, TaskPriority



# TODO: Add to pylightlib
# Normally, the ListView should be scrollable by itself, but it doesn't work
# as expected. So I create a custom ListView that scrolls the parent
# container instead.
class CustomListView(ListView):
    """
    Custom ListView that scrolls the parent container (`VerticalScroll`).

    Normally, the ListView should be scrollable by itself, but it doesn't work
    as expected in this application. So this custom ListView that scrolls the
    parent container is used instead.

    This is a workaround until the ListView is fixed.

    Attributes:
        vscroll: The parent container that is scrolled.
    """





    vscroll: VerticalScroll

    def __init__(self, vscroll, *args, **kwargs):
        """
        Initializes the CustomListView.

        Args:
            vscroll: The parent container that is scrolled.
            *args: Positional arguments for the ListView.
            **kwargs: Keyword arguments for the ListView.
        """
        super().__init__(*args, **kwargs)
        self.vscroll = vscroll
        self.vscroll.can_focus = False

    async def on_key(self, event: Key) -> None:
        """
        Handles key events for the ListView.

        This method is called when a key event occurs. If the key is 'up' or
        'down', the parent container is scrolled accordingly to maintain the
        current item in view.

        Args:
            event: The key event that occurred.
        """
        index = self.index or 0

        if event.key == 'up':
            index = max(0, index - 1)
        elif event.key == 'down':
            index = min(len(self.children) - 1, index + 1)
        else:
            return

        # self.index = index

        item = self.children[index]
        self.vscroll.scroll_to_widget(item)

        self.change_class(index)


    def change_class(self, index: int) -> None:
        for i, item in enumerate(self.children):
            if isinstance(item, ListItem):
                # if i == self.index:
                if i == index:
                    item.add_class('selected')
                else:
                    item.remove_class('selected')

    def on_focus(self, event: Focus) -> None:
        for item in self.children:
            item.remove_class('selected')

        self.change_class(self.index or 0)  # mark selected item


    def on_blur(self, event: Blur) -> None:
        for item in self.children:
            item.remove_class('selected')


    async def on_list_view_selected(self, event: ListView.Selected):
            for item in self.children:
            # for item in event.item.parent.children:
                item.remove_class('selected')  # alle deselektieren


            event.item.add_class('selected')  # aktuell ausgewähltes markieren

            logging.info(f"Selected item: {event.item.parent}")








class TasksTab(Static):
    """
    Tasks tab content
    """


    column_names: list[str]
    column_captions: dict[str, str]
    tasks: dict[str, list[Task]]


    def compose(self) -> ComposeResult:
        with Horizontal():
            for column_name in self.column_names:

                if column_name in self.tasks.keys():
                    list_items: list[ListItem] = []
                    for task in self.tasks[column_name]:
                        # item = ListItem(Label(Text(task.description)))



                        start_date_text = ' –––'
                        start_date_style = ''
                        if task.start_date is not None and task.start_date != '':
                            start_date_text = f'{task.start_date} ({task.days_to_start} d)'

                            if task.days_to_start > 0:
                                start_date_style = 'green'
                            elif task.days_to_start < 0 and task.days_to_end < 0:
                                start_date_style = 'red'
                            elif task.days_to_start <= 0:
                                start_date_style = 'yellow'




                        end_date_text = ' –––'
                        end_date_style = ''
                        if task.end_date is not None and task.end_date != '':
                            end_date_text = f'{task.end_date} ({task.days_to_end} d)'

                            if task.days_to_end > 0:
                                end_date_style = 'green'
                            elif task.days_to_end == 0:
                                end_date_style = 'yellow'
                            elif task.days_to_end < 0:
                                end_date_style = 'red'




                        item = ListItem(
                                Static(Text(task.description, style='bold')),
                                Static(),  # Empty line
                                # Static(Text('▶️ ' + start_date_text, style=start_date_style)),
                                Static(Text('↑' + start_date_text, style=start_date_style)),
                                # Static(Text('⏹️ ' + end_date_text, style=end_date_style)),
                                Static(Text('↓' + end_date_text, style=end_date_style)),


                        )

                        match task.priority:
                            case TaskPriority.HIGH:
                                item.add_class('task_prio_high')
                            case TaskPriority.MEDIUM:
                                item.add_class('task_prio_medium')
                            case _:
                                item.add_class('task_prio_low')

                        list_items.append(item)




                with Vertical():
                    yield(Label(Text(f'{self.column_captions[column_name]}:', style='bold underline'), classes='task_column_header'))

                    vertical_scroll = VerticalScroll()
                    with vertical_scroll:
                        yield CustomListView(vertical_scroll, *list_items)







    def composee(self) -> ComposeResult:
        """
        Creates the child widgets.
        """
        # horizontal = Horizontal()
        # horizontal.can_focus = False

        vscroll = VerticalScroll()


        items = [ListItem(Label(f'Item {i}')) for i in range(100)]

        # with horizontal:
        with Horizontal():

            with Vertical():
                yield Label('TEST')
                with vscroll:
                    yield CustomListView(vscroll, *items)

            with Vertical():
                yield Label('Heute:')
                # vscroll = VerticalScroll()
                # vscroll.can_focus = False
                # with vscroll:
                yield ListView(
                    ListItem(
                        Label(Text('Name of the Task', style='bold')),
                        Label(Text('S XXXX-XX-XX (XXX d)', style='green')),
                        Label(Text('E XXXX-XX-XX (XXX d)', style='green')),
                    ),
                    ListItem(Label(Text('Two\nxxx', style='bold red'))),
                    ListItem(Label('Three')),
                    ListItem(Label('One')),
                    ListItem(Label(Text('Two\nxxx', style='bold red'))),
                    ListItem(Label('Three')),
                    ListItem(Label('One')),
                    ListItem(Label(Text('Two\nxxx', style='bold red'))),
                    ListItem(Label('Three')),
                    ListItem(Label('One')),
                    ListItem(Label(Text('Two\nxxx', style='bold red'))),
                    ListItem(Label('Three')),
                    ListItem(Label('One')),
                    ListItem(Label(Text('Two\nxxx', style='bold red'))),
                    ListItem(Label('Three')),
                    ListItem(Label('One')),
                    ListItem(Label(Text('Two\nxxx', style='bold red'))),
                    ListItem(Label('Three')),
                    ListItem(Label('XXXXX')),
                    ListItem(Label('XXXXX')),
                    ListItem(Label('XXXXX')),
                    ListItem(Label('XXXXX')),
                    ListItem(Label('XXXXX')),
                    ListItem(Label('XXXXX')),
                    ListItem(Label('XXXXX')),
                    ListItem(Label('XXXXX')),
                    ListItem(Label('XXXXX')),
                    ListItem(Label('XXXXX')),
                )

            # vertical = Vertical()
            # vertical.can_focus = False
            # with vertical:
            with Vertical():
                yield Label('Morgen:')
                yield ListView(
                    ListItem(Label('One')),
                    ListItem(Label('Two')),
            )

            with Vertical():
                yield Label("XXX:")
                yield ListView(
                    ListItem(Label("One")),
                    ListItem(Label("Two")),
                )




    # async def add_list_view(self):
    def add_list_view(self):
        label = Label('TESTTEST')

        # container = self.query_one('#tasks-tab')
        container = self

        # await container.mount(label)
        container.mount(label)