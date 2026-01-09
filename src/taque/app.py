from textual.app import App, ComposeResult, RenderResult
from textual.reactive import reactive
from textual.widgets import Header, Footer, Static, Button, Static
from textual.containers import HorizontalGroup


class TimeDisplay(Static):
    """A widget to display the time"""

    pass

class Timer(Static):
    """A simple timer widget with start, stop, and reset buttons"""

    def compose(self):
        yield TimeDisplay("00:00:00")

        with HorizontalGroup():
            yield Button("Work")
            yield Button("Break")
            yield Button("Stop")
        
class TaqueApp(App):
    BINDINGS = [
        ("d", "toggle_dark", "Toggle dark mode"),
        ("q", "quit", "Quit"),
    ]

    CSS_PATH = "app.tcss"
    
    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        yield Timer()

    def action_toggle_dark_mode(self) -> None:
        pass
