from textual.app import App, ComposeResult, RenderResult
from textual.reactive import reactive
from textual.widgets import Header, Footer, Static, Button, Static
from textual.containers import HorizontalGroup, Container
from textual import on
from textual.reactive import reactive

from time import monotonic


class TimeDisplay(Static):
    """A widget to display the time"""

    accumulated_time = 0
    start_time = monotonic()
    time_elapsed = reactive(0)

    def _on_mount(self) -> None:
        self.update_timer = self.set_interval(
            1/60,
            self.update_time_elapsed,
            pause=True,
        )

    def update_time_elapsed(self) -> None:
        self.time_elapsed = (monotonic() - self.start_time) + self.accumulated_time


    def watch_time_elapsed(self) -> None:
        time = self.time_elapsed

        minutes, seconds = divmod(time, 60)
        hours, minutes = divmod(minutes, 60)

        time_string = f"{hours:02,.0f}:{minutes:02.0f}:{seconds:05.2f}"

        self.update(time_string)

    def start(self) -> None:
        self.start_time = monotonic()
        self.update_timer.resume()

    def pause(self) -> None:
        # self.time_elapsed = monotonic() - self.start_time
        self.accumulated_time = self.time_elapsed
        self.update_timer.pause()

    def stop(self) -> None:
        self.accumulated_time = 0
        self.time_elapsed = 0
        self.update_timer.pause()

class Timer(Static):
    """A simple timer widget with start, stop, and reset buttons"""

    def __init__(self) -> None:
        super().__init__()
        self.border_title = "Taque"

    @on(Button.Pressed, "#work-button")
    def start_work(self) -> None:
        self.query_one(TimeDisplay).start()

    @on(Button.Pressed, "#break-button")
    def start_break(self) -> None:
        self.query_one(TimeDisplay).pause()

    @on(Button.Pressed, "#stop-button")
    def stop_timer(self) -> None:
        self.query_one(TimeDisplay).stop()

    def compose(self):
        yield TimeDisplay("00:00:00")

        with Container():
            yield Button("Work", id="work-button")
            yield Button("Break", id="break-button")
            yield Button("Stop", id="stop-button")
        
class TaqueApp(App):
    BINDINGS = [
        ("d", "toggle_dark", "Toggle dark mode"),
        ("q", "quit", "Quit"),
        ("w", "start_work", "Start work timer"),
        ("b", "start_break", "Start break timer"),
        ("s", "stop_timer", "Stop timer"),
    ]

    CSS_PATH = "app.tcss"
    
    def compose(self) -> ComposeResult:
        # yield Header()
        # yield Footer()
        yield Timer()

    def action_start_work(self) -> None:
        self.query_one(Timer).start_work()

    def action_start_break(self) -> None:
        self.query_one(Timer).start_break()

    def action_stop_timer(self) -> None:
        self.query_one(Timer).stop_timer()

# from textual.app import App
# from textual.containers import Container
# from textual.widgets import Static

# class TaqueBox(Static):
#     """Um widget customizado com borda e título."""
    
#     def __init__(self):
#         super().__init__()
#         self.border_title = "Taque"

# class TaqueApp(App):
#     CSS = """
#     TaqueBox {
#         border: round cyan;
#         padding: 2;
#         margin: 2;
#         height: auto;
#     }
#     """

#     def compose(self):
#         yield TaqueBox()