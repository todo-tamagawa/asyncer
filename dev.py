

import asyncio
from pathlib import Path
import shutil
import signal
from lib.controller import Controller


if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    loop.add_signal_handler(signal.SIGINT, lambda: loop.stop())
    if Path('var').exists():
        shutil.rmtree('var')
    Controller(loop=loop).run()
