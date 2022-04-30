

import asyncio
from dataclasses import dataclass, field
from lib.mock import Mock
from lib.option import Option
from lib.predata import PreData
from lib.recepton import Reception
from lib.deliverer import Deliverer


@dataclass
class Controller:
    """制御モジュール
    """
    loop: asyncio.AbstractEventLoop = asyncio.new_event_loop()
    option: Option = Option()
    deliverable: asyncio.Event = field(init=False, default=asyncio.Event())
    ticketQueue: asyncio.Queue[str] = field(
        init=False, default=asyncio.Queue())

    def __post_init__(self):
        self.preData = PreData(
            loop=self.loop, option=self.option, deliverable=self.deliverable)
        self.mock = Mock(loop=self.loop, option=self.option)
        self.reception = Reception(loop=self.loop, option=self.option,
                                   ticketQueue=self.ticketQueue)
        self.deliverer = Deliverer(loop=self.loop, option=self.option,
                                   deliverable=self.deliverable, ticketQueue=self.ticketQueue)

    def run(self):
        self.loop.create_task(self.preData.run())
        self.loop.create_task(self.mock.run())
        self.loop.create_task(self.reception.run())
        self.loop.create_task(self.deliverer.run())
        self.loop.run_forever()
