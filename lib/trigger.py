

import asyncio
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from lib.util import move_done


class Trigger:
    """トリガー検知モジュール
    """
    class EventHandler(FileSystemEventHandler):

        def __init__(self, trigger: 'Trigger'):
            super().__init__()
            self.trigger = trigger

        def on_created(self, event):
            super().on_created(event)
            path = Path(event.src_path)
            if path.name != self.trigger.path.name:
                return
            self.trigger.future.get_loop().call_soon_threadsafe(self.trigger.watch_stop)

    def __init__(self, path: Path) -> None:
        self.observer = Observer()
        self.future = asyncio.get_event_loop().create_future()
        self.path = path

    def watch_start(self):
        self.path.parent.mkdir(exist_ok=True, parents=True)
        if self.path.exists():
            self.path.unlink()
        event_handler = Trigger.EventHandler(trigger=self)
        self.observer.schedule(event_handler, str(
            self.path.parent.absolute()))
        self.observer.start()
        return self.future

    def watch_stop(self):
        self.observer.stop()
        self.observer.join()
        move_done(self.path)
        self.future.set_result(True)

    @classmethod
    def find(cls, path: Path):
        return cls(path=path).watch_start()
