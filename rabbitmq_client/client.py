import asyncio
from logging import getLogger
from signal import SIGINT, SIGTERM

from rabbitmq_client import consumer, publisher
from rabbitmq_client.config import ClientConfig
from rabbitmq_client.consumer import MsgHandler

logger = getLogger(__name__)


async def run(config: ClientConfig, handler: MsgHandler):
    # Signal handling
    loop = asyncio.get_running_loop()
    term_event = asyncio.Event()

    def terminate():
        logger.info("terminate")
        term_event.set()

    loop.add_signal_handler(SIGTERM, terminate)
    loop.add_signal_handler(SIGINT, terminate)

    consume = consumer.run(config, handler, term_event.wait())
    # Because consumer can use publisher, publisher must wait consumer
    publish = publisher.run(config["connection"], consume)
    await publish
