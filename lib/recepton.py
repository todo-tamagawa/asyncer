import asyncio
from dataclasses import dataclass, field
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from lib.option import Option

from lib.util import move_done


@dataclass
class Reception:
    """受付モジュール
    zipファイル->Tucket
    """
    loop: asyncio.AbstractEventLoop = asyncio.new_event_loop()
    option: Option = Option()
    ticketQueue: asyncio.Queue[str] = asyncio.Queue()
    queue: asyncio.Queue[Path] = field(init=False, default=asyncio.Queue())
    observer: Observer = field(init=False, default=Observer())

    class EventHandler(FileSystemEventHandler):

        def __init__(self, reception: 'Reception'):
            super().__init__()
            self.reception = reception

        def on_created(self, event):
            super().on_created(event)
            path = Path(event.src_path)
            if not path.name.endswith('.zip'):
                return
            self.reception.loop.call_soon_threadsafe(
                lambda: self.reception.queue.put_nowait(path))

    class QueueIterator(object):
        def __init__(self, queue: asyncio.Queue[Path]) -> None:
            self.queue = queue

        def __aiter__(self):
            return self

        async def __anext__(self):
            return await self.queue.get()

    async def run(self):
        path = Path(self.option.ticket_dir)
        path.mkdir(exist_ok=True, parents=True)
        event_handler = Reception.EventHandler(reception=self)
        self.observer.schedule(event_handler, str(path.absolute()))
        self.observer.start()
        async for path in Reception.QueueIterator(self.queue):
            self.ticketQueue.put_nowait(path.stem)
            move_done(path)
