from textual.app import App, ComposeResult
from textual.widgets import ListView, ListItem, Label
from textual.events import Key

class MyListViewApp(App):
    # CSS = """
    # ListView {
    #     width: 100%;
    #     height: 100%;
    # }
    # """

    def compose(self) -> ComposeResult:
        items = [ListItem(Label(f"Item {i}")) for i in range(100)]
        self.list_view = ListView(*items)
        yield self.list_view

# async def on_key(self, event: Key) -> None:
#     index = self.list_view.index or 0

#     if event.key == "up":
#         index = max(0, index - 1)
#     elif event.key == "down":
#         index = min(len(self.list_view.children) - 1, index + 1)
#     else:
#         return

#     self.list_view.index = index
#     item = self.list_view.children[index]
#     await self.list_view.scroll_to_node(item)

if __name__ == "__main__":
    MyListViewApp().run()