

import asyncio
from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

from lib.option import Option


@dataclass
class Mock:
    """モックモジュール
    zipファイル/マスタトリガを定期作成する
    """
    loop: asyncio.AbstractEventLoop = asyncio.new_event_loop()
    option: Option = Option()

    async def run(self):
        self.loop.create_task(self.mock_tickets())
        self.loop.create_task(self.mock_predata())

    async def mock_tickets(self):
        while True:
            await asyncio.sleep(8)
            uid = str(uuid4())[:5]
            Path(self.option.ticket_dir).joinpath(f'{uid}.zip').touch()

    async def mock_predata(self):
        while True:
            await asyncio.sleep(40)

            Path(self.option.master_dir).joinpath(
                self.option.master_start_trg).touch()

            await asyncio.sleep(10)

            Path(self.option.master_dir).joinpath(
                self.option.master_end_trg).touch()
