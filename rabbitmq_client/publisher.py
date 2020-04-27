from logging import getLogger
from typing import Awaitable, Optional, TypeVar

import aio_pika

from rabbitmq_client.config import ConnectionOptions

logger = getLogger(__name__)

_channel: Optional[aio_pika.Channel] = None

T = TypeVar("T")


async def run(conn_opts: ConnectionOptions, until: Awaitable[T]) -> T:
    global _channel
    connection: aio_pika.Connection = await aio_pika.connect(
        **conn_opts, client_properties={
            'connection_name': 'Write connection'
        })
    async with connection:
        _channel = await connection.channel()
        return await until


async def publish(msg: aio_pika.Message, queue: str):
    if _channel is None:
        raise RuntimeError("Publisher is not running")
    await _channel.default_exchange.publish(msg, queue)
