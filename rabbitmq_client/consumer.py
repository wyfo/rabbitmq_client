from logging import getLogger
from typing import (Awaitable, Callable)

import aio_pika

from rabbitmq_client.config import ClientConfig
from rabbitmq_client.logs import add_log_record_extensions
from rabbitmq_client.utils import TaskCounter, event_from_awaitable

logger = getLogger(__name__)

MsgHandler = Callable[[aio_pika.Message], Awaitable]


class Reject(Exception):
    pass


class Nack(Exception):
    pass


async def consumer(msg: aio_pika.IncomingMessage, handler: MsgHandler):
    try:
        add_log_record_extensions(msg_id=msg.message_id,
                                  request_id=msg.correlation_id)
        await handler(msg)
        await msg.ack()
    except Reject:
        await msg.reject()
    except Nack:
        await msg.nack()
    except Exception:
        logger.exception("Unexpected error during message consumption")
        await msg.reject()


async def run(config: ClientConfig, handler: MsgHandler, until: Awaitable):
    connection: aio_pika.Connection = await aio_pika.connect(
        **config["connection"], client_properties={
            'connection_name': 'Read connection'
        })
    until_event = event_from_awaitable(until)
    task_counter = TaskCounter()
    async with connection:
        channel = await connection.channel()
        await channel.set_qos(**config["channel"])
        queue = await channel.declare_queue(**config["queue"])

        async def callback(msg: aio_pika.IncomingMessage):
            # In order to avoid run callback after `until`
            if until_event.is_set():
                return await msg.reject()
            # In order to wait until all tasks run are donned
            with task_counter:
                await consumer(msg, handler)

        tag = await queue.consume(callback)
        await until_event.wait()
        await queue.cancel(tag)
        await task_counter.wait_no_more_tasks()
