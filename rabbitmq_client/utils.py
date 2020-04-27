import asyncio
from typing import Awaitable


def event_from_awaitable(awaitable: Awaitable) -> asyncio.Event:
    async def set_event():
        await awaitable
        event.set()

    event = asyncio.Event()
    asyncio.create_task(set_event())
    return event


class TaskCounter:
    def __init__(self):
        self.count = 0
        self.waiting = False
        self.no_more_tasks = asyncio.Event()

    def __enter__(self):
        self.count += 1

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.count -= 1
        if self.waiting and self.count == 0:
            self.no_more_tasks.set()

    async def wait_no_more_tasks(self):
        self.waiting = True
        await self.no_more_tasks.wait()
