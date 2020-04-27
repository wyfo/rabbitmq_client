from typing import Dict, Optional, TypedDict

from aio_pika.types import TimeoutType


class ConnectionOptions(TypedDict):
    host: str
    port: int

    login: str
    password: str
    virtualhost: str

    ssl: bool
    ssl_options: Optional[Dict]
    timeout: Optional[TimeoutType]

    # reconnect_interval: int = 5
    # fail_fast: int = 1


class ChannelQos(TypedDict):
    prefetch_count: int
    prefetch_size: int


class QueueOptions(TypedDict):
    name: str
    durable: Optional[str]
    exclusive: bool
    passive: bool
    auto_delete: bool


class ClientConfig(TypedDict):
    connection: ConnectionOptions
    channel: ChannelQos
    queue: QueueOptions
