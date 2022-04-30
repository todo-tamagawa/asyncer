

import asyncio
from pathlib import Path
import shutil
import time


async def touch(path: Path, delay: int = 3):
    await asyncio.sleep(delay)
    path.touch()


def move_done(path: Path):
    now = time.strftime('%Y-%m-%d-%H-%M-%S')
    done_dir = path.parent.joinpath('done')
    done_dir.mkdir(exist_ok=True)
    shutil.move(str(path.absolute()),
                done_dir.joinpath(f'{path.name}.{now}'))
