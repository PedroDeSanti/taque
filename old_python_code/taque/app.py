from textual.app import App, ComposeResult, RenderResult
from textual.reactive import reactive
from textual.widgets import Header, Footer, Static, Button, Static
from textual.containers import HorizontalGroup, Container
from textual import on
from textual.reactive import reactive
from textual.widgets import Digits
from textual.binding import Binding

from time import monotonic, time

from enum import Enum, auto

from . import database

import asyncio


WORK_GOAL_SECONDS = 8 * 60 * 60  # 8 horas

class TimeDisplay(Digits):
    """A widget to display the time"""

    time_elapsed = reactive(0)
    current_state = None
    
    current_start_timestamp = None
    accumulated_time = 0

    class State(Enum):
        WORKING = auto()
        BREAK = auto()
        STOPPED = auto()


    async def _on_mount(self) -> None:

        self.update_timer = self.set_interval(
            1/60,
            self.update_time_elapsed,
            pause=True,
        )

        await self.sync_state()
        # self.run_worker(self.sync_state())

    def update_time_elapsed(self) -> None:
        now = time()
        section_duration = now - self.current_start_timestamp 
        self.time_elapsed = section_duration + self.accumulated_time

    def watch_time_elapsed(self) -> None:
        time = self.time_elapsed

        minutes, seconds = divmod(time, 60)
        hours, minutes = divmod(minutes, 60)

        time_string = f"{hours:02,.0f}:{minutes:02.0f}:{seconds:05.2f}"

        self.update(time_string)

    # def start(self) -> None:
    #     if self.current_state == self.State.WORKING:
    #         return
        
    #     self.current_start_timestamp = time()
    #     self.update_timer.resume()
    #     self.current_state = self.State.WORKING
    #     database.log_event("START_WORK")

    # def pause(self) -> None:
    #     if self.current_state == self.State.BREAK:
    #         return
        
    #     # self.time_elapsed = monotonic() - self.current_start_timestamp
    #     self.accumulated_time = self.time_elapsed
    #     self.update_timer.pause()
    #     self.current_state = self.State.BREAK
    #     database.log_event("START_BREAK")

    # def stop(self) -> None:
    #     if self.current_state == self.State.STOPPED:
    #         return
        
    #     self.accumulated_time = 0
    #     self.time_elapsed = 0
    #     self.update_timer.pause()
    #     self.current_state = self.State.STOPPED
    #     database.log_event("STOP")

    async def sync_state(self) -> None:
        last_event = await database.get_current_state()
        
        if last_event:
            event_type = last_event["event_type"]
            
            if event_type == "START_WORK":
                self.accumulated_time = await database.get_today_total_seconds()
                self.current_start_timestamp = last_event["timestamp"]
                self.update_time_elapsed()
                self.update_timer.resume()
                
            elif event_type == "START_BREAK":
                self.accumulated_time = await database.get_today_total_seconds()
                self.current_start_timestamp = None
                self.time_elapsed = self.accumulated_time
                self.update_timer.pause()
                
            elif event_type == "STOP":
                self.accumulated_time = 0
                self.current_start_timestamp = None
                self.time_elapsed = 0
                self.update_timer.pause()
        else:
            self.accumulated_time = 0
            self.current_start_timestamp = None
            self.time_elapsed = 0
            self.update_timer.pause()
            

class Timer(Static):
    """A simple timer widget with start, stop, and reset buttons"""

    def __init__(self) -> None:
        super().__init__()
        self.border_title = "Taque"

    @on(Button.Pressed, "#work-button")
    async def start_work(self) -> None:
        last_event = await database.get_current_state()
        if last_event and last_event["event_type"] == "START_WORK":
            return  # Already working; avoid duplicate log
        await database.log_event("START_WORK")
        await self.query_one(TimeDisplay).sync_state()

    @on(Button.Pressed, "#break-button")
    async def start_break(self) -> None:
        last_event = await database.get_current_state()
        if last_event and last_event["event_type"] == "START_BREAK":
            return  # Already on break; avoid duplicate log
        await database.log_event("START_BREAK")
        await self.query_one(TimeDisplay).sync_state()

    @on(Button.Pressed, "#stop-button")
    async def stop_timer(self) -> None:
        last_event = await database.get_current_state()
        if last_event and last_event["event_type"] == "STOP":
            return  # Already stopped; avoid duplicate log
        await database.log_event("STOP")
        await self.query_one(TimeDisplay).sync_state()

    # @on(Button.Pressed, "#work-button")
    # async def start_work(self) -> None:
    #     await database.log_event("START_WORK")
    #     self.query_one(TimeDisplay).start()

    # @on(Button.Pressed, "#break-button")
    # async def start_break(self) -> None:
    #     await database.log_event("START_BREAK")
    #     self.query_one(TimeDisplay).pause()

    # @on(Button.Pressed, "#stop-button")
    # async def stop_timer(self) -> None:
    #     await database.log_event("STOP")
    #     self.query_one(TimeDisplay).stop()

    def compose(self):
        yield TimeDisplay("00:00:00")

        with Container():
            yield Button("< Work >", id="work-button")
            yield Button("< Break >", id="break-button")
            yield Button("< Stop >", id="stop-button")
        
class TaqueApp(App):
    BINDINGS = [
        ("d", "toggle_dark", "Toggle dark mode"),
        ("q", "quit", "Quit"),
        ("w", "start_work", "Start work timer"),
        ("b", "start_break", "Start break timer"),
        ("s", "stop_timer", "Stop timer"),
    ]

    CSS_PATH = "app.tcss"

    def on_mount(self) -> None:
        database.init_db()

    def compose(self) -> ComposeResult:
        # yield Header()
        # yield Footer()
        yield Timer()

    def action_start_work(self) -> None:
        asyncio.create_task(self.query_one(Timer).start_work())

    def action_start_break(self) -> None:
        asyncio.create_task(self.query_one(Timer).start_break())

    def action_stop_timer(self) -> None:
        asyncio.create_task(self.query_one(Timer).stop_timer())

