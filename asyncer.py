import asyncio
import dataclasses
from enum import IntEnum, auto
import shutil
import signal
import time
from pathlib import Path
from typing import Optional

from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer


class JobTypeEnum(IntEnum):
    ZIP_CREATED = auto()


@dataclasses.dataclass
class Job:
    job_type: JobTypeEnum


@dataclasses.dataclass
class ZipCreatedJob(Job):
    job_type: JobTypeEnum = dataclasses.field(
        default=JobTypeEnum.ZIP_CREATED, init=False)
    zip_path: Path


class QueueIterator(object):
    def __init__(self, queue: asyncio.Queue[Job]):
        self.queue = queue

    def __aiter__(self):
        return self

    async def __anext__(self):
        return await self.queue.get()


class BaseWatchHandler(FileSystemEventHandler):
    def __init__(self, queue: asyncio.Queue[Job], loop: asyncio.AbstractEventLoop, *args, **kwargs):
        self._loop = loop
        self._queue = queue
        super(*args, **kwargs)

    def emitJob(self, job: Job):
        self._loop.call_soon_threadsafe(self._queue.put_nowait, job)


class BaseWatcher:
    loop: asyncio.AbstractEventLoop
    queue: asyncio.Queue[Job]
    path: Path
    observer: Optional[Observer] = None

    def __init__(self, path: Path, queue: asyncio.Queue[Job], loop: asyncio.AbstractEventLoop) -> None:
        self.path = path
        self.loop = loop
        self.queue = queue


class FeatureDataWatcher:
    pass


class TicketZipWatcher:
    pass


class Application:
    loop: asyncio.AbstractEventLoop
    queue: asyncio.Queue[Job]
    path: Path
    observer: Optional[Observer] = None

    def __init__(self, path: Path) -> None:
        self.path = path
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        self.loop = loop
        self.queue = asyncio.Queue()

    def run(self):
        infinite_task = self.loop.create_task(self.periodic(2))
        consume_task = self.loop.create_task(self.consume())

        def stop():
            self.watch(False)
            infinite_task.cancel()
            consume_task.cancel()

        # mock
        self.loop.call_later(5, lambda: self.watch())
        self.loop.call_later(10, lambda: self.watch(False))
        self.loop.call_later(15, lambda: self.watch())
        self.loop.call_later(20, lambda: self.watch(False))

        signal.signal(signal.SIGINT, lambda signum, frame: stop())

        try:
            self.loop.run_until_complete(infinite_task)
        except asyncio.CancelledError:
            print('Cancelled')
            pass

    async def periodic(self, interval: int):
        while True:
            now = time.strftime('%m-%d-%H-%M-%S')
            print(f'touch: {now}')
            now_path = self.path.joinpath(now)
            now_path.mkdir(exist_ok=True)
            now_path.joinpath('hoge.csv').touch()
            now_path.joinpath('fuga.csv').touch()

            shutil.make_archive(str(now_path), format='zip',
                                root_dir=str(now_path))
            shutil.rmtree(now_path)
            await asyncio.sleep(interval)

    async def consume(self):
        async for job in QueueIterator(self.queue):
            if isinstance(job, ZipCreatedJob):
                print("operate zip create job!", job.zip_path.name)

    def watch(self, start=True):
        if start:
            if self.observer is not None:
                self.watch(False)
            handler = self.__WatchZipHandler(queue=self.queue, loop=self.loop)
            observer = Observer()
            observer.schedule(handler, str(self.path))
            observer.start()
            self.observer = observer
            return
        if observer := self.observer:
            observer.stop()
            observer.join()
            self.observer = None

    class __WatchZipHandler(BaseWatchHandler):

        def on_created(self, event: FileSystemEvent) -> None:
            src_path: str = event.src_path
            if src_path.endswith('.zip'):
                job = ZipCreatedJob(Path(src_path))
                self.emitJob(job=job)


if __name__ == '__main__':
    app = Application(Path('watch'))
    app.run()
