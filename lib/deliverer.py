from pathlib import Path
from typing import Dict
from uuid import uuid4
from lib.option import Option
import asyncio
from dataclasses import dataclass, field

from lib.trigger import Trigger


@dataclass
class Deliverer:
    """出力モジュール
    Ticket->出力
    """
    loop: asyncio.AbstractEventLoop = asyncio.new_event_loop()
    option: Option = Option()
    deliverable: asyncio.Event = asyncio.Event()
    ticketQueue: asyncio.Queue[str] = asyncio.Queue()
    tasks: Dict[str, asyncio.Task] = field(init=False, default_factory=dict)

    class QueueIterator(object):
        def __init__(self, queue: asyncio.Queue[str]) -> None:
            self.queue = queue

        def __aiter__(self):
            return self

        async def __anext__(self):
            return await self.queue.get()

    def loadTickets(self):
        print('loadTickets')
        for _ in range(1, 10):
            uid = str(uuid4())[:5]
            self.ticketQueue.put_nowait(uid)

    async def run(self):
        print('run')
        self.loadTickets()
        async for uid in Deliverer.QueueIterator(self.ticketQueue):
            if len(self.tasks.keys()) == len(self.option.workers):
                await asyncio.wait(self.tasks.values(), return_when=asyncio.FIRST_COMPLETED)
            if not self.deliverable.is_set():
                print('guard', uid)
                await self.deliverable.wait()
                print('resume', uid)
            worker = next(
                filter(lambda w: w not in self.tasks.keys(), self.option.workers))
            self.tasks[worker] = self.loop.create_task(
                self.deliver(uid=uid, worker=worker))

    async def deliver(self, uid: str, worker: str):
        print('deliver.exec', worker, uid)
        path = Path(self.option.market_feature_dir).joinpath(
            uid).joinpath(self.option.market_feature_trg)
        self.loop.call_later(3, path.touch)
        await Trigger.find(path=path)

        path = Path(self.option.aiml_dir).joinpath(
            uid).joinpath(self.option.aiml_trg)
        self.loop.call_later(3, path.touch)
        await Trigger.find(path=path)

        del self.tasks[worker]
