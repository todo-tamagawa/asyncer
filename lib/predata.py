

import asyncio
from dataclasses import dataclass
from pathlib import Path
from lib.option import Option

from lib.trigger import Trigger


@dataclass
class PreData:
    """事前データモジュール
    """
    loop: asyncio.AbstractEventLoop = asyncio.new_event_loop()
    option: Option = Option()
    deliverable: asyncio.Event = asyncio.Event()

    async def run(self):
        while True:
            self.deliverable.set()

            path = Path(self.option.master_dir).joinpath(
                self.option.master_start_trg)
            await Trigger.find(path=path)

            self.deliverable.clear()

            path = Path(self.option.master_dir).joinpath(
                self.option.master_end_trg)
            await Trigger.find(path=path)

            path = Path(self.option.common_feature_dir).joinpath(
                self.option.common_feature_trg)
            self.loop.call_later(10, path.touch)
            await Trigger.find(path=path)
