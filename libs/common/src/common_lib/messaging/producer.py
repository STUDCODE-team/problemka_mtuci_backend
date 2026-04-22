import json
import logging
from uuid import UUID

import aio_pika
from aio_pika.abc import AbstractRobustConnection, AbstractChannel

logger = logging.getLogger(__name__)

NOTIFICATIONS_QUEUE = "notifications"

_connection: AbstractRobustConnection | None = None
_channel: AbstractChannel | None = None


async def init_producer(url: str) -> None:
    global _connection, _channel
    _connection = await aio_pika.connect_robust(url)
    _channel = await _connection.channel()
    await _channel.declare_queue(NOTIFICATIONS_QUEUE, durable=True)
    logger.info("RabbitMQ producer connected, queue '%s' declared", NOTIFICATIONS_QUEUE)


async def close_producer() -> None:
    global _connection, _channel
    _channel = None
    if _connection and not _connection.is_closed:
        await _connection.close()
    _connection = None
    logger.info("RabbitMQ producer connection closed")


async def publish_otp_email(to_email: str, otp: str) -> None:
    await _publish({"type": "otp_email", "to_email": to_email, "otp": otp})


async def publish_push(user_id: UUID, title: str, body: str, data: dict | None = None) -> None:
    await _publish({"type": "push", "user_id": str(user_id), "title": title, "body": body, "data": data})


async def _publish(payload: dict) -> None:
    if _channel is None or _channel.is_closed:
        logger.error("RabbitMQ producer unavailable, dropping message type='%s'", payload.get("type"))
        return
    await _channel.default_exchange.publish(
        aio_pika.Message(
            body=json.dumps(payload).encode(),
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
        ),
        routing_key=NOTIFICATIONS_QUEUE,
    )
